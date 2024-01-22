import logging
import os
import pathlib

IDENT_MAIN = "kernel_program.main"
KERNEL_PID_DIR = "process_pids"
SNAKEMQ_PORT = int(os.environ.get("SNAKEMQ_PORT", 8765))
NO_INTERNET_AVAILABLE = os.environ.get("NO_INTERNET_AVAILABLE", "FALSE")[0] in (
    "1",
    "t",
    "T",
)
KERNEL_APP_PORT = int(os.environ.get("API_PORT", 5010))
KERNEL_BASE_DIR = pathlib.Path(os.environ.get("KERNEL_BASE_DIR", "workspace"))
if not KERNEL_BASE_DIR.is_absolute():
    KERNEL_BASE_DIR = (
        KERNEL_BASE_DIR.absolute()
    )  # assuming it is relative to the current working dir
KERNEL_BASE_DIR.mkdir(parents=True, exist_ok=True)
BASE_VENV = KERNEL_BASE_DIR / "kernel.base"


def get_logger():
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s"
    )

    logger = logging.getLogger(__name__)
    if "DEBUG" in os.environ:
        logger.setLevel(logging.DEBUG)
    return logger
