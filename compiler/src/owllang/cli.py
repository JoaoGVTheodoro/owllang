"""
OwlLang CLI

Command-line interface for the OwlLang compiler.

Usage:
    owllang compile <file.ow>      Compile to Python
    owllang run <file.ow>          Compile and run
    owllang check <file.ow>        Type check (no output)
    owllang check examples/        Check all .ow files in directory
    owllang tokens <file.ow>       Show tokens (debug)
    owllang ast <file.ow>          Show AST (debug)

Exit Codes:
    0 - Success
    1 - Compilation error
    2 - Warnings treated as errors (with --deny-warnings)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

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


# =============================================================================
# Exit Codes
# =============================================================================

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_WARNING_AS_ERROR = 2


# =============================================================================
# Structured Output
# =============================================================================

@dataclass
class DiagnosticOutput:
    """Structured diagnostic for JSON output."""
    severity: str  # "error" or "warning"
    code: str
    message: str
    file: str
    line: int
    column: int
    hints: list[str]
    notes: list[str]
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CheckResult:
    """Result of checking a file or directory."""
    file: str
    success: bool
    errors: list[DiagnosticOutput]
    warnings: list[DiagnosticOutput]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "success": self.success,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
        }


# =============================================================================
# File Discovery
# =============================================================================

def discover_owl_files(path: Path) -> list[Path]:
    """
    Discover .ow files from a path.
    
    If path is a file, returns [path].
    If path is a directory, returns all .ow files recursively.
    """
    if path.is_file():
        return [path]
    elif path.is_dir():
        files = sorted(path.rglob("*.ow"))
        return files
    else:
        return []


# =============================================================================
# Output Functions
# =============================================================================

def print_error_stderr(message: str) -> None:
    """Print error message to stderr."""
    print(f"\033[91m{message}\033[0m", file=sys.stderr)


def print_warning_stderr(message: str) -> None:
    """Print warning message to stderr."""
    print(f"\033[93m{message}\033[0m", file=sys.stderr)


def print_success_stderr(message: str) -> None:
    """Print success message to stderr."""
    print(f"\033[92m{message}\033[0m", file=sys.stderr)


def print_info_stderr(message: str) -> None:
    """Print info message to stderr."""
    print(message, file=sys.stderr)


def print_type_errors(input_file: str, errors: list) -> None:
    """Print type errors to stderr."""
    print_error_stderr(f"Type errors in {input_file}:")
    for error in errors:
        print(f"  {error}", file=sys.stderr)


# =============================================================================
# Main Entry Point
# =============================================================================

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
    compile_parser.add_argument("--profile", action="store_true",
                               help="Show compilation timing breakdown")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Compile and run")
    run_parser.add_argument("file", help="OwlLang source file (.ow)")
    run_parser.add_argument("--profile", action="store_true",
                           help="Show compilation timing breakdown")
    
    # check command (type check)
    check_parser = subparsers.add_parser("check", help="Type check without compiling")
    check_parser.add_argument("path", help="OwlLang source file (.ow) or directory")
    check_parser.add_argument("--deny-warnings", "-W", action="store_true",
                             help="Treat warnings as errors (exit code 2)")
    check_parser.add_argument("--no-warnings", action="store_true",
                             help="Suppress all warnings")
    check_parser.add_argument("--json", action="store_true",
                             help="Output diagnostics as JSON")
    
    # tokens command (debug)
    tokens_parser = subparsers.add_parser("tokens", help="Show tokens (debug)")
    tokens_parser.add_argument("file", help="OwlLang source file (.ow)")
    
    # ast command (debug)
    ast_parser = subparsers.add_parser("ast", help="Show AST (debug)")
    ast_parser.add_argument("file", help="OwlLang source file (.ow)")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return EXIT_SUCCESS
    
    try:
        if args.command == "compile":
            return cmd_compile(args.file, args.output, profile=getattr(args, 'profile', False))
        elif args.command == "run":
            return cmd_run(args.file, profile=getattr(args, 'profile', False))
        elif args.command == "check":
            return cmd_check(
                args.path,
                deny_warnings=args.deny_warnings,
                no_warnings=args.no_warnings,
                json_output=args.json
            )
        elif args.command == "tokens":
            return cmd_tokens(args.file)
        elif args.command == "ast":
            return cmd_ast(args.file)
    except (LexerError, ParseError) as e:
        print_error(e)
        return EXIT_ERROR
    except CompileError as e:
        print_type_errors(args.file, e.errors)
        return EXIT_ERROR
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        raise
    
    return EXIT_SUCCESS


# =============================================================================
# Commands
# =============================================================================

def cmd_compile(input_file: str, output_file: str | None = None, profile: bool = False) -> int:
    """Compile OwlLang file to Python."""
    from .typechecker import TypeChecker
    
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
    
    # Parse first to check for errors
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
    except (LexerError, ParseError) as e:
        print_error(e)
        print_error_stderr(f"✗ Compilation failed - no output generated")
        return EXIT_ERROR
    
    # Type check
    checker = TypeChecker()
    errors = checker.check(ast)
    
    if errors:
        print_type_errors(input_file, errors)
        print_error_stderr(f"✗ Compilation failed - no output generated")
        return EXIT_ERROR
    
    # Compile
    print_info_stderr(f"Compiling {input_path} → {output_path}")
    python_code = compile_source(source, profile=profile)
    
    # Write output
    output_path.write_text(python_code)
    print_success_stderr("✓ Compiled successfully")
    
    return EXIT_SUCCESS


def cmd_run(input_file: str, profile: bool = False) -> int:
    """Compile and run OwlLang file."""
    from .typechecker import TypeChecker
    
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Read source
    source = input_path.read_text()
    
    # Parse first to check for errors
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
    except (LexerError, ParseError) as e:
        print_error(e)
        print_error_stderr(f"✗ Cannot run - compilation failed")
        return EXIT_ERROR
    
    # Type check
    checker = TypeChecker()
    errors = checker.check(ast)
    
    if errors:
        print_type_errors(input_file, errors)
        print_error_stderr(f"✗ Cannot run - type errors found")
        return EXIT_ERROR
    
    # Compile and run
    python_code = compile_source(source, profile=profile)
    
    # Write to temp file and run
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(python_code)
        temp_path = f.name
    
    try:
        # Run with Python - stdout goes to stdout, stderr to stderr
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=False
        )
        return result.returncode
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)


def cmd_check(
    path: str,
    deny_warnings: bool = False,
    no_warnings: bool = False,
    json_output: bool = False
) -> int:
    """Type check OwlLang file(s) without generating output."""
    from .typechecker import TypeChecker
    from .diagnostics import DUMMY_SPAN
    
    input_path = Path(path)
    
    if not input_path.exists():
        if json_output:
            print(json.dumps({"error": f"Path not found: {path}"}))
        else:
            print_error_stderr(f"Error: Path not found: {path}")
        return EXIT_ERROR
    
    # Discover files
    files = discover_owl_files(input_path)
    
    if not files:
        if json_output:
            print(json.dumps({"error": f"No .ow files found in: {path}"}))
        else:
            print_error_stderr(f"Error: No .ow files found in: {path}")
        return EXIT_ERROR
    
    # Check all files
    results: list[CheckResult] = []
    total_errors = 0
    total_warnings = 0
    
    for file_path in files:
        result = check_single_file(file_path, no_warnings)
        results.append(result)
        total_errors += len(result.errors)
        total_warnings += len(result.warnings)
    
    # Output results
    if json_output:
        output_json(results)
        # Determine exit code silently for JSON mode
        if total_errors > 0:
            return EXIT_ERROR
        if total_warnings > 0 and deny_warnings:
            return EXIT_WARNING_AS_ERROR
        return EXIT_SUCCESS
    else:
        return output_human(results, deny_warnings, no_warnings)


def check_single_file(file_path: Path, no_warnings: bool = False) -> CheckResult:
    """Check a single file and return structured result."""
    from .typechecker import TypeChecker
    from .diagnostics import DUMMY_SPAN
    
    errors: list[DiagnosticOutput] = []
    warnings: list[DiagnosticOutput] = []
    
    try:
        source = file_path.read_text()
        tokens = tokenize(source)
        ast = parse(tokens)
        
        checker = TypeChecker()
        type_errors = checker.check(ast)
        type_warnings = checker.get_warnings()
        
        # Convert errors
        for err in type_errors:
            errors.append(DiagnosticOutput(
                severity="error",
                code=getattr(err, 'code', "E0000"),  # Use error code if available
                message=err.message,
                file=str(file_path),
                line=getattr(err, 'line', 1),
                column=getattr(err, 'column', 1),
                hints=getattr(err, 'hints', None) or [],
                notes=[],
            ))
        
        # Convert warnings (sorted by line for deterministic order)
        sorted_warnings = sorted(
            type_warnings,
            key=lambda w: (w.span.start.line if w.span else 0, w.span.start.column if w.span else 0)
        )
        
        if not no_warnings:
            for warn in sorted_warnings:
                span = warn.span if warn.span else DUMMY_SPAN
                warnings.append(DiagnosticOutput(
                    severity="warning",
                    code=warn.code.value,
                    message=warn.message,
                    file=str(file_path),
                    line=span.start.line,
                    column=span.start.column,
                    hints=warn.hints,
                    notes=warn.notes,
                ))
        
    except LexerError as e:
        errors.append(DiagnosticOutput(
            severity="error",
            code="E0100",  # Lexer error
            message=e.message,
            file=str(file_path),
            line=e.line,
            column=e.column,
            hints=[],
            notes=[],
        ))
    except ParseError as e:
        errors.append(DiagnosticOutput(
            severity="error",
            code="E0200",  # Parse error
            message=e.message,
            file=str(file_path),
            line=e.token.line,
            column=e.token.column,
            hints=[],
            notes=[],
        ))
    
    return CheckResult(
        file=str(file_path),
        success=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def output_json(results: list[CheckResult]) -> None:
    """Output results as JSON to stdout."""
    output = {
        "version": __version__,
        "files": [r.to_dict() for r in results],
        "summary": {
            "total_files": len(results),
            "files_with_errors": sum(1 for r in results if not r.success),
            "total_errors": sum(len(r.errors) for r in results),
            "total_warnings": sum(len(r.warnings) for r in results),
        }
    }
    print(json.dumps(output, indent=2))


def output_human(
    results: list[CheckResult],
    deny_warnings: bool,
    no_warnings: bool
) -> int:
    """Output results in human-readable format to stderr. Returns exit code."""
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    
    # Print diagnostics for each file
    for result in results:
        if result.errors:
            print_error_stderr(f"Errors in {result.file}:")
            for err in result.errors:
                print(f"  error[{err.code}]: {err.message}", file=sys.stderr)
                for hint in err.hints:
                    print(f"    hint: {hint}", file=sys.stderr)
        
        if result.warnings and not no_warnings:
            color_code = "\033[91m" if deny_warnings else "\033[93m"
            reset = "\033[0m"
            label = "Errors (from warnings)" if deny_warnings else "Warnings"
            print(f"{color_code}{label} in {result.file}:{reset}", file=sys.stderr)
            for warn in result.warnings:
                print(f"  warning[{warn.code}]: {warn.message}", file=sys.stderr)
                for hint in warn.hints:
                    print(f"    hint: {hint}", file=sys.stderr)
    
    # Summary
    if len(results) > 1:
        print(file=sys.stderr)
        print(f"Checked {len(results)} files", file=sys.stderr)
    
    # Final status
    if total_errors > 0:
        print_error_stderr(f"✗ {total_errors} error(s) found")
        return EXIT_ERROR
    
    if total_warnings > 0 and deny_warnings:
        print_error_stderr(f"✗ {total_warnings} warning(s) treated as errors")
        return EXIT_WARNING_AS_ERROR
    
    if total_warnings > 0 and not no_warnings:
        print_success_stderr(f"✓ No errors found ({total_warnings} warning(s))")
    else:
        print_success_stderr(f"✓ No issues found")
    
    return EXIT_SUCCESS


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
    
    return EXIT_SUCCESS


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
    
    return EXIT_SUCCESS


# =============================================================================
# Helper Functions
# =============================================================================

def print_error(error: Exception) -> None:
    """Print formatted error message to stderr."""
    if isinstance(error, LexerError):
        print(f"\033[91mLexer Error\033[0m at {error.line}:{error.column}", file=sys.stderr)
        print(f"  {error.message}", file=sys.stderr)
    elif isinstance(error, ParseError):
        print(f"\033[91mParse Error\033[0m at {error.token.line}:{error.token.column}", file=sys.stderr)
        print(f"  {error.message}", file=sys.stderr)
        print(f"  Got: {error.token.value!r}", file=sys.stderr)
    else:
        print(f"\033[91mError\033[0m: {error}", file=sys.stderr)


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
