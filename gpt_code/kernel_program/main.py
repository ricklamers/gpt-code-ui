import os
import atexit
import subprocess
import sys
import pathlib
import json

import asyncio
import json
import threading

from queue import Queue

from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS library


import gpt_code.kernel_program.kernel_manager as kernel_manager
import gpt_code.kernel_program.config as config
import gpt_code.kernel_program.utils as utils

# Get global logger
logger = config.get_logger()

# Note, only one kernel_manager_process can be active
kernel_manager_process = None

# Use efficient Python queues to store messages
result_queue = Queue()

messaging = None

app = Flask(__name__)
CORS(app)

def start_kernel_manager():
    global kernel_manager_process
    print("start_kernel_manager")

    kernel_manager_script_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(), "kernel_manager.py"
    )
    kernel_manager_process = subprocess.Popen(
        [sys.executable, kernel_manager_script_path]
    )

    # Write PID as <pid>.pid to config.KERNEL_PID_DIR
    os.makedirs(config.KERNEL_PID_DIR, exist_ok=True)
    with open(os.path.join(config.KERNEL_PID_DIR, "%d.pid" % kernel_manager_process.pid), "w") as p:
        p.write("kernel_manager")

def cleanup_kernel_program():
    kernel_manager.cleanup_spawned_processes()

async def start_snakemq():
    print("start_snakemq")
    global messaging

    messaging, link = utils.init_snakemq(config.IDENT_MAIN)
    print("init_snakemq done: %s" % messaging)

    def on_recv(conn, ident, message):
        message = json.loads(message.data.decode("utf-8"))

        if message["type"] == "status":
            if message["value"] == "ready":
                logger.debug("Kernel is ready.")
                result_queue.put("Kernel is ready.")

        elif message["type"] in ["message", "message_raw", "image/png"]:
            # TODO: 1:1 kernel <> channel mapping
            logger.debug("%s of type %s" % (message["value"], message["type"]))

            result_queue.put(message["value"])

    messaging.on_message_recv.add(on_recv)
    logger.info("Starting snakemq loop")

    # Wrap the snakemq_link.Link loop in an asyncio task
    loop = asyncio.get_event_loop()
    link_loop_task = loop.run_in_executor(None, link.loop)

    # Wait for the snakemq_link.Link loop to complete (if ever)
    await link_loop_task


@app.route("/api", methods=["POST", "GET"])
def handle_request():
    
    if request.method == "GET":
        # Handle GET requests by sending everything that's in the receive_queue
        results = [result_queue.get() for _ in range(result_queue.qsize())]
        return jsonify({"results": results})
    elif request.method == "POST":
        data = request.json

        utils.send_json(messaging, 
            {"type": "execute", "value": data["command"]}, 
            config.IDENT_KERNEL_MANAGER
        )
        return jsonify({"result": "success"})


async def main():
    start_kernel_manager()

    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Run in background
    await start_snakemq()


def run_flask_app():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    asyncio.run(main())



    