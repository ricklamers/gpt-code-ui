from setuptools import setup, find_packages

setup(
    name='gpt_code_ui',
    version='0.42.9',
    packages=find_packages(),
    package_data={'gpt_code_ui.webapp': ['static/*', 'static/assets/*']},
    install_requires=[
        'ipykernel>=6,<7',
        'snakemq>=1,<2',
        'requests>=2,<3',
        'Flask>=2,<3',
        'flask-cors>=3,<4',
        'python-dotenv>=1,<2'
    ],
    entry_points={
        'console_scripts': [
            'gptcode = gpt_code_ui.main:main',
        ],
    },
)
