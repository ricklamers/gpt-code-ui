from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gpt_code_ui",
    version="0.42.40",
    description="An Open Source version of ChatGPT Code Interpreter",
    long_description=long_description,
    long_description_content_type="text/markdown",  # This field specifies the format of the `long_description`.
    packages=find_packages(),
    package_data={"gpt_code_ui.webapp": ["static/*", "static/assets/*"]},
    install_requires=[
        "ipykernel>=6,<7",
        "snakemq>=1,<2",
        "requests>=2,<3",
        "Flask>=2,<3",
        "Flask-Cors>=3,<4",
        "foundry-dev-tools>=1.3",
        "python-dotenv>=0.18,<2",
        "pandas>=1.3,<2",
        "openai>=1.0.0,<2",
    ],
    entry_points={
        "console_scripts": [
            "gptcode = gpt_code_ui.main:main",
        ],
    },
)
