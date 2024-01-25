
# gpt-code-ui-deploy
=======
# OpenAI's ChatGPT Code Interpreter

This is an open-source implementation of OpenAI's ChatGPT Code interpreter. This tool allows you to ask the OpenAI model to execute specific tasks, and it will automatically generate and run the code for you【9†source】.

## Installation

To install, open a terminal and run the following commands:

```bash
cp .env.example .env
make compile_frontend
pip install gpt-code-ui
gpt-code
```
The `.env` file in your working directory can be used to load the `OPENAI_API_KEY` environment variable【13†source】.

## Features

The tool includes a variety of features:

- File upload
- File download
- Context awareness (it can refer to your previous messages)
- Generate code
- Run code (Python kernel)
- Model switching (GPT-3.5 and GPT-4)【18†source】

## Configuration

You can override the default settings by modifying the following environment variables:

- `API_PORT`
- `WEB_PORT`
- `SNAKEMQ_PORT`
- `OPENAI_BASE_URL` (Change the OpenAI API endpoint that's being used)【20†source】

## Docker Version

A Docker container version of the Python package is also available. It's bundled and maintained by `localagi` and can be found at: `gpt-code-ui-docker`【21†source】.

To run the Docker version, follow these steps:

1. Ensure `docker` and `docker compose` are available on your system.
2. Get `docker-compose.yml`.
3. Update `OPENAI_API_KEY` in this file.
4. Run `docker compose up` from the same directory.
5. Open `http://localhost:8080` in your web browser【29†source】.

You can also set the `GPTCODEUI_VERSION` environment variable to select a specific version. For example, use `GPTCODEUI_VERSION=0.42.14` to use version 0.42.14【30†source】.

# GPT-Code-UI-PRD Deployment Guide

Welcome to the GPT-Code-UI-PRD project, an open-source implementation of OpenAI's ChatGPT Code interpreter. This project provides a user-friendly interface for interacting with the OpenAI GPT-4 model in real-time, making the most of its AI capabilities to generate human-like text. The project is deployed on an Amazon Web Services (AWS) EC2 instance.

## Amazon EC2 Instance Details

- **Instance ID:** i-0066c20259db97c42 (gpt-code-ui-prd)
- **Public IPv4 address:** 3.88.160.99
- **Private IPv4 addresses:** 13.0.101.251
- **Public IPv4 DNS:** ec2-3-88-160-99.compute-1.amazonaws.com
- **Hostname type:** IP name: ip-13-0-101-251.ec2.internal
- **Private IP DNS name (IPv4 only):** ip-13-0-101-251.ec2.internal
- **Instance type:** t3a.medium 

The project's frontend is built using React and the backend services are deployed on the specified AWS EC2 instance. This allows both developers and non-developers to create content, test hypotheses, generate code, and perform other creative writing tasks.

## Connection Guide

### Pre-Requisites

- AWS CLI installed and configured on your machine.
- Proper permissions to access and manage EC2 instances.
- .pem file (private key file) associated with this instance.

### Connect to the Instance

1. Open your terminal.
2. Use the `ssh` command:

```bash
ssh -i /path/to/your/key.pem ec2-user@ec2-3-88-160-99.compute-1.amazonaws.com
```

Replace `/path/to/your/key.pem` with the actual path to your .pem file.

### Alternative Connection Method: EC2 Instance Connect

AWS EC2 Instance Connect provides a secure method to connect to your instances.

1. Use the `aws ec2-instance-connect` command:

```bash
aws ec2-instance-connect send-ssh-public-key --instance-id i-0066c20259db97c42 --availability-zone us-east-1a --instance-os-user ec2-user --ssh-public-key file:///path/to/your/id_rsa.pub
```

Replace `/path/to/your/id_rsa.pub` with the actual path to your public key file.

2. After sending your SSH public key, use the `ssh` command:

```bash
ssh ec2-user@ec2-3-88-160-99.compute-1.amazonaws.com
```

## Configurations

You can modify several configuration variables:

- Set the `API_PORT`, `WEB_PORT`, `SNAKEMQ_PORT` to override the defaults.
- Set `OPENAI_BASE_URL` to change the OpenAI API endpoint that's being used (note this environment variable includes the `https://` protocol).

## Troubleshooting

If you're unable to connect, please:

- Check your internet connection.
- Confirm your permissions.
- Verify the location and access rights of your .pem file.
- Ensure the EC2 instance is running.

## Additional Resources

- [AWS CLI User Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- [AWS EC2 User Guide for Linux Instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html)
- [Connect to your instance using EC2 Instance Connect](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Connect-using-EC2-Instance-Connect.html?icmpid=docs_ec2_console)

