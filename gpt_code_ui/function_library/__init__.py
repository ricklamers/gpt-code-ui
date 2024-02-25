from typing import Callable, Dict

from .examples import generate_derivate_molecules, predict_solubility

# TODO (TP): Create better, more scalable way to discover functions
AVAILABLE_FUNCTIONS: Dict[str, Callable] = {
    "predict_solubility": predict_solubility,
    "generate_derivate_molecules": generate_derivate_molecules,
}
