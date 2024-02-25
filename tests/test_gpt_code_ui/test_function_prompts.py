from gpt_code_ui.function_library.examples import generate_derivate_molecules
from gpt_code_ui.function_library.examples import predict_solubility
from gpt_code_ui.webapp.prompts import function_to_prompt
from gpt_code_ui.webapp.prompts import get_system_prompt
from gpt_code_ui.webapp.prompts import SYSTEM_PROMPT_TEMPLATE


_predict_solubility_prompt = '''def predict_solubility(smiles: str) -> float:
    """Predict the solubility of a molecule from its SMILES string.

    Args:
        smiles: SMILES string of the molecule.

    Returns:
        The predicted solubility.
    """
    pass
'''

_generate_derivate_molecules_prompt = '''def generate_derivate_molecules(smiles: str, n: int = 10) -> list[str]:
    """Generate a list of molecules that are similar to the input molecule.

    Args:
        smiles: SMILES string of the molecule.
        n: Number of molecules to generate.

    Returns:
        A list of SMILES strings of molecules that are similar to the input molecule.
    """
    pass
'''


def test_function_prompt():
    prompt = function_to_prompt(predict_solubility)
    assert prompt == _predict_solubility_prompt

    prompt = function_to_prompt(generate_derivate_molecules)
    assert prompt == _generate_derivate_molecules_prompt


def test_system_prompt():
    prompt = get_system_prompt(
        template=SYSTEM_PROMPT_TEMPLATE,
        functions=[predict_solubility, generate_derivate_molecules],
    )
    assert _predict_solubility_prompt in prompt
    assert _generate_derivate_molecules_prompt in prompt

    # test with defaults
    prompt = get_system_prompt()
    assert _predict_solubility_prompt in prompt
    assert _generate_derivate_molecules_prompt in prompt
