"""
Integration tests for the OwlLang Compiler.

These tests verify the complete compilation pipeline and CLI functionality.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from owllang import compile_source


class TestEndToEnd:
    """End-to-end compilation and execution tests."""
    
    def test_hello_world(self, hello_owl_file: Path) -> None:
        """Complete hello world program compiles and runs."""
        source = hello_owl_file.read_text()
        python_code = compile_source(source)
        
        # Execute the generated code
        namespace: dict = {}
        exec(python_code, namespace)
        
        # main function should exist
        assert "main" in namespace
        assert callable(namespace["main"])
    
    def test_arithmetic_program(self, test_files_dir: Path) -> None:
        """Arithmetic program produces correct results."""
        source = (test_files_dir / "arithmetic.owl").read_text()
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["a"] == 10
        assert namespace["b"] == 20
        assert namespace["c"] == 30
    
    def test_import_math(self, test_files_dir: Path) -> None:
        """Program with math import works correctly."""
        source = (test_files_dir / "math_test.owl").read_text()
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        # main function should exist and be callable
        assert "main" in namespace


class TestCompilationPipeline:
    """Test the complete compilation pipeline."""
    
    def test_lexer_to_transpiler(self) -> None:
        """Complete pipeline from source to Python."""
        source = """
from python import math

fn calculate(x) {
    return math.sqrt(x)
}

fn main() {
    let result = calculate(16.0)
    print(result)
}
"""
        python_code = compile_source(source)
        
        # Verify all parts are present
        assert "import math" in python_code
        assert "def calculate(x):" in python_code
        assert "def main():" in python_code
        assert "math.sqrt(x)" in python_code
        assert 'if __name__ == "__main__":' in python_code
    
    def test_complex_expressions(self) -> None:
        """Complex expressions compile correctly."""
        source = """
fn complex(a, b, c) {
    let result = (a + b) * c - 10 / 2
    return result > 0
}
"""
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["complex"](5, 3, 2) is True  # (5+3)*2 - 5 = 11
        assert namespace["complex"](1, 1, 1) is False  # (1+1)*1 - 5 = -3
    
    def test_nested_function_calls(self) -> None:
        """Nested function calls compile correctly."""
        source = """
fn double(x) {
    return x * 2
}

fn add(a, b) {
    return a + b
}

fn compute() {
    return add(double(3), double(4))
}
"""
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["compute"]() == 14  # 6 + 8
    
    def test_if_else_chains(self) -> None:
        """If-else statements compile correctly."""
        source = """
fn classify(x) {
    if x > 100 {
        return "big"
    } else {
        if x > 10 {
            return "medium"
        } else {
            return "small"
        }
    }
}
"""
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["classify"](200) == "big"
        assert namespace["classify"](50) == "medium"
        assert namespace["classify"](5) == "small"


class TestErrorRecovery:
    """Test error handling in the pipeline."""
    
    def test_lexer_error_propagates(self) -> None:
        """Lexer errors are raised properly."""
        from owllang.lexer import LexerError
        
        with pytest.raises(LexerError):
            compile_source('"unterminated string')
    
    def test_parser_error_propagates(self) -> None:
        """Parser errors are raised properly."""
        from owllang.parser import ParseError
        
        with pytest.raises(ParseError):
            compile_source("let x 42")  # Missing =


class TestRealWorldPatterns:
    """Test real-world programming patterns."""
    
    def test_fibonacci(self) -> None:
        """Recursive fibonacci compiles correctly."""
        source = """
fn fib(n) {
    if n <= 1 {
        return n
    } else {
        return fib(n - 1) + fib(n - 2)
    }
}
"""
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["fib"](0) == 0
        assert namespace["fib"](1) == 1
        assert namespace["fib"](5) == 5
        assert namespace["fib"](10) == 55
    
    def test_factorial(self) -> None:
        """Recursive factorial compiles correctly."""
        source = """
fn fact(n) {
    if n <= 1 {
        return 1
    } else {
        return n * fact(n - 1)
    }
}
"""
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["fact"](0) == 1
        assert namespace["fact"](1) == 1
        assert namespace["fact"](5) == 120
    
    def test_multiple_imports(self) -> None:
        """Multiple imports work correctly."""
        source = """
from python import math
from python import json

fn use_both() {
    let pi = math.pi
    let data = json.dumps(42)
    return true
}
"""
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["use_both"]() is True
    
    def test_string_operations(self) -> None:
        """String operations work correctly."""
        source = """
fn greet(name) {
    return name
}
"""
        python_code = compile_source(source)
        
        namespace: dict = {}
        exec(python_code, namespace)
        
        assert namespace["greet"]("Alice") == "Alice"


class TestCLIIntegration:
    """Test CLI functionality (subprocess tests)."""
    
    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Shell behavior differs on Windows"
    )
    def test_cli_version(self) -> None:
        """CLI shows version."""
        result = subprocess.run(
            [sys.executable, "-m", "owllang", "--version"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "OwlLang" in result.stdout or "0.1.0" in result.stdout
    
    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Shell behavior differs on Windows"
    )
    def test_cli_help(self) -> None:
        """CLI shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "owllang", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "compile" in result.stdout
        assert "run" in result.stdout
    
    def test_cli_compile(self, hello_owl_file: Path, tmp_path: Path) -> None:
        """CLI compile command works."""
        output_file = tmp_path / "hello.py"
        
        result = subprocess.run(
            [
                sys.executable, "-m", "owllang",
                "compile", str(hello_owl_file),
                "-o", str(output_file)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "def main():" in content
    
    def test_cli_run(self, hello_owl_file: Path) -> None:
        """CLI run command works."""
        result = subprocess.run(
            [sys.executable, "-m", "owllang", "run", str(hello_owl_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Hello from OwlLang!" in result.stdout
    
    def test_cli_tokens(self, hello_owl_file: Path) -> None:
        """CLI tokens command shows tokens."""
        result = subprocess.run(
            [sys.executable, "-m", "owllang", "tokens", str(hello_owl_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "FN" in result.stdout
        assert "IDENT" in result.stdout
    
    def test_cli_ast(self, hello_owl_file: Path) -> None:
        """CLI ast command shows AST."""
        result = subprocess.run(
            [sys.executable, "-m", "owllang", "ast", str(hello_owl_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Program" in result.stdout or "FnDecl" in result.stdout
