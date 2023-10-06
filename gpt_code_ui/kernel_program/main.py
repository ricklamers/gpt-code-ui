import os
import subprocess
import sys
import pathlib
import json
import logging
import time
from typing import Dict

import asyncio
import threading

from queue import Queue

from flask import Flask, request, jsonify
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv('.env')

import gpt_code_ui.kernel_program.config as config
import gpt_code_ui.kernel_program.utils as utils


APP_PORT = int(os.environ.get("API_PORT", 5010))

# Get global logger
logger = config.get_logger()


class KernelManager:
    KERNEL_MANAGER_SCRIPT_PATH = pathlib.Path(__file__).parent.resolve() / 'kernel_manager.py'

    def __init__(self, session_id: str):
        print(f'Creating kernel {session_id}')
        self._session_id = session_id
        self._workdir = pathlib.Path(os.getcwd()) / f'kernel.{self._session_id}'
        self._result_queue = Queue()
        self._send_queue = Queue()

        self._status = "starting"
        self._result_queue.put({"value": "Starting Kernel...", "type": "message_status"})

        self._process = subprocess.Popen([
            sys.executable,
            KernelManager.KERNEL_MANAGER_SCRIPT_PATH,
            self._session_id,
            self._workdir,
        ])

    @property
    def status(self):
        return self._status

    def set_status(self, status: str):
        self._status = status

    def __del__(self):
        print(f'Killing kernel {self._session_id}')
        self._status = 'stopping'
        self._process.terminate()
        self._status = 'stopped'

    def on_recv(self, message):
        if message["type"] == "status":
            message["type"] = "message_status"
            self._status = message["value"]

            if self.status == "ready":
                message["value"] = "Kernel is ready."
            else:
                raise ValueError(f'Unexpected status_message {self.status}')

        elif message["type"] in ["message", "message_raw", "message_error", "image/png", "image/jpeg"]:
            pass

        else:
            raise ValueError(f'Unexpected message type {message["type"]}')

        self._result_queue.put({"value": message["value"], "type": message["type"]})

    def execute(self, command):
        self._send_queue.put({"value": command, "type": "execute"})

    def get_results(self):
        return [self._result_queue.get() for _ in range(self._result_queue.qsize())]

    def get_messages(self):
        return [self._send_queue.get() for _ in range(self._send_queue.qsize())]

    @property
    def workdir(self) -> str:
        return self._workdir

    @property
    def session_id(self) -> str:
        return self._session_id


kernel_managers: Dict[str, KernelManager] = dict()
kernel_managers_lock = threading.Lock()
messaging = None

# We know this Flask app is for local use. So we can disable the verbose Werkzeug logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)
CORS(app)


async def start_snakemq():
    global kernel_managers
    global messaging

    messaging, link = utils.init_snakemq(config.IDENT_MAIN)

    def on_recv(conn, ident, message):
        session_id = ident
        message = json.loads(message.data.decode("utf-8"))
        logger.debug(f'{message["value"]} of type {message["type"]} from {session_id}')
        kernel_managers[session_id].on_recv(message)

    messaging.on_message_recv.add(on_recv)
    logger.info("Starting snakemq loop")

    def send_queued_messages():
        while True:
            for session_id, kernel in kernel_managers.items():
                for message in kernel.get_messages():
                    print(f'Sending {message} to {session_id}.')
                    utils.send_json(messaging, message, session_id)
            time.sleep(0.1)

    async def async_send_queued_messages():
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_queued_messages)

    async def async_link_loop():
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, link.loop)

    # Wrap the snakemq_link.Link loop in an asyncio task
    await asyncio.gather(async_send_queued_messages(), async_link_loop())


def _get_kernel_manager(session_id: str, force_recreate: bool = False) -> KernelManager:
    global kernel_managers
    if force_recreate:
        kernel_managers_lock.acquire()
        try:
            kernel_managers[session_id] = KernelManager(session_id)
        finally:
            kernel_managers_lock.release()
    else:
        if session_id not in kernel_managers:
            kernel_managers_lock.acquire()
            try:
                # while waiting for the lock, the object already might have been created --> check again inside the lock
                if session_id not in kernel_managers:
                    kernel_managers[session_id] = KernelManager(session_id)
            finally:
                kernel_managers_lock.release()

    return kernel_managers[session_id]


@app.route("/api/<session_id>", methods=["POST", "GET"])
def handle_request(session_id: str):
    km = _get_kernel_manager(session_id)

    if request.method == "GET":
        # Handle GET requests by sending everything that is in the receive_queue
        return jsonify({"results": km.get_results(), "status": km.status})
    elif request.method == "POST":
        km.execute(request.json['command'])
        return jsonify({"result": "success", "status": km.status})


@app.route("/status/<session_id>", methods=["POST", "GET"])
def handle_status(session_id: str):
    km = _get_kernel_manager(session_id)

    if request.method == "POST":
        km.set_status(request.json['status'])

    return jsonify({"result": "success", "status": km.status})


@app.route("/restart/<session_id>", methods=["POST"])
def handle_restart(session_id):
    km = _get_kernel_manager(session_id, force_recreate=True)
    return jsonify({"result": "success", "status": km.status})


@app.route("/shutdown/<session_id>", methods=["POST"])
def handle_shutdown(session_id):
    global kernel_managers
    kernel_managers_lock.acquire()
    try:
        del kernel_managers[session_id]
    finally:
        kernel_managers_lock.release()
    return jsonify({"result": "success", "status": "terminated"})


@app.route("/workdir/<session_id>", methods=["GET"])
def handle_workdir(session_id):
    km = _get_kernel_manager(session_id)
    return jsonify({"result": str(km.workdir)})


async def main():
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Run in background
    await start_snakemq()


def run_flask_app():
    app.run(host="0.0.0.0", port=APP_PORT)


if __name__ == "__main__":
    asyncio.run(main())
