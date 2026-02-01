"""
OwlLang Type System - Phase 2

Defines all types used by the type checker:
- Primitive types: Int, Float, String, Bool, Void
- Special types: Any, Unknown
- Generic types: Option[T], Result[T, E]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Base Type
# =============================================================================

@dataclass(frozen=True)
class OwlType:
    """Base type representation."""
    name: str
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OwlType):
            return NotImplemented
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


# =============================================================================
# Primitive Types
# =============================================================================

INT = OwlType("Int")
FLOAT = OwlType("Float")
STRING = OwlType("String")
BOOL = OwlType("Bool")
VOID = OwlType("Void")

# Special types
UNKNOWN = OwlType("Unknown")  # For unresolved types
ANY = OwlType("Any")  # For Python interop


# =============================================================================
# Generic Types: Option[T] and Result[T, E]
# =============================================================================

@dataclass(frozen=True)
class OptionType(OwlType):
    """
    Option[T] type - represents an optional value.
    
    - Some(x) -> Option[type(x)]
    - None -> Option[Any]
    """
    inner: OwlType
    
    def __init__(self, inner: OwlType) -> None:
        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, 'name', f"Option[{inner}]")
        object.__setattr__(self, 'inner', inner)
    
    def __str__(self) -> str:
        return f"Option[{self.inner}]"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, OptionType):
            # Option[Any] is compatible with any Option[T]
            if self.inner == ANY or other.inner == ANY:
                return True
            return self.inner == other.inner
        return False
    
    def __hash__(self) -> int:
        return hash(("Option", self.inner))


@dataclass(frozen=True)
class ResultType(OwlType):
    """
    Result[T, E] type - represents a success or error value.
    
    - Ok(x) -> Result[type(x), Any]
    - Err(e) -> Result[Any, type(e)]
    """
    ok_type: OwlType
    err_type: OwlType
    
    def __init__(self, ok_type: OwlType, err_type: OwlType) -> None:
        object.__setattr__(self, 'name', f"Result[{ok_type}, {err_type}]")
        object.__setattr__(self, 'ok_type', ok_type)
        object.__setattr__(self, 'err_type', err_type)
    
    def __str__(self) -> str:
        return f"Result[{self.ok_type}, {self.err_type}]"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, ResultType):
            # Check ok_type compatibility (ANY matches anything)
            ok_match = (
                self.ok_type == ANY or 
                other.ok_type == ANY or 
                self.ok_type == other.ok_type
            )
            # Check err_type compatibility
            err_match = (
                self.err_type == ANY or 
                other.err_type == ANY or 
                self.err_type == other.err_type
            )
            return ok_match and err_match
        return False
    
    def __hash__(self) -> int:
        return hash(("Result", self.ok_type, self.err_type))


@dataclass(frozen=True)
class ListType(OwlType):
    """
    List[T] type - represents a list of values of type T.
    
    - [1, 2, 3] -> List[Int]
    - ["a", "b"] -> List[String]
    - [] -> List[Any] (empty list, type determined by context)
    """
    element_type: OwlType
    
    def __init__(self, element_type: OwlType) -> None:
        object.__setattr__(self, 'name', f"List[{element_type}]")
        object.__setattr__(self, 'element_type', element_type)
    
    def __str__(self) -> str:
        return f"List[{self.element_type}]"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, ListType):
            # List[Any] is compatible with any List[T]
            if self.element_type == ANY or other.element_type == ANY:
                return True
            return self.element_type == other.element_type
        return False
    
    def __hash__(self) -> int:
        return hash(("List", self.element_type))


# =============================================================================
# Type Utilities
# =============================================================================

def parse_type(type_str: str) -> OwlType:
    """
    Parse a type annotation string into an OwlType.
    
    Supports:
    - Primitive types: Int, Float, String, Bool, Void
    - Option[T]: Option[Int], Option[String], etc.
    - Result[T, E]: Result[Int, String], etc.
    """
    type_str = type_str.strip()
    
    # Primitive types
    primitives = {
        "int": INT, "Int": INT,
        "float": FLOAT, "Float": FLOAT,
        "str": STRING, "String": STRING,
        "bool": BOOL, "Bool": BOOL,
        "void": VOID, "Void": VOID,
        "Any": ANY,
    }
    
    if type_str in primitives:
        return primitives[type_str]
    
    # Option[T]
    if type_str.startswith("Option[") and type_str.endswith("]"):
        inner_str = type_str[7:-1]  # Extract T from Option[T]
        inner_type = parse_type(inner_str)
        return OptionType(inner_type)
    
    # List[T]
    if type_str.startswith("List[") and type_str.endswith("]"):
        inner_str = type_str[5:-1]  # Extract T from List[T]
        inner_type = parse_type(inner_str)
        return ListType(inner_type)
    
    # Result[T, E]
    if type_str.startswith("Result[") and type_str.endswith("]"):
        inner_str = type_str[7:-1]  # Extract "T, E" from Result[T, E]
        # Find the comma that separates T and E (handle nested generics)
        depth = 0
        comma_pos = -1
        for i, c in enumerate(inner_str):
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
            elif c == ',' and depth == 0:
                comma_pos = i
                break
        
        if comma_pos == -1:
            return UNKNOWN
        
        ok_str = inner_str[:comma_pos].strip()
        err_str = inner_str[comma_pos + 1:].strip()
        ok_type = parse_type(ok_str)
        err_type = parse_type(err_str)
        return ResultType(ok_type, err_type)
    
    return UNKNOWN


def types_compatible(expected: OwlType, actual: OwlType) -> bool:
    """
    Check if two types are compatible for assignment/return.
    
    Rules:
    - ANY is compatible with anything
    - UNKNOWN is compatible with anything (unresolved)
    - Option[T] == Option[T] or Option[Any]
    - Result[T, E] == Result[T, E] with ANY matching anything
    - List[T] == List[T] or List[Any]
    - Primitive types must match exactly
    """
    # ANY and UNKNOWN are wildcards
    if expected == ANY or actual == ANY:
        return True
    if expected == UNKNOWN or actual == UNKNOWN:
        return True
    
    # Both Option types
    if isinstance(expected, OptionType) and isinstance(actual, OptionType):
        return expected == actual  # __eq__ handles ANY
    
    # Both Result types
    if isinstance(expected, ResultType) and isinstance(actual, ResultType):
        return expected == actual  # __eq__ handles ANY
    
    # Both List types
    if isinstance(expected, ListType) and isinstance(actual, ListType):
        return expected == actual  # __eq__ handles ANY
    
    # Same type class
    return expected == actual
