from gpt_code_ui.webapp.prompts import type_to_string


def test_type_to_string():
    # test simple types
    assert type_to_string(int) == "int"
    assert type_to_string(str) == "str"
    assert type_to_string(float) == "float"

    # test generic types
    assert type_to_string(list[int]) == "list[int]"
    assert type_to_string(list[str]) == "list[str]"

    # test None
    assert type_to_string(None) == "None"
