"""
OwlLang Compiler Package

A minimal compiler that transpiles OwlLang to Python.
"""

from .ast_nodes import (
    Token, TokenType,
    Program, FnDecl, Parameter,
    PythonImport, PythonFromImport,
    Stmt, LetStmt, ExprStmt, ReturnStmt, IfStmt,
    Expr, IntLiteral, FloatLiteral, StringLiteral, BoolLiteral,
    Identifier, BinaryOp, UnaryOp, Call, FieldAccess
)
from .lexer import Lexer, LexerError, tokenize
from .parser import Parser, ParseError, parse
from .transpiler import Transpiler, transpile


__version__ = "0.1.0"
__all__ = [
    # Version
    "__version__",
    
    # AST nodes
    "Token", "TokenType",
    "Program", "FnDecl", "Parameter",
    "PythonImport", "PythonFromImport",
    "Stmt", "LetStmt", "ExprStmt", "ReturnStmt", "IfStmt",
    "Expr", "IntLiteral", "FloatLiteral", "StringLiteral", "BoolLiteral",
    "Identifier", "BinaryOp", "UnaryOp", "Call", "FieldAccess",
    
    # Lexer
    "Lexer", "LexerError", "tokenize",
    
    # Parser
    "Parser", "ParseError", "parse",
    
    # Transpiler
    "Transpiler", "transpile",
    
    # Convenience
    "compile_source",
]


def compile_source(source: str) -> str:
    """
    Compile OwlLang source code to Python.
    
    Args:
        source: OwlLang source code
        
    Returns:
        Generated Python source code
        
    Raises:
        LexerError: If tokenization fails
        ParseError: If parsing fails
    """
    tokens = tokenize(source)
    ast = parse(tokens)
    python_code = transpile(ast)
    return python_code
