# Run the webapp and kernel_program in separate processes

# webapp is a Flask app (in webapp/main.py relative to this main.py)
# kernel_program is a Python script (in kernel_program/main.py relative to this main.py)

import sys
import logging
import asyncio
from multiprocessing import Process

from gpt_code.webapp.main import app
from gpt_code.kernel_program.main import main, cleanup_kernel_program

def run_webapp():
    try:
        app.run(debug=True, port=8080, use_reloader=False)
    except Exception as e:
        logging.exception("Error running the webapp:")
        sys.exit(1)

def run_kernel_program():
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Error running the kernel_program:")
        sys.exit(1)

def setup_logging():
    log_format = "%(asctime)s [%(levelname)s]: %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    log_filename = "app.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)

if __name__ == "__main__":
    setup_logging()

    webapp_process = Process(target=run_webapp)
    kernel_program_process = Process(target=run_kernel_program)

    try:
        webapp_process.start()
        kernel_program_process.start()

        webapp_process.join()
        kernel_program_process.join()
    except KeyboardInterrupt:
        print("Terminating processes...")
        
        cleanup_kernel_program()
        kernel_program_process.terminate()

        webapp_process.terminate()

        webapp_process.join()
        kernel_program_process.join()

        print("Processes terminated.")