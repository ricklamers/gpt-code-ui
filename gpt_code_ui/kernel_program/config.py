import logging
import os

for key, value in os.environ.items():
    print(f'{key} = {value}')

BASE_VENV = 'kernel.base'
IDENT_MAIN = "kernel_program.main"
KERNEL_PID_DIR = "process_pids"
SNAKEMQ_PORT = int(os.environ.get("SNAKEMQ_PORT", 8765))
NO_INTERNET_AVAILABLE = os.environ.get("NO_INTERNET_AVAILABLE", "FALSE")[0] in ("1", "t", "T")


def get_logger():
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s"
    )

    logger = logging.getLogger(__name__)
    if "DEBUG" in os.environ:
        logger.setLevel(logging.DEBUG)
    return logger
