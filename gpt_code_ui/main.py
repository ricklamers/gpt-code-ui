# Run the webapp and kernel_program in separate processes

# webapp is a Flask app (in webapp/main.py relative to this main.py)
# kernel_program is a Python script (in kernel_program/main.py relative to this main.py)
import sys
import time
import webbrowser
from multiprocessing import Process

from gpt_code_ui.kernel_program.main import main as kernel_program_main
from gpt_code_ui.webapp.main import APP_PORT, app
import gpt_code_ui.kernel_program.config as config


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


def print_color(text, color="gray"):
    # Default to gray
    code = "242"

    if color == "green":
        code = "35"

    gray_code = "\033[38;5;%sm" % code
    reset_code = "\033[0m"
    print(f"{gray_code}{text}{reset_code}")


def print_banner():
    print(
        """
█▀▀ █▀█ ▀█▀ ▄▄ █▀▀ █▀█ █▀▄ █▀▀
█▄█ █▀▀ ░█░ ░░ █▄▄ █▄█ █▄▀ ██▄
    """
    )

    print("> Open GPT-Code UI in your browser %s" % APP_URL)
    print("")
    print("You can inspect detailed logs in app.log.")
    print("")
    print("Find your OpenAI API key at https://platform.openai.com/account/api-keys")
    print("")
    print_color("Contribute to GPT-Code UI at https://github.com/ricklamers/gpt-code-ui")


def main():
    logger = config.get_logger("GPT Code UI")

    webapp_process = Process(target=run_webapp, name="WebApp", args=[logger])
    kernel_program_process = Process(target=run_kernel_program, name="Kernel API", args=[logger])

    try:
        webapp_process.start()
        kernel_program_process.start()

        # Poll until the webapp is running
        while True:
            try:
                app.test_client().get("/")
                break
            except Exception:
                time.sleep(0.1)

        print_banner()

        webbrowser.open(APP_URL)

        webapp_process.join()
        kernel_program_process.join()

    except KeyboardInterrupt:
        logger.info("Terminating processes...")

        kernel_program_process.terminate()
        webapp_process.terminate()

        webapp_process.join()
        kernel_program_process.join()

        logger.info("Processes terminated.")


if __name__ == "__main__":
    main()
