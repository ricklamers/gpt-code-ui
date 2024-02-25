import inspect
from dataclasses import dataclass
from typing import Type, Any, Callable, List


@dataclass
class Parameter:
    name: str
    type: Type
    default: Any


@dataclass
class FunctionSignature:
    name: str
    doc_string: str | None
    parameters: List[Parameter]
    return_type: Type


def is_empty_default(value: Any) -> bool:
    return value is inspect.Parameter.empty


def is_empty_annotation(value: Any) -> bool:
    return value is inspect.Signature.empty


def get_function_signature(fun: Callable) -> FunctionSignature:
    return FunctionSignature(
        name=fun.__name__,
        doc_string=fun.__doc__,
        parameters=[
            Parameter(name=param.name, type=param.annotation, default=param.default)
            for param in inspect.signature(fun).parameters.values()
        ],
        return_type=fun.__annotations__["return"],
    )
