"""
OwlLang AST (Abstract Syntax Tree)

Define all node types for the OwlLang MVP.
This is the core data structure that represents parsed code.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum, auto


# =============================================================================
# Token Types (used by Lexer)
# =============================================================================

class TokenType(Enum):
    """All token types recognized by the lexer."""
    
    # Literals
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    
    # Identifiers and Keywords
    IDENT = auto()
    FN = auto()
    LET = auto()
    FROM = auto()
    PYTHON = auto()
    IMPORT = auto()
    AS = auto()
    IF = auto()
    ELSE = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    PERCENT = auto()     # %
    EQ = auto()          # ==
    NE = auto()          # !=
    LT = auto()          # <
    GT = auto()          # >
    LE = auto()          # <=
    GE = auto()          # >=
    ASSIGN = auto()      # =
    
    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    COMMA = auto()       # ,
    COLON = auto()       # :
    ARROW = auto()       # ->
    DOT = auto()         # .
    
    # Special
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    """A single token from the source code."""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


# =============================================================================
# AST Node Types
# =============================================================================

# Base class for all expressions
@dataclass
class Expr:
    """Base class for all expression nodes."""
    pass


@dataclass
class IntLiteral(Expr):
    """Integer literal: 42"""
    value: int


@dataclass
class FloatLiteral(Expr):
    """Float literal: 3.14"""
    value: float


@dataclass
class StringLiteral(Expr):
    """String literal: "hello" """
    value: str


@dataclass
class BoolLiteral(Expr):
    """Boolean literal: true, false"""
    value: bool


@dataclass
class Identifier(Expr):
    """Variable reference: x, my_var"""
    name: str


@dataclass
class BinaryOp(Expr):
    """Binary operation: a + b, x == y"""
    left: Expr
    operator: str  # '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>='
    right: Expr


@dataclass
class UnaryOp(Expr):
    """Unary operation: -x, !flag"""
    operator: str  # '-', '!'
    operand: Expr


@dataclass
class Call(Expr):
    """Function call: print(x), math.sqrt(4)"""
    callee: Expr  # Can be Identifier or FieldAccess
    arguments: List[Expr]


@dataclass
class FieldAccess(Expr):
    """Field/attribute access: math.pi, obj.method"""
    object: Expr
    field: str


# =============================================================================
# Statement Node Types
# =============================================================================

@dataclass
class Stmt:
    """Base class for all statement nodes."""
    pass


@dataclass
class LetStmt(Stmt):
    """Variable declaration: let x = 10"""
    name: str
    value: Expr
    type_annotation: Optional[str] = None  # Future: type checking


@dataclass
class ExprStmt(Stmt):
    """Expression as statement: print(x)"""
    expr: Expr


@dataclass
class ReturnStmt(Stmt):
    """Return statement: return x + y"""
    value: Optional[Expr]


@dataclass
class IfStmt(Stmt):
    """If statement: if x > 0 { ... } else { ... }"""
    condition: Expr
    then_body: List[Stmt]
    else_body: Optional[List[Stmt]]


# =============================================================================
# Top-Level Declarations
# =============================================================================

@dataclass
class Parameter:
    """Function parameter: name: Type"""
    name: str
    type_annotation: Optional[str] = None


@dataclass
class FnDecl:
    """Function declaration: fn add(a, b) { ... }"""
    name: str
    params: List[Parameter]
    body: List[Stmt]
    return_type: Optional[str] = None


@dataclass
class PythonImport:
    """Python import: from python import math"""
    module: str
    alias: Optional[str] = None


@dataclass 
class PythonFromImport:
    """Python from import: from python.os.path import join, exists"""
    module: str
    names: List[tuple]  # List of (name, alias) tuples


# =============================================================================
# Program (Root Node)
# =============================================================================

@dataclass
class Program:
    """Root AST node containing the entire program."""
    imports: List[Union[PythonImport, PythonFromImport]]
    functions: List[FnDecl]
    statements: List[Stmt]  # Top-level statements (script mode)
