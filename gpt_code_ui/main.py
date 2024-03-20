# Run the webapp and kernel_program in separate processes

# webapp is a Flask app (in webapp/main.py relative to this main.py)
# kernel_program is a Python script (in kernel_program/main.py relative to this main.py)
import multiprocessing
import multiprocessing.connection
import sys
import time
import webbrowser

import gpt_code_ui.kernel_program.config as config
from gpt_code_ui.kernel_program.main import main as kernel_program_main
from gpt_code_ui.webapp.main import APP_PORT, app

APP_URL = "http://localhost:%s" % APP_PORT


def run_webapp(logger):
    try:
        app.run(host="0.0.0.0", port=APP_PORT, use_reloader=False)
    except Exception:
        logger.exception("Error running the webapp")
        sys.exit(1)


def run_kernel_program(logger):
    try:
        kernel_program_main()
    except Exception:
        logger.exception("Error running the kernel_program")
        sys.exit(1)


def start_subprocess(name, proc, logger):
    process = multiprocessing.Process(target=proc, name=name, args=[logger])
    process.start()
    return process


def print_banner(logger):
    logger.info(
        """
█▀▀ █▀█ ▀█▀ ▄▄ █▀▀ █▀█ █▀▄ █▀▀
█▄█ █▀▀ ░█░ ░░ █▄▄ █▄█ █▄▀ ██▄
    """
    )
    logger.info("> Open GPT-Code UI in your browser %s" % APP_URL)
    logger.info("You can inspect detailed logs in app.log.")
    logger.info("Contribute to GPT-Code UI at https://github.com/ricklamers/gpt-code-ui")


def main():
    logger = config.get_logger("GPT Code UI")

    SUBPROCESSES = {
        "WebApp": run_webapp,
        "Kernel API": run_kernel_program,
    }

    try:
        subprocesses = {name: start_subprocess(name, proc, logger) for name, proc in SUBPROCESSES.items()}

        # Poll until the webapp is running
        while True:
            try:
                app.test_client().get("/")
                break
            except Exception:
                time.sleep(0.1)

        print_banner(logger)

        webbrowser.open(APP_URL)

        while True:
            multiprocessing.connection.wait(process.sentinel for process in subprocesses.values())

            for name in list(subprocesses.keys()):
                if (exitcode := subprocesses[name].exitcode) is not None:
                    logger.info(f"{name} process terminated with exit code {exitcode}. Restarting.")
                    subprocesses[name] = start_subprocess(name, SUBPROCESSES[name], logger)

    except KeyboardInterrupt:
        logger.info("Terminating processes...")

        for process in subprocesses.values():
            process.terminate()

        for process in subprocesses.values():
            process.join()

        logger.info("Processes terminated.")


if __name__ == "__main__":
    main()
