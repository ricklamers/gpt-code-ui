import json
import os
import queue
import shutil
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Dict

from jupyter_client import BlockingKernelClient

import gpt_code_ui.kernel_program.config as config
from gpt_code_ui.kernel_program.stoppable_thread import StoppableThread
from gpt_code_ui.kernel_program.utils import create_derived_venv, escape_ansi


class FlushingThread(StoppableThread):
    def __init__(self, flush_kernel_msgs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flush = flush_kernel_msgs

    def run(self):
        while not self.stopped(timeout=1.0):
            self._flush()


class Kernel:
    def __init__(self, session_id: str):
        self._logger = config.get_logger(f"Kernel {session_id}")
        self._session_id = session_id
        self._workdir = config.KERNEL_BASE_DIR / f"kernel.{self._session_id}"
        self._result_queue: queue.Queue[Dict[str, str]] = queue.Queue()
        self._status = "stopped"
        self._kernel_client = None
        self._kernel_process = None
        self._flusher_thread = None
        self._startup_thread = None
        self._start()

    def _start(self):
        self._startup_thread = Thread(
            name=f"Kernel {self._session_id} startup procedure.",
            target=self._start_impl,
        )
        self._startup_thread.start()

    def _ensure_started(self):
        self._startup_thread.join()

    def _start_impl(self):
        if self.status != "stopped":
            self._logger.error(f"Trying to start a kernel that is not stopped but has status {self.status} instead.")

        self._logger.info(f"Start of kernel with workdir {self._workdir} has been requested.")

        self._status = "starting"
        self._put_message("Starting Kernel...", message_type="message_status")

        # Cleanup potential leftovers
        shutil.rmtree(self._workdir, ignore_errors=True)
        os.makedirs(self._workdir)

        kernel_env: Dict[
            str, str
        ] = {}  # instead of os.environ.copy() to prevent leaking information from the runtime into the kernel
        kernel_connection_file = self._workdir / "kernel_connection_file.json"

        if config.NO_INTERNET_AVAILABLE:
            # cannot install packages, so no need for a dedicated venv
            kernel_python_executable = sys.executable
            self._logger.info(
                f"Skipped creating kernel venv as there is no internet connection. Using python binary {kernel_python_executable}."
            )
        else:
            kernel_venv_dir = self._workdir / "venv"
            kernel_venv_bindir, kernel_python_executable = create_derived_venv(config.BASE_VENV, kernel_venv_dir)
            kernel_env["PATH"] = str(kernel_venv_bindir) + os.pathsep + kernel_env.get("PATH", "")
            self._logger.info(
                f"Created kernel venv at {kernel_venv_dir} with python binary {kernel_python_executable}."
            )

        # ensure that the function library is available # TODO: this also allows acessing gpt_code_ui and frontend :-()
        kernel_env["PYTHONPATH"] = (
            str(Path(__file__).parent.parent.resolve()) + os.pathsep + kernel_env.get("PYTHONPATH", "")
        )

        # start the kernel using the virtual env python executable
        kernel_code = f"""from ipykernel.kernelapp import IPKernelApp
IPKernelApp.launch_instance(
    argv=[
        "--IPKernelApp.connection_file",
        "{kernel_connection_file}",
        "--matplotlib=inline",
        f"--ipython-dir={self._workdir}",
        "--quiet",
    ]
)"""

        self._kernel_process = subprocess.Popen(
            [kernel_python_executable, "-c", kernel_code],
            cwd=self._workdir,
            env=kernel_env,
        )

        self._logger.info(f"Kernel process has started. PID is {self._kernel_process.pid}.")

        # Wait for kernel connection file to be written
        while True:
            try:
                with open(kernel_connection_file, "r") as fp:
                    json.load(fp)
            except (FileNotFoundError, json.JSONDecodeError):
                # Either file was not yet there or incomplete (then JSON parsing failed)
                time.sleep(0.1)
            else:
                break

        # Client
        self._kernel_client = BlockingKernelClient(connection_file=str(kernel_connection_file))
        self._kernel_client.load_connection_file()
        self._kernel_client.start_channels()
        self._kernel_client.wait_for_ready()
        self._kernel_client.execute(
            """from function_library import AVAILABLE_FUNCTIONS
for function_name, function in AVAILABLE_FUNCTIONS.items():
    locals()[function_name] = function
"""
        )
        self._logger.info(f"Kernel client has started. Connection details found in {kernel_connection_file}.")

        self._flusher_thread = FlushingThread(
            name=f"Kernel Message Flusher {self._session_id}", flush_kernel_msgs=self.flush_kernel_msgs
        )
        self._flusher_thread.start()

        self._logger.info("Message Flusher thread started.")

        self._status = "idle"
        self._put_message("Kernel is ready.", message_type="message_status")

    @property
    def status(self):
        return self._status

    def set_status(self, status: str):
        self._status = status

    def __del__(self):
        if self._status != "stopped":
            self.terminate()

    def restart(self):
        self._logger.info("Restarting kernel.")
        self.terminate()
        self._start()

    def terminate(self):
        self._ensure_started()
        self._logger.info("Termination of kernel has been requested.")
        self._status = "stopping"
        self._logger.info("Stopping message flusher thread has been requested.")
        self._flusher_thread.stop(wait=True)
        self._logger.info(f"Terminating kernel process {self._kernel_process.pid}")
        self._kernel_process.kill()
        self._logger.info(f"Removing kernel work directory {self._workdir}")
        shutil.rmtree(self._workdir, ignore_errors=True)
        self._status = "stopped"
        self._logger.info("Kernel terminated.")

    def _put_message(self, value, message_type):
        self._result_queue.put({"value": value, "type": message_type})

    def flush_kernel_msgs(self, tries=1, timeout=0.2):
        self._ensure_started()

        try:
            hit_empty = 0

            while True:
                try:
                    msg = self._kernel_client.get_iopub_msg(timeout=timeout)
                    msg_type = msg["msg_type"]
                    msg_content = msg["content"]

                    self._logger.debug(f'Received "{msg_type}": {msg_content}')

                    if msg_type == "status":
                        self._status = msg_content["execution_state"]
                        # self._put_message(msg_content["execution_state"], message_type="message_status")

                    elif msg_type == "execute_input":
                        pass  # do not want to mirror the input back

                    elif msg_type in ("execute_result", "display_data"):
                        content_data = msg_content["data"]

                        if "image/png" in content_data:
                            self._put_message(content_data["image/png"], message_type="image/png")
                        elif "image/jpeg" in content_data:
                            self._put_message(content_data["image/jpeg"], message_type="image/jpeg")
                        elif "image/svg+xml" in content_data:
                            self._put_message(content_data["image/svg+xml"], message_type="image/svg+xml")
                        elif "text/plain" in content_data:
                            self._put_message(
                                content_data["text/plain"],
                                "message_raw" if msg_type == "execute_result" else "message",
                            )

                    elif msg_type == "stream":
                        self._put_message(msg_content["text"], message_type="message")

                    elif msg_type == "error":
                        self._put_message(
                            escape_ansi("\n".join(msg_content["traceback"])),
                            message_type="message_error",
                        )

                    else:
                        self._logger.debug(f"Unexpected message type {msg_type}")

                except queue.Empty:
                    hit_empty += 1
                    if hit_empty == tries:
                        # Empty queue for one second, give back control
                        break
                except (ValueError, IndexError):
                    # get_iopub_msg suffers from message fetch errors
                    break
                except Exception as e:
                    self._logger.exception(e)
                    break
        except Exception as e:
            self._logger.exception(e)

    def execute(self, command):
        self._ensure_started()

        self._logger.debug("Executing command: %s" % command)

        code = command.get("command", "")
        options = command.get("options", [])

        if "svg" in options:
            code = f"""%matplotlib inline
import matplotlib_inline
matplotlib_inline.backend_inline.set_matplotlib_formats('svg')
del matplotlib_inline
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype'] = 'none'
del plt
import warnings
warnings.filterwarnings("ignore", message="Glyph.*missing from current font.")
del warnings
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
del logging
{code}"""
        else:
            code = f"""%matplotlib inline
import matplotlib_inline
matplotlib_inline.backend_inline.set_matplotlib_formats('png')
del matplotlib_inline
{code}"""

        self._kernel_client.execute(code, allow_stdin=False)
        # Try direct flush with default wait (0.2)
        self.flush_kernel_msgs()

    def get_results(self):
        return [self._result_queue.get() for _ in range(self._result_queue.qsize())]

    @property
    def workdir(self) -> str:
        return str(self._workdir)

    @property
    def session_id(self) -> str:
        return self._session_id
