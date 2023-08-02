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
import venv

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
                msg_type = msg["msg_type"]
                msg_content = msg["content"]

                logger.debug(f'Received "{msg_type}" output: {msg_content}')

                if msg_type in ("execute_result", "display_data"):
                    content_data = msg_content["data"]

                    if "image/png" in content_data:
                        send_message(content_data["image/png"], message_type="image/png")
                    elif "image/jpeg" in content_data:
                        send_message(content_data["image/jpeg"], message_type="image/jpeg")
                    elif "text/plain" in content_data:
                        send_message(content_data["text/plain"], "message_raw" if msg_type == "execute_result" else "message")

                elif msg_type == "stream":
                    send_message(msg_content["text"])

                elif msg_type == "error":
                    send_message(utils.escape_ansi("\n".join(msg["content"]["traceback"])), "message_error")

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


def create_venv(venv_dir: pathlib.Path, install_default_packages: bool) -> pathlib.Path:
    venv_bindir = venv_dir / 'bin'
    venv_python_executable = venv_bindir / os.path.basename(sys.executable)

    if not os.path.isdir(venv_dir):
        # create virtual env inside venv_dir directory
        venv.create(venv_dir, system_site_packages=True, with_pip=True, upgrade_deps=True)

        if install_default_packages:
            # install wheel because some packages do not like being installed without
            subprocess.run([venv_python_executable, '-m', 'pip', 'install', 'wheel>=0.41,<1.0'])
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
            subprocess.run([venv_python_executable, '-m', 'pip', 'install'] + default_packages)

    # get base env library path as we need this to refer to this form a derived venv
    site_packages = subprocess.check_output([venv_python_executable, '-c', 'import sysconfig; print(sysconfig.get_paths()["purelib"])'])
    site_packages = site_packages.decode('utf-8').split('\n')[0]

    return pathlib.Path(site_packages)


def create_derived_venv(base_venv: pathlib.Path, venv_dir: pathlib.Path):
    site_packages_base = create_venv(base_venv, install_default_packages=True)
    site_packages_derived = create_venv(venv_dir, install_default_packages=False)

    # create a link from derived venv into the base venv, see https://stackoverflow.com/a/75545634
    with open(site_packages_derived / '_base_packages.pth', 'w') as pth:
        pth.write(f'{site_packages_base}\n')

    venv_bindir = venv_dir / 'bin'
    venv_python_executable = venv_bindir / os.path.basename(sys.executable)

    return venv_bindir, venv_python_executable


def start_kernel(id: str):
    cwd = pathlib.Path(os.getcwd())
    kernel_dir = cwd / f'kernel.{id}'
    base_dir = cwd / 'kernel.base'

    # Cleanup potential leftovers
    shutil.rmtree(kernel_dir, ignore_errors=True)
    os.makedirs(kernel_dir)

    kernel_env = os.environ.copy()
    kernel_connection_file = kernel_dir / "kernel_connection_file.json"
    launch_kernel_script_path = pathlib.Path(__file__).parent.resolve() / "launch_kernel.py"

    kernel_venv_dir = kernel_dir / 'venv'
    kernel_venv_bindir, kernel_python_executable = create_derived_venv(base_dir, kernel_venv_dir)
    kernel_env['PATH'] = str(kernel_venv_bindir) + os.pathsep + kernel_env['PATH']

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
