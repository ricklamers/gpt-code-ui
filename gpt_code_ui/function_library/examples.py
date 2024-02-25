""" A library of example functions that are to be understood by an LLM."""
import random

from rdkit import Chem


def predict_solubility(smiles: str) -> float:
    """Predict the solubility of a molecule from its SMILES string.

    Args:
        smiles: SMILES string of the molecule.

    Returns:
        The predicted solubility.
    """

    # return a random number between 0 and 1
    return random.random()


def generate_derivate_molecules(smiles: str, n: int = 10) -> list[str]:
    """Generate a list of molecules that are similar to the input molecule.

    Args:
        smiles: SMILES string of the molecule.
        n: Number of molecules to generate.

    Returns:
        A list of SMILES strings of molecules that are similar to the input molecule.
    """

    mol = Chem.MolFromSmiles(smiles)
    output = [Chem.MolToSmiles(mol, doRandom=True) for _ in range(n)]
    return output
