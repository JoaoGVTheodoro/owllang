"""
OwlLang Type Checker Module

Exports:
- TypeChecker: Main type checking class
- TypeError: Type error representation
- Type definitions: OwlType, INT, FLOAT, STRING, BOOL, VOID, ANY
- Generic types: OptionType, ResultType, ListType
- Type registries: lookup_primitive_type, lookup_parameterized_type
- Built-in functions: BUILTIN_FUNCTIONS, TYPE_CONSTRUCTORS
"""

from .types import (
    OwlType,
    INT,
    FLOAT,
    STRING,
    BOOL,
    VOID,
    UNKNOWN,
    ANY,
    OptionType,
    ResultType,
    ListType,
    parse_type,
    types_compatible,
    # Type registries
    PRIMITIVE_TYPES,
    PARAMETERIZED_TYPES,
    lookup_primitive_type,
    lookup_parameterized_type,
)

from .checker import (
    TypeChecker,
    TypeError,
)

from .builtins import (
    BuiltinFunction,
    TypeConstructor,
    BUILTIN_FUNCTIONS,
    TYPE_CONSTRUCTORS,
    is_builtin_function,
    is_type_constructor,
    get_builtin,
    get_type_constructor,
)

__all__ = [
    # Checker
    "TypeChecker",
    "TypeError",
    # Base types
    "OwlType",
    "INT",
    "FLOAT",
    "STRING",
    "BOOL",
    "VOID",
    "UNKNOWN",
    "ANY",
    # Generic types
    "OptionType",
    "ResultType",
    "ListType",
    # Type registries
    "PRIMITIVE_TYPES",
    "PARAMETERIZED_TYPES",
    "lookup_primitive_type",
    "lookup_parameterized_type",
    # Built-ins
    "BuiltinFunction",
    "TypeConstructor",
    "BUILTIN_FUNCTIONS",
    "TYPE_CONSTRUCTORS",
    "is_builtin_function",
    "is_type_constructor",
    "get_builtin",
    "get_type_constructor",
    # Utilities
    "parse_type",
    "types_compatible",
]
