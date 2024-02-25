import json
import os

import openai
import requests
from dotenv import load_dotenv

load_dotenv(".env")


def get_available_models():
    available_models = os.environ.get(
        "AVAILABLE_MODELS",
        json.dumps(
            [
                {"displayName": "GPT-3.5 16k", "name": "openai/gpt-35-turbo-16k"},
                {"displayName": "GPT-3.5 0613", "name": "openai/gpt-35-turbo-0613"},
            ]
        ),
    )

    try:
        return json.loads(available_models)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"List of available models is not a valid JSON, check environment variable AVAILABLE_MODELS: {available_models}."
        ) from e


def call(messages, model: str = "openai/gpt-3.5-turbo"):
    vendor = "openai"
    if (sep := model.find("/")) > -1:
        vendor = model[:sep]
        model = model[sep + 1 :]

    # ############ Azure / OpenAI ##############
    if vendor in ("openai", "azure"):
        if vendor == "azure":
            client = openai.AzureOpenAI(
                azure_endpoint=os.environ["AZURE_API_BASE"],
                api_key=os.environ["AZURE_API_KEY"],
                api_version=os.environ.get("AZURE_API_VERSION", None),
            )
        else:
            client = openai.OpenAI(
                api_key=os.environ["OPENAI_API_KEY"],
            )

        arguments = dict(
            temperature=0.7,
            messages=messages,
        )

        try:
            result_GPT = client.chat.completions.create(
                model=model,
                **arguments,
            )

            if hasattr(result_GPT, "error") and result_GPT.error is not None:
                raise RuntimeError(f"Error: {result_GPT.error['code']}, Message: {result_GPT.error['message']}")

            if result_GPT.choices is None:
                raise RuntimeError(f"Malformed answer from API: {result_GPT}")

            if result_GPT.choices[0].finish_reason == "content_filter":
                raise RuntimeError("Content Filter")

        except openai.OpenAIError as e:
            raise RuntimeError(f"Error from API: {e}") from e

        try:
            return result_GPT.choices[0].message.content
        except AttributeError as e:
            raise RuntimeError(f"Malformed answer from API: {result_GPT}") from e

    # ###### Bedrock behind a very simple gateway (NOT the actual Bedrock API) ######
    elif vendor == "bedrock_gateway":
        if (sep := model.find(".")) > -1:
            base_vendor = model[:sep]

            if base_vendor == "anthropic":
                ROLE_MAP = {
                    "system": "",
                    "user": "\n\nHuman: ",
                    "assistant": "\n\nAssistant: ",
                }

                arguments = dict(
                    temperature=0.7,
                    max_tokens_to_sample=4000,
                    prompt="".join((ROLE_MAP[m["role"]] + m["content"]) for m in messages) + ROLE_MAP["assistant"],
                )
            else:
                raise RuntimeError(f"Unsupported bedrock base vendor: {base_vendor}")

            response = requests.request(
                method="POST",
                url=f"{os.environ['BEDROCK_GATEWAY_API_BASE']}/{model}/invoke",
                headers={"x-api-key": os.environ["BEDROCK_GATEWAY_API_KEY"]},
                data=json.dumps(arguments),
            )

            return response.json()["completion"]
        else:
            raise RuntimeError(f"Malformed bedrock model ID: {model}. Expected format 'BASE_VENDOR.MODEL'.")

    # ############ Others ##############
    else:
        raise RuntimeError(f"Unsupported vendor {vendor} with model {model} requested.")
