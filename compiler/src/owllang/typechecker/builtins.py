"""
OwlLang Built-in Functions Registry

Centralizes all built-in function definitions in one place.
This makes it easy to:
- Add new built-ins
- Ensure typechecker and transpiler are in sync
- Document available functions

Each built-in defines:
- Type signature (for typechecker)
- Transpilation pattern (for transpiler)
- Documentation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .types import (
    OwlType, INT, FLOAT, STRING, BOOL, VOID, ANY,
    ListType, OptionType,
)


@dataclass(frozen=True)
class BuiltinFunction:
    """
    Definition of a built-in function.
    
    Attributes:
        name: Function name as used in OwlLang
        param_types: Expected parameter types (use ANY for polymorphic)
        return_type: Return type (can be a callable for generic returns)
        transpile_template: Python code template or callable
        doc: Documentation string
        generic_return: If True, return_type is computed from arguments
    """
    name: str
    param_types: tuple[OwlType, ...]
    return_type: OwlType
    transpile_template: str | None  # None means special handling required
    doc: str
    generic_return: bool = False


# =============================================================================
# Built-in Function Definitions
# =============================================================================

BUILTIN_FUNCTIONS: dict[str, BuiltinFunction] = {}


def _register(fn: BuiltinFunction) -> BuiltinFunction:
    """Register a built-in function."""
    BUILTIN_FUNCTIONS[fn.name] = fn
    return fn


# I/O Functions
_register(BuiltinFunction(
    name="print",
    param_types=(ANY,),
    return_type=VOID,
    transpile_template="print({0})",
    doc="Print a value to stdout.",
))

# List Functions
_register(BuiltinFunction(
    name="len",
    param_types=(ListType(ANY),),
    return_type=INT,
    transpile_template="len({0})",
    doc="Return the length of a list.",
))

_register(BuiltinFunction(
    name="is_empty",
    param_types=(ListType(ANY),),
    return_type=BOOL,
    transpile_template="len({0}) == 0",
    doc="Return True if the list is empty.",
))

_register(BuiltinFunction(
    name="get",
    param_types=(ListType(ANY), INT),
    return_type=ANY,  # Actual type computed from list element type
    transpile_template="{0}[{1}]",
    doc="Get element at index from list.",
    generic_return=True,
))

_register(BuiltinFunction(
    name="push",
    param_types=(ListType(ANY), ANY),
    return_type=ListType(ANY),  # Returns new list with same element type
    transpile_template="{0} + [{1}]",
    doc="Return a new list with element appended.",
    generic_return=True,
))

# Range Function
_register(BuiltinFunction(
    name="range",
    param_types=(INT, INT),
    return_type=ListType(INT),
    transpile_template="range({0}, {1})",
    doc="Create a range from start to end (exclusive).",
))


# =============================================================================
# Type Constructors (Option/Result)
# =============================================================================

@dataclass(frozen=True)
class TypeConstructor:
    """
    Definition of a type constructor (Some, None, Ok, Err).
    
    These are not regular functions - they create values of algebraic types.
    """
    name: str
    param_count: int  # Number of arguments (0 for None)
    creates_type: str  # "Option" or "Result"
    doc: str


TYPE_CONSTRUCTORS: dict[str, TypeConstructor] = {
    "Some": TypeConstructor(
        name="Some",
        param_count=1,
        creates_type="Option",
        doc="Create an Option containing a value.",
    ),
    "None": TypeConstructor(
        name="None",
        param_count=0,
        creates_type="Option",
        doc="Create an empty Option.",
    ),
    "Ok": TypeConstructor(
        name="Ok",
        param_count=1,
        creates_type="Result",
        doc="Create a successful Result.",
    ),
    "Err": TypeConstructor(
        name="Err",
        param_count=1,
        creates_type="Result",
        doc="Create an error Result.",
    ),
}


# =============================================================================
# Query Functions
# =============================================================================

def is_builtin_function(name: str) -> bool:
    """Check if a name is a built-in function."""
    return name in BUILTIN_FUNCTIONS


def is_type_constructor(name: str) -> bool:
    """Check if a name is a type constructor."""
    return name in TYPE_CONSTRUCTORS


def get_builtin(name: str) -> BuiltinFunction | None:
    """Get a built-in function by name."""
    return BUILTIN_FUNCTIONS.get(name)


def get_type_constructor(name: str) -> TypeConstructor | None:
    """Get a type constructor by name."""
    return TYPE_CONSTRUCTORS.get(name)
