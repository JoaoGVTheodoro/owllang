"""
OwlLang - A modern programming language that transpiles to Python.

This package provides a compiler that converts OwlLang source code
into executable Python code.

Example usage:
    >>> from owllang import compile_source
    >>> python_code = compile_source('let x = 42')
    >>> print(python_code)
    x = 42

CLI usage:
    $ owl compile hello.owl
    $ owl run hello.owl
"""

from owllang.ast.nodes import (
    # Expressions
    BinaryOp,
    BoolLiteral,
    Call,
    Expr,
    FieldAccess,
    FloatLiteral,
    Identifier,
    IntLiteral,
    StringLiteral,
    UnaryOp,
    # Statements
    ExprStmt,
    IfStmt,
    LetStmt,
    ReturnStmt,
    Stmt,
    # Declarations
    FnDecl,
    Parameter,
    Program,
    PythonFromImport,
    PythonImport,
    # Tokens
    Token,
    TokenType,
)
from owllang.lexer import Lexer, LexerError, tokenize
from owllang.parser import ParseError, Parser, parse
from owllang.transpiler import Transpiler, transpile

__version__ = "0.1.0"
__all__ = [
    # Version
    "__version__",
    # Main function
    "compile_source",
    # AST nodes
    "Token",
    "TokenType",
    "Program",
    "FnDecl",
    "Parameter",
    "PythonImport",
    "PythonFromImport",
    "Stmt",
    "LetStmt",
    "ExprStmt",
    "ReturnStmt",
    "IfStmt",
    "Expr",
    "IntLiteral",
    "FloatLiteral",
    "StringLiteral",
    "BoolLiteral",
    "Identifier",
    "BinaryOp",
    "UnaryOp",
    "Call",
    "FieldAccess",
    # Lexer
    "Lexer",
    "LexerError",
    "tokenize",
    # Parser
    "Parser",
    "ParseError",
    "parse",
    # Transpiler
    "Transpiler",
    "transpile",
]


def compile_source(source: str) -> str:
    """
    Compile OwlLang source code to Python.

    Args:
        source: OwlLang source code string

    Returns:
        Generated Python source code

    Raises:
        LexerError: If tokenization fails
        ParseError: If parsing fails

    Example:
        >>> code = compile_source('let x = 42')
        >>> exec(code)
    """
    tokens = tokenize(source)
    ast = parse(tokens)
    python_code = transpile(ast)
    return python_code
