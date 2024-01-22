<img src="https://github.com/ricklamers/gpt-code-ui/assets/1309307/9ad4061d-2e26-4407-9431-109b650fb022" alt="GPT-Code logo" width=240 />

An open source implementation of OpenAI's ChatGPT [Code interpreter](https://openai.com/blog/chatgpt-plugins#code-interpreter).

Simply ask the OpenAI model to do something and it will generate & execute the code for you.

This project is an extended and further developed fork of of [Rick Lamer's GPT Code UI](https://github.com/ricklamers/gpt-code-ui).
Read the [blog post](https://ricklamers.io/posts/gpt-code) to find out more.

## User interface
![User Interface](UserInterface.png)
 
## Features
- File upload
- File download
- Dataset Download from Palantir Foundry using [Foundry Dev Tools](https://github.com/emdgroup/foundry-dev-tools)
- Context awareness (it can refer to your previous messages)
- Generate code
- Run code (Python kernel)
- Model switching (GPT-3.5 and GPT-4)

## Misc.
### Running the Docker Container as fully packaged Service
See the [Dockerfile](Dockerfile) for details. Most notably, we do not invoke the tool directly but via [run_with_app_service_config.py](rub_with_app_service_config.py), which extracts environment variable specifications from a json-formatted `APP_SERVICE_CONFIG` environment variable.
In order to run properly, your `APP_SERVICE_CONFIG` should read similar to
```
{
  "OPENAI_API_KEY": "<YOUR API KEY>",
  "OPENAI_API_BASE": "<YOUR_AZURE_API_URL>",
  "OPENAI_API_TYPE": "azure",
  "OPENAI_API_VERSION": "2023-06-01-preview",
  "AZURE_OPENAI_DEPLOYMENTS": [
    {"displayName": "GPT-3.5 0301", "name": "gpt-35-turbo-0301"},
    {"displayName": "GPT-3.5 0613", "name": "gpt-35-turbo-0613"},
    {"displayName": "GPT-3.5 16k", "name": "gpt-35-turbo-16k"},
    {"displayName": "GPT-4 0314", "name": "gpt-4-0314"}
  ],

  "API_PORT": 5010,
  "WEB_PORT": 8080,
  "SNAKEMQ_PORT": 8765,

  "NO_INTERNET_AVAILABLE": 1,

  "SESSION_ENCRYPTION_KEY": "67ed8ea0-05f0-4086-9a54-6b2bb6dbcf29",

  "DEBUG": 1,

  "FOUNDRY_DATA_FOLDER": "<YOUR FOUNDRY DATA FOLDER>"
}
```

### Running locally
For local execution, your `.env` could read similar to
```
OPENAI_API_KEY="<YOUR API KEY>"
OPENAI_API_BASE="<YOUR_AZURE_API_URL>"
OPENAI_API_TYPE="azure"
OPENAI_API_VERSION="2023-06-01-preview"
AZURE_OPENAI_DEPLOYMENTS=[{"displayName": "GPT-3.5", "name": "gpt-35-turbo-0613"}, {"displayName": "GPT-3.5 16k", "name": "gpt-35-turbo-16k"}, {"displayName": "GPT-4 0314", "name": "gpt-4-0314"}, {"displayName": "GPT-4 0613", "name": "gpt-4-0613"}, {"displayName": "GPT-4 32k", "name": "gpt-4-32k"}, {"displayName": "GPT-4 32k 0613", "name": "gpt-4-32k-0613"}]
# OPENAI_API_LOGLEVEL=debug

API_PORT=5010
WEB_PORT=8080
SNAKEMQ_PORT=8765

NO_INTERNET_AVAILABLE=1

SESSION_ENCRYPTION_KEY="67ed8ea0-05f0-4086-9a54-6b2bb6dbcf29"

DEBUG=1

FOUNDRY_DATA_FOLDER="<YOUR FOUNDRY DATA FOLDER>"
```
Then call
```
# build the frontend and inject it into the main application, you will need Node.js and Vite to be installed for this
make compile_frontend

# the following only required on recent MacOS, see https://stackoverflow.com/a/52230415/10984529
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# finally, run all required services
python gpt_code_ui/main.py
```
This should open a browser window, navigating you to [http://localhost:8080](http://localhost:8080), where the application is running.

### Configurables
Set the `API_PORT`, `WEB_PORT`, `SNAKEMQ_PORT` variables to override the defaults.
When `NO_INTERNET_AVAILABLE` is non-trueish or absent, the application will create dedicated virtual environments for every session and also makes active use of `!pip install ...` commands for missing packages.

## Contributing
Please contribute.


Thank you for your interest in this project!
