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
from owllang.typechecker import TypeChecker


class CompileError(Exception):
    """Error raised when compilation fails due to type errors."""
    
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(f"{len(errors)} type error(s) found")


__version__ = "0.1.0-alpha"
__all__ = [
    # Version
    "__version__",
    # Main function
    "compile_source",
    "CompileError",
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


def compile_source(source: str, check_types: bool = True) -> str:
    """
    Compile OwlLang source code to Python.

    Args:
        source: OwlLang source code string
        check_types: Whether to run the type checker (default: True)

    Returns:
        Generated Python source code

    Raises:
        LexerError: If tokenization fails
        ParseError: If parsing fails
        CompileError: If type checking fails

    Example:
        >>> code = compile_source('let x = 42')
        >>> exec(code)
    """
    tokens = tokenize(source)
    ast = parse(tokens)
    
    if check_types:
        checker = TypeChecker()
        errors = checker.check(ast)
        if errors:
            raise CompileError(errors)
    
    python_code = transpile(ast)
    return python_code
