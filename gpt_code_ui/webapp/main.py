# The GPT web UI as a template based Flask app
import asyncio
import json
import logging
import os
import re
import sys
import uuid
from collections import defaultdict
from functools import wraps
from typing import Dict, List

import pandas as pd
import pandas.api.types as pd_types
import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory, session
from flask_cors import CORS
from foundry_dev_tools import FoundryRestClient
from foundry_dev_tools.foundry_api_client import FoundryAPIError

from gpt_code_ui.kernel_program.config import KERNEL_APP_PORT
from gpt_code_ui.webapp import llm
from gpt_code_ui.webapp.prompts import get_system_prompt

load_dotenv(".env")

AVAILABLE_MODELS = llm.get_available_models()
SESSION_ENCRYPTION_KEY = os.environ["SESSION_ENCRYPTION_KEY"]
APP_PORT = int(os.environ.get("WEB_PORT", 8080))
FOUNDRY_DATA_FOLDER = os.getenv("FOUNDRY_DATA_FOLDER", "/Group Functions/mgf-use-case-gpt-code-ui/data")


class ChatHistory:
    def __init__(self, system_prompt: str = None):
        self._buffer: List[Dict[str, str]] = list()
        self._last_untruncated = None
        self._truncation_maxlines = 20

        if system_prompt is None:
            system_prompt = get_system_prompt()

        self._append("system", system_prompt)

    def _append(self, role: str, content: str, name: str = None):
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"Invalid role: {role}")

        entry = {"role": role, "content": content}
        if name is not None:
            entry["name"] = name

        self._buffer.append(entry)

    def _extend_or_append(self, role: str, prefix: str, content: str, name: str = None) -> bool:
        """Returns true if a new entry has been created (i.e. append instead of extend)"""
        last = self._buffer[-1]
        if last["role"] == role and last.get("name", None) == name:
            last["content"] += content
            return False
        else:
            self._append(role, f"{prefix}\n{content}", name)
            return True

    def _truncate(self, s: str) -> str:
        return "\n".join(s.splitlines()[: self._truncation_maxlines])

    def _update_truncation(self):
        if self._last_untruncated is not None:
            self._buffer[self._last_untruncated]["content"] = self._truncate(
                self._buffer[self._last_untruncated]["content"]
            )
        self._last_untruncated = len(self._buffer) - 1

    def add_prompt(self, prompt: str):
        self._append("user", prompt, "User")

    def add_answer(self, answer: str):
        self._append("assistant", answer)

    def upload_file(self, filename: str, file_info: str = None):
        self._append(
            "user",
            f"In the following, I will refer to the file {filename}.\n{file_info}",
        )

    def add_execution_result(self, result: str):
        if self._extend_or_append(
            "user",
            "These are the first lines of the output generated when executing the code:",
            result,
            "Computer",
        ):
            self._update_truncation()

    def add_error(self, message: str):
        if self._extend_or_append(
            "user",
            "Executing this code lead to an error.\nThe first lines of the error message read:",
            message,
            "Computer",
        ):
            self._update_truncation()

    def __call__(self, exclude_system: bool = False, override_system_prompt: str = None):
        if exclude_system:
            return [entry for entry in self._buffer if entry["role"] != "system"]
        elif override_system_prompt is not None:
            buffer = [entry for entry in self._buffer if entry["role"] != "system"]
            buffer.insert(0, {"role": "system", "content": override_system_prompt})
            return buffer
        else:
            return self._buffer


chat_history: Dict[str, ChatHistory] = defaultdict(ChatHistory)


def allowed_file(filename):
    return True


def inspect_file(filename: str) -> str:
    NUM_SAMPLE_ROWS = 5
    READER_MAP = {
        ".csv": pd.read_csv,
        ".tsv": pd.read_csv,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".xml": pd.read_xml,
        ".json": pd.read_json,
        ".hdf": pd.read_hdf,
        ".hdf5": pd.read_hdf,
        ".feather": pd.read_feather,
        ".parquet": pd.read_parquet,
        ".pkl": pd.read_pickle,
        ".sql": pd.read_sql,
    }

    def _convert_type(t):
        if pd_types.is_string_dtype(t):
            return "string"
        elif pd_types.is_integer_dtype(t):
            return "integer"
        elif pd_types.is_float_dtype(t):
            return "float"
        else:
            return t

    _, ext = os.path.splitext(filename)

    try:
        df: pd.DataFrame = READER_MAP[ext.lower()](filename)
        column_table = "| Column Name | Column Type |\n| ----------- | ----------- |\n" + "\n".join(
            [f"| {n} | {_convert_type(t)} |" for n, t in df.dtypes.items()]
        )
        return f"""The file contains the following columns:
{column_table}

The table has {len(df.index)} rows. The first {NUM_SAMPLE_ROWS} rows read
{df.head(NUM_SAMPLE_ROWS).to_markdown()}
"""
    except KeyError:
        return ""  # unsupported file type
    except Exception:
        return ""  # file reading failed. - Don't want to know why.


async def get_code(messages, model="openai/gpt-3.5-turbo"):
    try:
        content = llm.call(messages, model=model)
    except RuntimeError as e:
        return None, str(e), 500
    else:

        def extract_code(text):
            # Match triple backtick blocks first
            triple_match = re.search(
                r"```(?:(?:[^\r\n]*[pP]ython[^\r\n]*[\r\n])|(?:\w+\n))?(.+?)```",
                text,
                re.DOTALL,
            )
            if triple_match:
                return triple_match.group(1).strip()
            else:
                # If no triple backtick blocks, match single backtick blocks
                single_match = re.search(r"`(.+?)`", text, re.DOTALL)
                if single_match:
                    return single_match.group(1).strip()

        return extract_code(content), content.strip(), 200


# We know this Flask app is for local use. So we can disable the verbose Werkzeug logger
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

cli = sys.modules["flask.cli"]
cli.show_server_banner = lambda *x: None  # type: ignore

app = Flask(__name__)
app.secret_key = SESSION_ENCRYPTION_KEY

CORS(app)


def session_id_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        if (session_id := session.get("session_id", None)) is None:
            session_id = str(uuid.uuid4())
            session["session_id"] = session_id
        return function_to_protect(session_id, *args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/models")
def models():
    return jsonify(AVAILABLE_MODELS)


@app.route("/assets/<path:path>")
def serve_static(path):
    return send_from_directory("static/assets/", path)


@app.route("/api/<path:path>", methods=["GET", "POST"])
@session_id_required
def proxy_kernel_manager(session_id, path):
    backend_url = f"http://localhost:{KERNEL_APP_PORT}/{path}/{session_id}"

    try:
        if request.method == "POST":
            resp = requests.post(backend_url, json=request.get_json())
        else:
            resp = requests.get(backend_url)
    except requests.exceptions.ConnectionError as e:
        return jsonify({"message": f"Failed to communicate with backend server: {e}."}), 500

    # store execution results in conversation history to allow back-references by the user
    content = json.loads(resp.content)
    for res in content.get("results", []):
        if res["type"] == "message":
            chat_history[session_id].add_execution_result(res["value"])
        elif res["type"] == "message_error":
            chat_history[session_id].add_error(res["value"])

        log.debug(session_id, res)

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

    # inject the conversation history into the results
    content["chat_history"] = chat_history[session_id](exclude_system=True)

    return Response(json.dumps(content), resp.status_code, headers)


@app.route("/download")
@session_id_required
def download_file(session_id):
    # Get query argument file
    file = request.args.get("file")
    # find out the workspace directory corresponding to the specific session
    resp = requests.get(f"http://localhost:{KERNEL_APP_PORT}/workdir/{session_id}")
    if resp.status_code == 200:
        workdir = resp.json()["result"]
    else:
        return resp, resp.status_code

    return send_from_directory(workdir, file, as_attachment=True)


@app.route("/clear_history", methods=["POST"])
@session_id_required
def clear_history(session_id):
    del chat_history[session_id]
    return jsonify({"result": "success"})


@app.route("/generate", methods=["POST"])
@session_id_required
def generate_code(session_id):
    requests.post(
        f"http://localhost:{KERNEL_APP_PORT}/status/{session_id}",
        json={"status": "generating"},
    )

    user_prompt = request.json.get("prompt", "")
    model = request.json.get("model", None)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    chat_history[session_id].add_prompt(user_prompt)

    code, text, status = loop.run_until_complete(get_code(chat_history[session_id](), model))
    loop.close()

    if status == 200:
        chat_history[session_id].add_answer(text)

    requests.post(
        f"http://localhost:{KERNEL_APP_PORT}/status/{session_id}",
        json={"status": "ready"},
    )

    return jsonify({"code": code, "text": text}), status


@app.route("/upload", methods=["POST"])
@session_id_required
def upload_file(session_id):
    # check if the post request has the file part
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files["file"]
    # if user does not select file, browser also submit an empty part without filename
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        # find out the workspace directory corresponding to the specific session
        resp = requests.get(f"http://localhost:{KERNEL_APP_PORT}/workdir/{session_id}")
        if resp.status_code == 200:
            workdir = resp.json()["result"]
        else:
            return resp, resp.status_code

        file_target = os.path.join(workdir, file.filename)
        file.save(file_target)
        file_info = inspect_file(file_target)
        chat_history[session_id].upload_file(file.filename, file_info)
        return jsonify({"message": f"File `{file.filename}` uploaded successfully.\n{file_info}"}), 200
    else:
        return jsonify({"message": "File type not supported."}), 400


@app.route("/foundry_files", methods=["GET", "POST"])
@session_id_required
def foundry_files(session_id, folder=None):
    try:
        fc = FoundryRestClient()
    except ValueError as e:
        log.exception(e)
        return "Foundry access misconfigured on server", 500

    if request.method == "POST":
        req = request.get_json()
        dataset_rid = req["dataset_rid"]

        # find out the workspace directory corresponding to the specific session
        resp = requests.get(f"http://localhost:{KERNEL_APP_PORT}/workdir/{session_id}")
        if resp.status_code == 200:
            workdir = resp.json()["result"]
        else:
            return resp, resp.status_code

        try:
            files = fc.download_dataset_files(dataset_rid, workdir)
        except requests.exceptions.HTTPError as e:
            return e.response.json().get("errorCode", "Unknown Error"), e.response.status_code

        results = []
        http_code = 400
        for file in files:
            filename = os.path.relpath(file, workdir)

            if allowed_file(file):
                file_info = inspect_file(file)
                chat_history[session_id].upload_file(filename, file_info)

                results.append(
                    {
                        "filename": filename,
                        "message": f"File `{filename}` downloaded successfully.\n{file_info}",
                    }
                )
                http_code = 200
            else:
                results.append({"filename": filename, "message": "File type not supported."})

        return jsonify(results), http_code
    else:
        folder = request.args.get("folder", FOUNDRY_DATA_FOLDER)

        try:
            if folder.startswith("/"):
                # this is a path - query the RID
                folder_rid = fc.get_dataset_rid(folder)
            else:
                # this must be an RID - query the path
                folder_rid, folder = folder, fc.get_dataset_path(folder)

            files = fc.get_child_objects_of_folder(folder_rid)
            return jsonify(
                {
                    "folder": folder,
                    "folder_rid": folder_rid,
                    "datasets": [{"name": f["name"], "dataset_rid": f["rid"]} for f in files],
                }
            )
        except FoundryAPIError:
            return "Folder not accessible", 404


if __name__ == "__main__":
    # Check if index.html exists in the static folder
    if not os.path.exists(os.path.join(app.root_path, "static/index.html")):
        raise RuntimeError(
            "index.html not found in static folder. Exiting. Did you forget to run `make compile_frontend` before installing the local package?"
        )
    else:
        app.run(host="0.0.0.0", port=APP_PORT, debug=True, use_reloader=False)
