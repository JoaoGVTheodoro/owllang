"""
OwlLang CLI

Command-line interface for the OwlLang compiler.

Usage:
    python -m owl compile <file.owl>     Compile to Python
    python -m owl run <file.owl>         Compile and run
    python -m owl tokens <file.owl>      Show tokens (debug)
    python -m owl ast <file.owl>         Show AST (debug)
"""

import sys
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from . import compile_source, tokenize, parse, __version__
from .lexer import LexerError
from .parser import ParseError, _print_ast


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="owl",
        description="OwlLang Compiler - Transpiles OwlLang to Python"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"OwlLang {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # compile command
    compile_parser = subparsers.add_parser("compile", help="Compile .owl to .py")
    compile_parser.add_argument("file", help="OwlLang source file")
    compile_parser.add_argument("-o", "--output", help="Output file (default: <file>.py)")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Compile and run")
    run_parser.add_argument("file", help="OwlLang source file")
    
    # tokens command (debug)
    tokens_parser = subparsers.add_parser("tokens", help="Show tokens (debug)")
    tokens_parser.add_argument("file", help="OwlLang source file")
    
    # ast command (debug)
    ast_parser = subparsers.add_parser("ast", help="Show AST (debug)")
    ast_parser.add_argument("file", help="OwlLang source file")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    try:
        if args.command == "compile":
            return cmd_compile(args.file, args.output)
        elif args.command == "run":
            return cmd_run(args.file)
        elif args.command == "tokens":
            return cmd_tokens(args.file)
        elif args.command == "ast":
            return cmd_ast(args.file)
    except (LexerError, ParseError) as e:
        print_error(e)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        raise
    
    return 0


def cmd_compile(input_file: str, output_file: Optional[str] = None) -> int:
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
    print(f"✓ Compiled successfully")
    
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
    _print_ast(ast)
    
    return 0


def print_error(error: Exception):
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


if __name__ == "__main__":
    sys.exit(main())
