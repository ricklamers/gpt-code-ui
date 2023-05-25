<img src="https://github.com/ricklamers/gpt-code-ui/assets/1309307/9ad4061d-2e26-4407-9431-109b650fb022" alt="GPT-Code logo" width=240 />

An open source implementation of OpenAI's ChatGPT [Code interpreter](https://openai.com/blog/chatgpt-plugins#code-interpreter).

Simply ask the OpenAI model to do something and it will generate & execute the code for you.

Read the [blog post](https://ricklamers.io/posts/gpt-code) to find out more.

## Installation

Open a terminal and run:

```
$ pip install gpt-code-ui
$ gptcode
```

## User interface
<img src="https://github.com/ricklamers/gpt-code-ui/assets/1309307/c29c504a-a7ed-4ae0-9360-d7224bc3e3d6" alt="GPT-Code logo" width="100%" />
 
## Features
- File upload
- File download
- Context awareness (it can refer to your previous messages)
- Generate code
- Run code (Python kernel)
- Model switching (GPT-3.5 and GPT-4)

## Misc.
### Using .env for OpenAI key
You can put a .env in the working directory to load the `OPENAI_API_KEY` environment variable.

Note: Please use the following commands in the terminal to create and edit the `.env` file.

For **Windows** : 

`copy con .env` # Create a new **.env** file.

`notepad.exe .env` # Edit the **.env** file.
                  
For **Linux** :

`nano .env` # Edits the file or creates a new one if not available.


For **MacOS** :

touch `.env` # Creates a new **.env** file.

`nano .env`(Recommended) or `vim .env` # Edits the **.env** file.
           
### Configurables
Set the `API_PORT`, `WEB_PORT`, `SNAKEMQ_PORT` variables to override the defaults.

Set `OPENAI_BASE_URL` to change the OpenAI API endpoint that's being used (note this environment variable includes the protocol `https://...`).

## Contributing
Please do and have a look at the [contributions guide](.github/CONTRIBUTING.md)! This should be a community initiative. I'll try my best to be responsive.
