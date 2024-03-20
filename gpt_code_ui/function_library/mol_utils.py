from typing import List

from IPython.display import display
from rdkit import Chem
from rdkit.Chem import Draw


def draw_smiles(smiles_list: List[str], legends: List[str] = None, mols_per_row: int = 5) -> None:
    """Draw a list of SMILES strings.

    Args:
        smiles_list (List[str]): A list of SMILES strings.
        legends (List[str], optional): A list of legend strings. Defaults to None.
        mols_per_row (int, optional): Number of molecules per row. Defaults to 5.
    """
    mols = Draw.MolsToGridImage(
        [Chem.MolFromSmiles(smiles) for smiles in smiles_list],
        molsPerRow=mols_per_row,
        legends=legends,
        useSVG=True,
    )

    display(mols)
