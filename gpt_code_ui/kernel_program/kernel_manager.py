import sys
import subprocess
import os
import shutil
import atexit
import queue
import json
import signal
import pathlib
import threading
import time
import traceback

from time import sleep
from jupyter_client import BlockingKernelClient

from dotenv import load_dotenv
load_dotenv('.env')

import gpt_code_ui.kernel_program.utils as utils
import gpt_code_ui.kernel_program.config as config

# Set up globals
messaging = None
logger = config.get_logger()


class FlushingThread(threading.Thread):
    def __init__(self, kc, kill_sema):
        threading.Thread.__init__(self)
        self.kill_sema = kill_sema
        self.kc = kc

    def run(self):
        logger.info("Running message flusher...")
        while True:

            if self.kill_sema.acquire(blocking=False):
                logger.info("Sema was released to kill thread")
                sys.exit()

            flush_kernel_msgs(self.kc)
            time.sleep(1)


def cleanup_spawned_processes():
    print("Cleaning up kernels...")
    for filename in os.listdir(config.KERNEL_PID_DIR):
        fp = os.path.join(config.KERNEL_PID_DIR, filename)
        if os.path.isfile(fp):
            try:
                pid = int(filename.split(".pid")[0])
                logger.debug("Killing process with pid %s" % pid)
                os.remove(fp)
                try:
                    if os.name == "nt":
                        os.kill(pid, signal.CTRL_BREAK_EVENT)
                    else:
                        os.kill(pid, signal.SIGKILL)

                    # After successful kill, cleanup pid file
                    os.remove(fp)

                except Exception:
                    # Windows process killing is flaky
                    pass
            except Exception as e:
                logger.debug(e)


def start_snakemq(kc):
    global messaging

    messaging, link = utils.init_snakemq(config.IDENT_KERNEL_MANAGER, "connect")

    def on_recv(conn, ident, message):
        if ident == config.IDENT_MAIN:
            message = json.loads(message.data.decode("utf-8"))

            if message["type"] == "execute":
                logger.debug("Executing command: %s" % message["value"])
                kc.execute(message["value"])
                # Try direct flush with default wait (0.2)
                flush_kernel_msgs(kc)

    messaging.on_message_recv.add(on_recv)

    start_flusher(kc)

    # Send alive
    utils.send_json(messaging, {"type": "status", "value": "ready"}, config.IDENT_MAIN)
    logger.info("Python kernel ready to receive messages!")

    logger.info("Starting snakemq loop")

    try:
        link.loop()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error("Error in snakemq loop: %s" % e)
        sys.exit(1)


def start_flusher(kc):
    # Start FlushMessenger
    kill_sema = threading.Semaphore()
    kill_sema.acquire()
    t = FlushingThread(kc, kill_sema)
    t.start()

    def end_thread():
        kill_sema.release()

    atexit.register(end_thread)


def send_message(message, message_type="message"):
    utils.send_json(
        messaging, {"type": message_type, "value": message}, config.IDENT_MAIN
    )


def flush_kernel_msgs(kc, tries=1, timeout=0.2):
    try:
        hit_empty = 0

        while True:
            try:
                msg = kc.get_iopub_msg(timeout=timeout)
                if msg["msg_type"] == "execute_result":
                    if "text/plain" in msg["content"]["data"]:
                        send_message(
                            msg["content"]["data"]["text/plain"], "message_raw"
                        )
                if msg["msg_type"] == "display_data":
                    if "image/png" in msg["content"]["data"]:
                        # Convert to Slack upload
                        send_message(
                            msg["content"]["data"]["image/png"],
                            message_type="image/png",
                        )
                    elif "text/plain" in msg["content"]["data"]:
                        send_message(msg["content"]["data"]["text/plain"])

                elif msg["msg_type"] == "stream":
                    logger.debug("Received stream output %s" % msg["content"]["text"])
                    send_message(msg["content"]["text"])
                elif msg["msg_type"] == "error":
                    send_message(
                        utils.escape_ansi("\n".join(msg["content"]["traceback"])),
                        "message_error",
                    )
            except queue.Empty:
                hit_empty += 1
                if hit_empty == tries:
                    # Empty queue for one second, give back control
                    break
            except (ValueError, IndexError):
                # get_iopub_msg suffers from message fetch errors
                break
            except Exception as e:
                logger.debug(f"{e} [{type(e)}")
                logger.debug(traceback.format_exc())
                break
    except Exception as e:
        logger.debug(f"{e} [{type(e)}")


def start_kernel(id: str):
    cwd = pathlib.Path(os.getcwd())
    kernel_dir = cwd / f'kernel.{id}'
    kernel_venv = kernel_dir / 'venv'
    kernel_venv_bindir = kernel_venv / 'bin'
    kernel_python_executable = kernel_venv_bindir / os.path.basename(sys.executable)
    kernel_connection_file = kernel_dir / "kernel_connection_file.json"
    launch_kernel_script_path = pathlib.Path(__file__).parent.resolve() / "launch_kernel.py"
    kernel_env = os.environ.copy()
    kernel_env['PATH'] = str(kernel_venv_bindir) + os.pathsep + kernel_env['PATH']

    # Cleanup potential leftovers
    shutil.rmtree(kernel_dir, ignore_errors=True)

    os.makedirs(kernel_dir)

    # create virtual env inside kernel_venv directory
    subprocess.run([sys.executable, '-m', 'venv', kernel_venv, '--upgrade-deps', '--system-site-packages'])
    # install wheel because some packages do not like being installed without
    subprocess.run([kernel_python_executable, '-m', 'pip', 'install', 'wheel>=0.41,<1.0'])
    # install all default packages into the venv
    default_packages = [
        "ipykernel>=6,<7",
        "numpy>=1.24,<1.25",
        "dateparser>=1.1,<1.2",
        "pandas>=1.5,<1.6",
        "geopandas>=0.13,<0.14",
        "tabulate>=0.9.0<1.0",
        "PyPDF2>=3.0,<3.1",
        "pdfminer>=20191125,<20191200",
        "pdfplumber>=0.9,<0.10",
        "matplotlib>=3.7,<3.8",
        "openpyxl>=3.1.2,<4",
    ]
    subprocess.run([kernel_python_executable, '-m', 'pip', 'install'] + default_packages)

    # start the kernel using the virtual env python executable
    kernel_process = subprocess.Popen(
        [
            kernel_python_executable,
            launch_kernel_script_path,
            "--IPKernelApp.connection_file",
            kernel_connection_file,
            "--matplotlib=inline",
            "--quiet",
        ],
        cwd=kernel_dir,
        env=kernel_env,
    )

    utils.store_pid(kernel_process.pid, "kernel")

    # Wait for kernel connection file to be written
    while True:
        try:
            with open(kernel_connection_file, 'r') as fp:
                json.load(fp)
        except (FileNotFoundError, json.JSONDecodeError):
            # Either file was not yet there or incomplete (then JSON parsing failed)
            sleep(0.1)
            pass
        else:
            break

    # Client
    kc = BlockingKernelClient(connection_file=str(kernel_connection_file))
    kc.load_connection_file()
    kc.start_channels()
    kc.wait_for_ready()
    return kc, kernel_dir


if __name__ == "__main__":
    try:
        kernel_id = sys.argv[1]
    except IndexError as e:
        logger.exception('Missing kernel ID command line parameter', e)
    else:
        kc, kernel_dir = start_kernel(id=kernel_id)

        # make sure the dir with the virtualenv will be deleted after kernel termination
        atexit.register(lambda: shutil.rmtree(kernel_dir, ignore_errors=True))

        start_snakemq(kc)
