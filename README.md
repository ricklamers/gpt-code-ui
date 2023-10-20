<img src="https://github.com/ricklamers/gpt-code-ui/assets/1309307/9ad4061d-2e26-4407-9431-109b650fb022" alt="GPT-Code logo" width=240 />

An open source implementation of OpenAI's ChatGPT [Code interpreter](https://openai.com/blog/chatgpt-plugins#code-interpreter).

Simply ask the OpenAI model to do something and it will generate & execute the code for you.

Read the [blog post](https://ricklamers.io/posts/gpt-code) to find out more.

## User interface
![User Interface](UserInterface.png)
 
## Features
- File upload
- File download
- Dataset Download from Palantir Foundry
- Context awareness (it can refer to your previous messages)
- Generate code
- Run code (Python kernel)
- Model switching (GPT-3.5 and GPT-4)

## Misc.
### Running inside the AppService
See the [Dockerfile](Dockerfile) for details. Most notably, we do not invoke the tool directly but via [run_with_app_service_config.py](rub_with_app_service_config.py), which extracts environment variable specifications from the json-formatted `APP_SERVICE_CONFIG` environment variable.
In order to run properly, your `APP_SERVICE_CONFIG` should read similar to
```
{
  "OPENAI_API_KEY": "33 ... e8",
  "OPENAI_API_BASE": "$APP_SERVICE_NLP_API_URL",
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

  "FOUNDRY_DATA_FOLDER": "/Group Functions/mgf-use-case-gpt-code-ui/data"
}
```

### Running locally
For local execution, your `.env` could read similar to
```
REQUESTS_CA_BUNDLE="/Users/m290886/Projects/technology_repository/merck_cacert_v1.pem"

OPENAI_API_KEY="33 ... e8"
OPENAI_API_BASE="https://mygpt-api.nlp.dev.uptimize.merckgroup.com"
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
```

### Configurables
Set the `API_PORT`, `WEB_PORT`, `SNAKEMQ_PORT` variables to override the defaults.
When `NO_ITNERNET_AVAILABLE` is non-trueish or absent, the application will create dedicated virtual environments for every session and also m,akes active use of `!pip install ...` commands for missing packages.

## Contributing
Please contribute.


Thank you for your interest in this project!
