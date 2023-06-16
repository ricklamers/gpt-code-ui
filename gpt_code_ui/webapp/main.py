# The GPT web UI as a template based Flask app
import os
import requests
import json
import asyncio
import re
import logging
import sys

from collections import deque

from flask_cors import CORS
from flask import Flask, request, jsonify, send_from_directory, Response
from dotenv import load_dotenv

from gpt_code_ui.kernel_program.main import APP_PORT as KERNEL_APP_PORT

load_dotenv('.env')

OPENAI_API_TYPE = os.environ.get("OPENAI_API_TYPE", "openai")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com")
OPENAI_API_VERSION = os.environ.get("OPENAI_API_VERSION", "2023-03-15-preview")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")


UPLOAD_FOLDER = 'workspace/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


APP_PORT = int(os.environ.get("WEB_PORT", 8080))


class LimitedLengthString:
    def __init__(self, maxlen=2000):
        self.data = deque()
        self.len = 0
        self.maxlen = maxlen

    def append(self, string):
        self.data.append(string)
        self.len += len(string)
        while self.len > self.maxlen:
            popped = self.data.popleft()
            self.len -= len(popped)

    def get_string(self):
        result = ''.join(self.data)
        return result[-self.maxlen:]


message_buffer = LimitedLengthString()


def allowed_file(filename):
    return True


async def get_code(user_prompt, user_openai_key=None, model="gpt-3.5-turbo"):

    prompt = f"""First, here is a history of what I asked you to do earlier. 
    The actual prompt follows after ENDOFHISTORY. 
    History:
    {message_buffer.get_string()}
    ENDOFHISTORY.
    Write Python code, in a triple backtick Markdown code block, that does the following:
    {user_prompt}
    
    Notes: 
        First, think step by step what you want to do and write it down in English.
        Then generate valid Python code in a code block 
        Make sure all code is valid - it be run in a Jupyter Python 3 kernel environment. 
        Define every variable before you use it.
        For data munging, you can use 
            'numpy', # numpy==1.24.3
            'dateparser' #dateparser==1.1.8
            'pandas', # matplotlib==1.5.3
            'geopandas' # geopandas==0.13.2
        For pdf extraction, you can use
            'PyPDF2', # PyPDF2==3.0.1
            'pdfminer', # pdfminer==20191125
            'pdfplumber', # pdfplumber==0.9.0
        For data visualization, you can use
            'matplotlib', # matplotlib==3.7.1
        Be sure to generate charts with matplotlib. If you need geographical charts, use geopandas with the geopandas.datasets module.
        If the user has just uploaded a file, focus on the file that was most recently uploaded (and optionally all previously uploaded files)
    
    Teacher mode: if the code modifies or produces a file, end your output AFTER YOUR CODE BLOCK with a link to it as <a href='/download?file=INSERT_FILENAME_HERE'>Download file</a>. Replace INSERT_FILENAME_HERE with the actual filename. So just print that HTML to stdout at the end, AFTER your code block."""
    temperature = 0.7
    message_array = [
        {
            "role": "user",
            "content": prompt,
        },
    ]

    final_openai_key = OPENAI_API_KEY
    if user_openai_key:
        final_openai_key = user_openai_key

    if OPENAI_API_TYPE == "openai":
        data = {
            "model": model,
            "messages": message_array,
            "temperature": temperature,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {final_openai_key}",
        }

        response = requests.post(
            f"{OPENAI_BASE_URL}/v1/chat/completions",
            data=json.dumps(data),
            headers=headers,
        )
    elif OPENAI_API_TYPE == "azure":
        data = {
            "messages": message_array,
            "temperature": temperature,
        }
        headers = {
            "Content-Type": "application/json",
            "api-key": f"{final_openai_key}",
        }

        response = requests.post(
            f"{OPENAI_BASE_URL}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={OPENAI_API_VERSION}",
            data=json.dumps(data),
            headers=headers,
        )
    else:
        return "Error: Invalid OPENAI_PROVIDER", 500

    def extract_code(text):
        # Match triple backtick blocks first
        triple_match = re.search(r'```(?:\w+\n)?(.+?)```', text, re.DOTALL)
        if triple_match:
            return triple_match.group(1).strip()
        else:
            # If no triple backtick blocks, match single backtick blocks
            single_match = re.search(r'`(.+?)`', text, re.DOTALL)
            if single_match:
                return single_match.group(1).strip()
        # If no code blocks found, return original text
        return text

    if response.status_code != 200:
        return "Error: " + response.text, 500

    return extract_code(response.json()["choices"][0]["message"]["content"]), 200

# We know this Flask app is for local use. So we can disable the verbose Werkzeug logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)


@app.route('/')
def index():

    # Check if index.html exists in the static folder
    if not os.path.exists(os.path.join(app.root_path, 'static/index.html')):
        print("index.html not found in static folder. Exiting. Did you forget to run `make compile_frontend` before installing the local package?")

    return send_from_directory('static', 'index.html')


@app.route('/api/<path:path>', methods=["GET", "POST"])
def proxy_kernel_manager(path):
    if request.method == "POST":
        resp = requests.post(
            f'http://localhost:{KERNEL_APP_PORT}/{path}', json=request.get_json())
    else:
        resp = requests.get(f'http://localhost:{KERNEL_APP_PORT}/{path}')

    excluded_headers = ['content-encoding',
                        'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


@app.route('/assets/<path:path>')
def serve_static(path):
    return send_from_directory('static/assets/', path)


@app.route('/download')
def download_file():

    # Get query argument file
    file = request.args.get('file')
    # from `workspace/` send the file
    # make sure to set required headers to make it download the file
    return send_from_directory(os.path.join(os.getcwd(), 'workspace'), file, as_attachment=True)


@app.route('/inject-context', methods=['POST'])
def inject_context():
    user_prompt = request.json.get('prompt', '')

    # Append all messages to the message buffer for later use
    message_buffer.append(user_prompt + "\n\n")

    return jsonify({"result": "success"})


@app.route('/generate', methods=['POST'])
def generate_code():
    user_prompt = request.json.get('prompt', '')
    user_openai_key = request.json.get('openAIKey', None)
    model = request.json.get('model', None)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    code, status = loop.run_until_complete(
        get_code(user_prompt, user_openai_key, model))
    loop.close()

    # Append all messages to the message buffer for later use
    message_buffer.append(user_prompt + "\n\n")

    return jsonify({'code': code}), status


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return jsonify({'message': 'File successfully uploaded'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=APP_PORT, debug=True, use_reloader=False)
