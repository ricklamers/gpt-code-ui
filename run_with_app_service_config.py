import os
import sys
import json
import subprocess

try:
    config = json.loads(os.environ["APP_SERVICE_CONFIG"])
except KeyError:
    config = json.load(open('.app_service_config.json'))

sub_env = os.environ.copy()

for key, value in config.items():
    if isinstance(value, str):
        if value.startswith('$'):
            try:
                value = os.environ[value[1:]]
            except KeyError:
                print(f'Failed to resolve environment variable {value}. Keepting the reference in the env.')

        sub_env[key] = value
    elif isinstance(value, int):
        sub_env[key] = str(value)
    else:
        sub_env[key] = json.dumps(value)

sub_env['PYTHONUNBUFFERED'] = '1'

if len(sys.argv) > 1:
    args = sys.argv[1:]
else:
    args = ['./gpt_code_ui/main.py']

subprocess.run([sys.executable] + args, env=sub_env)
