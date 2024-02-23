import atexit
import logging
import sys

from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps

from gpt_code_ui.kernel_program import config  # noqa: E402
from gpt_code_ui.kernel_program.kernel import Kernel, StoppableThread  # noqa: E402
from gpt_code_ui.kernel_program.kernel_manager import KernelManager  # noqa: E402

kernel_manager = KernelManager()


class WatchdogThread(StoppableThread):
    def __init__(self, kernel_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = config.get_logger("Watchdog Thread")
        self._kernel_manager = kernel_manager

    def run(self):
        while not self.stopped(timeout=config.WATCHDOG_INTERVAL_S):
            km = self._kernel_manager
            timeout_limit = datetime.now() - timedelta(seconds=config.KERNEL_TIMEOUT_S)

            self._logger.info(f"Purging kernels accessed before {timeout_limit}")
            expired_sessions = []
            for session_id, kernel in km.items():
                if hasattr(kernel, "last_access") and kernel.last_access < timeout_limit:
                    self._logger.info(
                        f"Kernel for session {session_id} expired, last access: {kernel.last_access} which was more than {config.KERNEL_TIMEOUT_S}s ago."
                    )
                    expired_sessions.append(session_id)

            km.purge_kernels(expired_sessions)


# We know this Flask app is for local use. So we can disable the verbose Werkzeug logger
logging.getLogger("werkzeug").setLevel(logging.ERROR)

cli = sys.modules["flask.cli"]
cli.show_server_banner = lambda *x: None  # type: ignore

app = Flask(__name__)
CORS(app)


def kernel_specific(func):
    @wraps(func)
    def wrapper(session_id, *args, **kwargs):
        kernel = kernel_manager.get(session_id)
        kernel.last_access = datetime.now()
        return func(kernel, *args, **kwargs)

    return wrapper


@app.route("/api/<session_id>", methods=["POST", "GET"])
@kernel_specific
def handle_request(kernel: Kernel):
    if request.method == "GET":
        # Handle GET requests by sending everything that is in the receive_queue
        return jsonify({"results": kernel.get_results(), "status": kernel.status})
    elif request.method == "POST":
        kernel.execute(request.json)
        return jsonify({"result": "success", "status": kernel.status})


@app.route("/status/<session_id>", methods=["POST", "GET"])
@kernel_specific
def handle_status(kernel: Kernel):
    if request.method == "POST":
        kernel.set_status(request.json["status"])

    return jsonify({"result": "success", "status": kernel.status})


@app.route("/restart/<session_id>", methods=["POST"])
@kernel_specific
def handle_restart(kernel: Kernel):
    kernel.restart()
    return jsonify({"result": "success", "status": kernel.status})


@app.route("/workdir/<session_id>", methods=["GET"])
@kernel_specific
def handle_workdir(kernel: Kernel):
    return jsonify({"result": str(kernel.workdir)})


def main():
    # Monitor last access to kernels, remove all that have not been accessed in a while
    watchdog_thread = WatchdogThread(
        name="Kernel Manager Watchdog Thread",
        kernel_manager=kernel_manager,
    )

    watchdog_thread.start()
    atexit.register(lambda: cleanup(watchdog_thread))
    app.run(host="0.0.0.0", port=config.KERNEL_APP_PORT)


def cleanup(watchdog_thread):
    watchdog_thread.stop(wait=True)
    kernel_manager.terminate()


if __name__ == "__main__":
    main()
