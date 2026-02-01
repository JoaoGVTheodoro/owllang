"""
OwlLang AST (Abstract Syntax Tree)

This module defines all node types for the OwlLang language.
The AST is the core data structure that represents parsed code.

Structure:
    - Token/TokenType: Lexical tokens
    - Expr subclasses: Expression nodes
    - Stmt subclasses: Statement nodes  
    - FnDecl, Program: Top-level declarations

All nodes support optional Span for source location tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from ..diagnostics.span import Span


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
    MUT = auto()  # mut (mutable)
    WHILE = auto()  # while
    FROM = auto()
    PYTHON = auto()
    IMPORT = auto()
    AS = auto()
    IF = auto()
    ELSE = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    MATCH = auto()

    # Operators
    PLUS = auto()  # +
    MINUS = auto()  # -
    STAR = auto()  # *
    SLASH = auto()  # /
    PERCENT = auto()  # %
    EQ = auto()  # ==
    NE = auto()  # !=
    LT = auto()  # <
    GT = auto()  # >
    LE = auto()  # <=
    GE = auto()  # >=
    ASSIGN = auto()  # =

    # Delimiters
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()  # ,
    COLON = auto()  # :
    ARROW = auto()  # ->
    FAT_ARROW = auto()  # =>
    DOT = auto()  # .
    QUESTION = auto()  # ?

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
    
    def span(self, filename: str = "<unknown>") -> Span:
        """Create a Span from this token's position."""
        from ..diagnostics.span import Span
        return Span.from_token(self.line, self.column, self.value, filename)


# =============================================================================
# AST Node Types - Expressions
# =============================================================================


@dataclass
class Expr:
    """Base class for all expression nodes."""

    pass


@dataclass
class IntLiteral(Expr):
    """Integer literal: 42"""

    value: int
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class FloatLiteral(Expr):
    """Float literal: 3.14"""

    value: float
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class StringLiteral(Expr):
    """String literal: "hello" """

    value: str
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class BoolLiteral(Expr):
    """Boolean literal: true, false"""

    value: bool
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class Identifier(Expr):
    """Variable reference: x, my_var"""

    name: str
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class BinaryOp(Expr):
    """Binary operation: a + b, x == y"""

    left: Expr
    operator: str  # '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>='
    right: Expr
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class UnaryOp(Expr):
    """Unary operation: -x, !flag"""

    operator: str  # '-', '!'
    operand: Expr
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class Call(Expr):
    """Function call: print(x), math.sqrt(4)"""

    callee: Expr  # Can be Identifier or FieldAccess
    arguments: list[Expr]
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class FieldAccess(Expr):
    """Field/attribute access: math.pi, obj.method"""

    object: Expr
    field: str
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class TryExpr(Expr):
    """
    Try operator: expr?
    
    Used for Result error propagation.
    If expr is Ok(x), evaluates to x.
    If expr is Err(e), returns Err(e) from the current function.
    """

    operand: Expr
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class Pattern:
    """Base class for match patterns."""
    pass


@dataclass
class SomePattern(Pattern):
    """Pattern: Some(binding)"""
    binding: str
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class NonePattern(Pattern):
    """Pattern: None"""
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class OkPattern(Pattern):
    """Pattern: Ok(binding)"""
    binding: str
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class ErrPattern(Pattern):
    """Pattern: Err(binding)"""
    binding: str
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class MatchArm:
    """
    A single arm in a match expression.
    
    pattern => body
    """
    pattern: Pattern
    body: Expr
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class MatchExpr(Expr):
    """
    Match expression for pattern matching.
    
    match expr {
        Some(x) => x,
        None => 0,
    }
    """
    subject: Expr
    arms: list[MatchArm]
    span: Optional[Span] = field(default=None, compare=False)


# =============================================================================
# AST Node Types - Type Annotations
# =============================================================================


@dataclass
class TypeAnnotation:
    """
    Type annotation node for parameterized types.
    
    Examples:
        - Simple: Int, String, Bool
        - Parameterized: Option[Int], Result[Int, String]
    """

    name: str
    params: list[TypeAnnotation] = field(default_factory=list)
    span: Optional[Span] = field(default=None, compare=False)

    def to_string(self) -> str:
        """Convert type annotation to string representation."""
        if not self.params:
            return self.name
        param_strs = ", ".join(p.to_string() for p in self.params)
        return f"{self.name}[{param_strs}]"


# =============================================================================
# AST Node Types - Statements
# =============================================================================


@dataclass
class Stmt:
    """Base class for all statement nodes."""

    pass


@dataclass
class LetStmt(Stmt):
    """Variable declaration: let x = 10 or let mut x = 10"""

    name: str
    value: Expr
    type_annotation: Optional[TypeAnnotation] = None
    mutable: bool = False  # True for 'let mut'
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class AssignStmt(Stmt):
    """Assignment to mutable variable: x = 20"""

    name: str
    value: Expr
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class ExprStmt(Stmt):
    """Expression as statement: print(x)"""

    expr: Expr
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class ReturnStmt(Stmt):
    """Return statement: return x + y"""

    value: Optional[Expr] = None
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class WhileStmt(Stmt):
    """While loop: while condition { body }"""

    condition: Expr
    body: list[Stmt]
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class IfStmt(Stmt):
    """If statement: if x > 0 { ... } else { ... }"""

    condition: Expr
    then_body: list[Stmt]
    else_body: Optional[list[Stmt]] = None
    span: Optional[Span] = field(default=None, compare=False)


# =============================================================================
# Top-Level Declarations
# =============================================================================


@dataclass
class Parameter:
    """Function parameter: name: Type"""

    name: str
    type_annotation: Optional[TypeAnnotation] = None
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class FnDecl:
    """Function declaration: fn add(a, b) { ... }"""

    name: str
    params: list[Parameter]
    body: list[Stmt]
    return_type: Optional[TypeAnnotation] = None
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class PythonImport:
    """Python import: from python import math"""

    module: str
    alias: Optional[str] = None
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class PythonFromImport:
    """Python from import: from python.os.path import join, exists"""

    module: str
    names: list[tuple[str, Optional[str]]]  # List of (name, alias) tuples
    span: Optional[Span] = field(default=None, compare=False)


@dataclass
class Program:
    """Root AST node containing the entire program."""

    imports: list[PythonImport | PythonFromImport]
    functions: list[FnDecl]
    statements: list[Stmt]  # Top-level statements (script mode)
    span: Optional[Span] = field(default=None, compare=False)
