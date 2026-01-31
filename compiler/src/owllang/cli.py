"""
OwlLang CLI

Command-line interface for the OwlLang compiler.

Usage:
    owllang compile <file.ow>      Compile to Python
    owllang run <file.ow>          Compile and run
    owllang check <file.ow>        Type check (no output)
    owllang tokens <file.ow>       Show tokens (debug)
    owllang ast <file.ow>          Show AST (debug)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from . import __version__, compile_source, parse, CompileError
from .lexer import LexerError, tokenize
from .parser import ParseError

# AST node types for pretty printing
from .ast import (
    BoolLiteral,
    Call,
    ExprStmt,
    FieldAccess,
    FloatLiteral,
    FnDecl,
    Identifier,
    IntLiteral,
    LetStmt,
    Program,
    PythonFromImport,
    PythonImport,
    StringLiteral,
    BinaryOp,
)


def print_type_errors(input_file: str, errors: list) -> None:
    """Print type errors to stderr."""
    print(f"\033[91mType errors in {input_file}:\033[0m")
    for error in errors:
        print(f"  {error}")


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="owllang",
        description="OwlLang Compiler - Transpiles OwlLang to Python"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"OwlLang {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # compile command
    compile_parser = subparsers.add_parser("compile", help="Compile .ow to .py")
    compile_parser.add_argument("file", help="OwlLang source file (.ow)")
    compile_parser.add_argument("-o", "--output", help="Output file (default: <file>.py)")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Compile and run")
    run_parser.add_argument("file", help="OwlLang source file (.ow)")
    
    # check command (type check)
    check_parser = subparsers.add_parser("check", help="Type check without compiling")
    check_parser.add_argument("file", help="OwlLang source file (.ow)")
    
    # tokens command (debug)
    tokens_parser = subparsers.add_parser("tokens", help="Show tokens (debug)")
    tokens_parser.add_argument("file", help="OwlLang source file (.ow)")
    
    # ast command (debug)
    ast_parser = subparsers.add_parser("ast", help="Show AST (debug)")
    ast_parser.add_argument("file", help="OwlLang source file (.ow)")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    try:
        if args.command == "compile":
            return cmd_compile(args.file, args.output)
        elif args.command == "run":
            return cmd_run(args.file)
        elif args.command == "check":
            return cmd_check(args.file)
        elif args.command == "tokens":
            return cmd_tokens(args.file)
        elif args.command == "ast":
            return cmd_ast(args.file)
    except (LexerError, ParseError) as e:
        print_error(e)
        return 1
    except CompileError as e:
        print_type_errors(args.file, e.errors)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        raise
    
    return 0


def cmd_compile(input_file: str, output_file: str | None = None) -> int:
    """Compile OwlLang file to Python."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Determine output file
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = input_path.with_suffix(".py")
    
    # Read source
    source = input_path.read_text()
    
    # Compile
    print(f"Compiling {input_path} → {output_path}")
    python_code = compile_source(source)
    
    # Write output
    output_path.write_text(python_code)
    print("✓ Compiled successfully")
    
    return 0


def cmd_run(input_file: str) -> int:
    """Compile and run OwlLang file."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Read and compile
    source = input_path.read_text()
    python_code = compile_source(source)
    
    # Write to temp file and run
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(python_code)
        temp_path = f.name
    
    try:
        # Run with Python
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=False
        )
        return result.returncode
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)


def cmd_check(input_file: str) -> int:
    """Type check OwlLang file without generating output."""
    from .typechecker import TypeChecker, TypeError as OwlTypeError
    
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Read and parse
    source = input_path.read_text()
    tokens = tokenize(source)
    ast = parse(tokens)
    
    # Type check
    checker = TypeChecker()
    errors = checker.check(ast)
    
    if errors:
        print(f"\033[91mType errors in {input_file}:\033[0m")
        for error in errors:
            print(f"  {error}")
        return 1
    
    print(f"✓ {input_file}: No type errors found")
    return 0


def cmd_tokens(input_file: str) -> int:
    """Show tokens for debugging."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    source = input_path.read_text()
    tokens = tokenize(source)
    
    print(f"Tokens for {input_file}:")
    print("-" * 50)
    for token in tokens:
        print(f"  {token}")
    
    return 0


def cmd_ast(input_file: str) -> int:
    """Show AST for debugging."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    source = input_path.read_text()
    tokens = tokenize(source)
    ast = parse(tokens)
    
    print(f"AST for {input_file}:")
    print("-" * 50)
    print_ast(ast)
    
    return 0


def print_error(error: Exception) -> None:
    """Print formatted error message."""
    if isinstance(error, LexerError):
        print(f"\033[91mLexer Error\033[0m at {error.line}:{error.column}")
        print(f"  {error.message}")
    elif isinstance(error, ParseError):
        print(f"\033[91mParse Error\033[0m at {error.token.line}:{error.token.column}")
        print(f"  {error.message}")
        print(f"  Got: {error.token.value!r}")
    else:
        print(f"\033[91mError\033[0m: {error}")


def print_ast(node: object, indent: int = 0) -> None:
    """Pretty-print AST node."""
    prefix = "  " * indent
    
    if isinstance(node, Program):
        print(f"{prefix}Program:")
        print(f"{prefix}  Imports:")
        for imp in node.imports:
            print_ast(imp, indent + 2)
        print(f"{prefix}  Functions:")
        for fn in node.functions:
            print_ast(fn, indent + 2)
        print(f"{prefix}  Statements:")
        for stmt in node.statements:
            print_ast(stmt, indent + 2)
    
    elif isinstance(node, PythonImport):
        alias = f" as {node.alias}" if node.alias else ""
        print(f"{prefix}PythonImport: {node.module}{alias}")
    
    elif isinstance(node, PythonFromImport):
        names = ", ".join(
            f"{n} as {a}" if a else n for n, a in node.names
        )
        print(f"{prefix}PythonFromImport: from {node.module} import {names}")
    
    elif isinstance(node, FnDecl):
        params = ", ".join(p.name for p in node.params)
        print(f"{prefix}FnDecl: {node.name}({params})")
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, LetStmt):
        print(f"{prefix}LetStmt: {node.name} =")
        print_ast(node.value, indent + 1)
    
    elif isinstance(node, ExprStmt):
        print(f"{prefix}ExprStmt:")
        print_ast(node.expr, indent + 1)
    
    elif isinstance(node, Call):
        print(f"{prefix}Call:")
        print_ast(node.callee, indent + 1)
        print(f"{prefix}  Args:")
        for arg in node.arguments:
            print_ast(arg, indent + 2)
    
    elif isinstance(node, BinaryOp):
        print(f"{prefix}BinaryOp: {node.operator}")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    
    elif isinstance(node, Identifier):
        print(f"{prefix}Ident: {node.name}")
    
    elif isinstance(node, IntLiteral):
        print(f"{prefix}Int: {node.value}")
    
    elif isinstance(node, FloatLiteral):
        print(f"{prefix}Float: {node.value}")
    
    elif isinstance(node, StringLiteral):
        print(f"{prefix}String: {node.value!r}")
    
    elif isinstance(node, BoolLiteral):
        print(f"{prefix}Bool: {node.value}")
    
    elif isinstance(node, FieldAccess):
        print(f"{prefix}FieldAccess: .{node.field}")
        print_ast(node.object, indent + 1)
    
    else:
        print(f"{prefix}{type(node).__name__}: {node}")


if __name__ == "__main__":
    sys.exit(main())
