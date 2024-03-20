import types
from typing import Any, Callable, Dict, List

from gpt_code_ui.function_library import AVAILABLE_FUNCTIONS
from gpt_code_ui.function_library.parser import get_function_signature, is_empty_annotation, is_empty_default
from gpt_code_ui.kernel_program.config import NO_INTERNET_AVAILABLE

SYSTEM_PROMPT_TEMPLATE = """Write Python code, in a triple backtick Markdown code block, that answers the user prompts.

Notes:
    First, think step by step what you want to do and write it down in English.
    Then generate valid Python code in a single code block.
    Make sure all code is valid - it will Be run in a Jupyter Python 3 kernel environment.
    Define every variable before you use it.
    For data processing, you can use
        'numpy', # numpy==1.24.3
        'dateparser' #dateparser==1.1.8
        'pandas', # matplotlib==1.5.3
        'geopandas', # geopandas==0.13.2
        'tabulate', # tabulate==0.9.0
        'scipy', # scipy==1.11.1
        'scikit-learn', # scikit-learn==1.3.0
        'WordCloud', # wordcloud==1.9.3"
    For pdf extraction, you can use
        'PyPDF2', # PyPDF2==3.0.1
        'pdfminer', # pdfminer==20191125
        'pdfplumber', # pdfplumber==0.9.0
    For data visualization, you can use
        'matplotlib', # matplotlib==3.7.1
    For chemistry related tasks, you can use
        'rdkit', # rdkit>=2023.3.3
    For 3D visualizations of molecules (e.g. from file formats 'pdb', 'sdf', 'xyz', 'pqr', 'cub', or 'mol2'), you can use
        'py3Dmol', # py3Dmol==2.0.4

    { f'''In addition you can use the following functions. DO NOT REDEFINE THEM:
{functions}''' if functions else '' }

    Be sure to generate charts with matplotlib. If you need geographical charts, use geopandas with the geopandas.datasets module.
    Do not set or modify matplotlib fonts. Instead assume that fonts are selected automatically as needed.
    For 3D visualizations of SMILEs strings, you need to use rdkit to convert them to a Mol block first as the `addModel` function of py3Dmol does not suport SMILEs strings directly.
    {  'Do not try to install additional packages as no internet connection is available. Do not include any "!pip install PACKAGE" commands.' if NO_INTERNET_AVAILABLE else
       'If an additional package is required, you can add the corresponding "!pip install PACKAGE" call to the beginning of the code.'  }
    If the user requests to generate a table, produce code that prints a markdown table.
    If the user has just uploaded a file, focus on the file that was most recently uploaded (and optionally all previously uploaded files)
    If the code modifies or produces a file, at the end of the code block insert a print statement that prints a link to it as HTML string: <a href='/download?file=INSERT_FILENAME_HERE'>Download file</a>. Replace INSERT_FILENAME_HERE with the actual filename.
    Do not use your own knowledge to answer the user prompt. Instead, focus on generating Python code for doing so."""


def format_prompt(template: str, variables: Dict[str, Any]) -> str:
    """Formats a prompt string.

    Args:
        template (str): The template string.
        variables (Dict): The variables to insert into the template.

    Returns:
        The formatted prompt string.
    """

    _globals = {
        "NO_INTERNET_AVAILABLE": NO_INTERNET_AVAILABLE,
    }

    # Might be a security risk, so only use trusted templates
    return eval(f'f"""{template}"""', _globals, variables)  # noqa: W0123


def get_system_prompt(template: str = SYSTEM_PROMPT_TEMPLATE, functions: List[Callable] = None) -> str:
    """Gets the system prompt.

    Args:
        template (str, optional): The template to use. Defaults to SYSTEM_PROMPT_TEMPLATE.
        functions (List[Callable], optional): The functions to include in the prompt. Defaults to None.

    Returns:
        The system prompt.
    """

    if functions is None:
        functions = list(AVAILABLE_FUNCTIONS.values())

    function_prompts = [function_to_prompt(fun) for fun in functions]
    function_prompts_str = "\n".join(function_prompts)

    return format_prompt(
        template,
        {
            "functions": function_prompts_str,
        },
    )


def type_to_string(t: type) -> str:
    """Converts a type to a string.

    Args:
        t (type): The type to convert.

    Returns:
        A string representation of the type.
    """

    if isinstance(t, types.GenericAlias) or t is None:
        return str(t)
    else:
        return t.__name__


def function_to_prompt(fun: Callable) -> str:
    """Converts a function into a prompt string.

    Args:
        fun (Callable): The function to convert.

    Returns:
        A prompt string.
    """

    signature = get_function_signature(fun)

    # TODO (TP): Write JINJA2 template for function prompt
    parameter_strs = []
    for parameter in signature.parameters:
        s = f"{parameter.name}: {type_to_string(parameter.type)}"
        if not is_empty_default(parameter.default):
            s += f" = {parameter.default}"
        parameter_strs.append(s)

    parameter_str = ", ".join(parameter_strs)
    return_type_str = (
        type_to_string(signature.return_type) if not is_empty_annotation(signature.return_type) else "None"
    )
    output = f'''def {signature.name}({parameter_str}) -> {return_type_str}:
    """{signature.doc_string}"""
    pass
'''
    return output
