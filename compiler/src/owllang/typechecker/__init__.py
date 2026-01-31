"""
OwlLang Type Checker Module

Exports:
- TypeChecker: Main type checking class
- TypeError: Type error representation
- Type definitions: OwlType, INT, FLOAT, STRING, BOOL, VOID, ANY
- Generic types: OptionType, ResultType
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
    parse_type,
    types_compatible,
)

from .checker import (
    TypeChecker,
    TypeError,
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
    # Utilities
    "parse_type",
    "types_compatible",
]
