import logging
import os

IDENT_KERNEL_MANAGER = "kernel_manager"
IDENT_MAIN = "main"
KERNEL_PID_DIR = "process_pids"
SNAKEMQ_PORT = int(os.environ.get("SNAKEMQ_PORT", 8765))


def get_logger():
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s"
    )

    logger = logging.getLogger(__name__)
    if "DEBUG" in os.environ:
        logger.setLevel(logging.DEBUG)
    return logger