# The GPT web UI as a template based Flask app
import os
import requests
import json
import asyncio
import re

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
UPLOAD_FOLDER = 'workspace/'

def allowed_file(filename):
    return True

async def get_code(user_prompt):
    prompt = f"Write Python code that does the following: \n\n{user_prompt}\n\nNote, the code is going to be executed in a Jupyter Python kernel.\n\nLast instruction, and this is the most important, just return code. No other outputs, as your full response will directly be executed in the kernel."

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.7,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data),
        headers=headers,
    )

    def extract_code(text):
        match = re.search(r'```(?:\w+\n)?(.+?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return text

    return extract_code(response.json()["choices"][0]["message"]["content"])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_code():
    user_prompt = request.json.get('prompt', '')
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    code = loop.run_until_complete(get_code(user_prompt))
    loop.close()

    return jsonify({'code': code})

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
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File successfully uploaded'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080, use_reloader=False)
