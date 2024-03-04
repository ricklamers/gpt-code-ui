import logging
import os
import pathlib
import sys

from dotenv import load_dotenv

load_dotenv(".env")

IDENT_MAIN = "kernel_program.main"
KERNEL_PID_DIR = "process_pids"
NO_INTERNET_AVAILABLE = os.environ.get("NO_INTERNET_AVAILABLE", "FALSE")[0] in (
    "1",
    "t",
    "T",
)
KERNEL_APP_PORT = int(os.environ.get("API_PORT", 5010))
KERNEL_BASE_DIR = pathlib.Path(os.environ.get("KERNEL_BASE_DIR", "workspace"))
if not KERNEL_BASE_DIR.is_absolute():
    KERNEL_BASE_DIR = KERNEL_BASE_DIR.absolute()  # assuming it is relative to the current working dir
KERNEL_BASE_DIR.mkdir(parents=True, exist_ok=True)
BASE_VENV = KERNEL_BASE_DIR / "kernel.base"

WATCHDOG_INTERVAL_S = float(os.getenv("KERNEL_MANAGER_WATCHDOG_INTERVAL_S", 60))
assert WATCHDOG_INTERVAL_S > 0
KERNEL_TIMEOUT_S = float(os.getenv("KERNEL_MANAGER_TIMEOUT_S", 3600))
assert KERNEL_TIMEOUT_S > 0


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        logFormatter = logging.Formatter(fmt="%(asctime)s [%(levelname)8s %(name)s]  %(message)s")

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.DEBUG if "DEBUG" in os.environ else logging.WARNING)
        consoleHandler.setFormatter(logFormatter)
        logger.addHandler(consoleHandler)

        file_handler = logging.FileHandler("app.log", mode="a")
        file_handler.setLevel(logging.DEBUG if "DEBUG" in os.environ else logging.WARNING)
        file_handler.setFormatter(logFormatter)
        logger.addHandler(file_handler)

    return logger
