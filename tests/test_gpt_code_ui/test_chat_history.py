from gpt_code_ui.webapp.main import ChatHistory


def test_chat_history():
    chat_history = ChatHistory()
    # empty history should only include system message
    messages = chat_history()
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    messages = chat_history(exclude_system=True)
    assert len(messages) == 0

    # add a message
    chat_history.add_prompt("test")
    messages = chat_history()
    assert len(messages) == 2
    assert messages[1]["role"] == "user"

    # get messages with new system message
    messages = chat_history(override_system_prompt="another system message")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "another system message"
