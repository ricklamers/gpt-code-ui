import asyncio

import streamlit as st

from gpt_code_ui.webapp.main import AVAILABLE_MODELS
from gpt_code_ui.webapp.main import ChatHistory
from gpt_code_ui.webapp.main import get_code
from gpt_code_ui.webapp.prompts import SYSTEM_PROMPT


def is_initialized():
    return "initalized" in st.session_state and st.session_state["initalized"]


def reset_state():
    st.session_state["initalized"] = True
    st.session_state["chat_history"] = ChatHistory()


def init():
    if not is_initialized():
        reset_state()


init()


def get_parameters() -> dict:
    model = st.sidebar.selectbox(
        "Model",
        options=AVAILABLE_MODELS,
        format_func=lambda model: model["displayName"],
    )

    return {"model": model["name"]}


st.set_page_config(
    page_title="MoleculeMate / CodeImpact prompting playground",
    page_icon="🧪",
)
st.header("MoleculeMate / CodeImpact prompting playground")
parameters = get_parameters()

system_prompt = st.text_area("System Prompt", SYSTEM_PROMPT, height=300)


chat_history: ChatHistory = st.session_state["chat_history"]
messages: list[dict] = chat_history(override_system_prompt=system_prompt)

for message in messages[1:]:
    with st.chat_message(name=message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("User input")
if user_input:
    chat_history.add_prompt(user_input)
    messages = chat_history(override_system_prompt=system_prompt)
    code, text, status = asyncio.run(get_code(messages=messages, model=parameters["model"]))
    chat_history.add_answer(text)
    st.rerun()

if st.sidebar.button("Clear chat history"):
    reset_state()
    st.rerun()
