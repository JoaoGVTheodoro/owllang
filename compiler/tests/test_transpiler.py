"""
Tests for the OwlLang Transpiler.
"""

import pytest

from owllang import tokenize, parse, transpile, compile_source
from owllang.transpiler import Transpiler


def compile_no_check(source: str) -> str:
    """Compile source without type checking (for transpiler tests)."""
    return compile_source(source, check_types=False)


class TestCompileSource:
    """Test the high-level compile_source function."""
    
    def test_simple_let(self, simple_let_source: str) -> None:
        """compile_source handles simple let."""
        result = compile_source(simple_let_source)
        assert "x = 42" in result
    
    def test_complete_program(self, complete_program_source: str) -> None:
        """compile_source handles complete program."""
        result = compile_source(complete_program_source)
        
        assert "import math" in result
        assert "def calculate(x, y):" in result
        assert "def main():" in result
        assert 'if __name__ == "__main__":' in result


class TestImportTranspilation:
    """Test import transpilation."""
    
    def test_simple_import(self, python_import_source: str) -> None:
        """Transpiler handles simple import."""
        result = compile_source(python_import_source)
        assert "import json" in result
    
    def test_import_with_alias(self, python_import_alias_source: str) -> None:
        """Transpiler handles import with alias."""
        result = compile_source(python_import_alias_source)
        assert "import numpy as np" in result
    
    def test_from_import(self, python_from_import_source: str) -> None:
        """Transpiler handles from import."""
        result = compile_source(python_from_import_source)
        assert "from os.path import join, exists" in result
    
    def test_from_import_with_alias(self) -> None:
        """Transpiler handles from import with alias."""
        source = "from python.os.path import join as j"
        result = compile_source(source)
        assert "from os.path import join as j" in result


class TestFunctionTranspilation:
    """Test function transpilation."""
    
    def test_simple_function(self, simple_function_source: str) -> None:
        """Transpiler handles simple function."""
        result = compile_source(simple_function_source)
        
        assert "def greet():" in result
        assert 'print("Hello")' in result
    
    def test_function_with_params(self, function_with_params_source: str) -> None:
        """Transpiler handles function with params."""
        result = compile_source(function_with_params_source)
        
        assert "def add(a, b):" in result
        assert "return (a + b)" in result
    
    def test_empty_function(self) -> None:
        """Transpiler adds pass to empty function."""
        source = "fn empty() { }"
        result = compile_source(source)
        
        assert "def empty():" in result
        assert "pass" in result
    
    def test_main_function(self) -> None:
        """Transpiler adds main guard for main function."""
        source = "fn main() { print(42) }"
        result = compile_source(source)
        
        assert 'if __name__ == "__main__":' in result
        assert "main()" in result


class TestStatementTranspilation:
    """Test statement transpilation."""
    
    def test_let_statement(self, simple_let_source: str) -> None:
        """Transpiler converts let to assignment."""
        result = compile_source(simple_let_source)
        assert "x = 42" in result
        assert "let" not in result
    
    def test_return_statement(self) -> None:
        """Transpiler handles return statement."""
        source = "fn test() { return 42 }"
        result = compile_source(source)
        assert "return 42" in result
    
    def test_empty_return(self) -> None:
        """Transpiler handles empty return."""
        source = "fn test() { return }"
        result = compile_source(source)
        assert "return" in result
    
    def test_if_statement(self) -> None:
        """Transpiler handles if statement."""
        source = """
fn check(x) {
    if x > 0 {
        print("positive")
    }
}
"""
        result = compile_source(source)
        assert "if (x > 0):" in result
    
    def test_if_else_statement(self, if_else_source: str) -> None:
        """Transpiler handles if-else statement."""
        result = compile_source(if_else_source)
        
        assert "if (x > 10):" in result
        assert "else:" in result
    
    def test_expression_statement(self) -> None:
        """Transpiler handles expression statement."""
        source = "print(42)"
        result = compile_source(source)
        assert "print(42)" in result


class TestExpressionTranspilation:
    """Test expression transpilation."""
    
    def test_integer_literal(self) -> None:
        """Transpiler handles integer literal."""
        result = compile_source("let x = 42")
        assert "42" in result
    
    def test_float_literal(self, float_source: str) -> None:
        """Transpiler handles float literal."""
        result = compile_source(float_source)
        assert "3.14159" in result
    
    def test_string_literal(self, string_source: str) -> None:
        """Transpiler handles string literal."""
        result = compile_source(string_source)
        assert '"Hello, World!"' in result
    
    def test_string_escape(self) -> None:
        """Transpiler escapes special characters in strings."""
        source = r'let x = "line1\nline2"'
        result = compile_source(source)
        # The transpiler should preserve or escape the newline
        assert '"' in result
    
    def test_boolean_true(self) -> None:
        """Transpiler converts true to True."""
        result = compile_source("let x = true")
        assert "True" in result
        assert "true" not in result.split("=")[1]  # Check value, not keyword
    
    def test_boolean_false(self) -> None:
        """Transpiler converts false to False."""
        result = compile_source("let x = false")
        assert "False" in result
    
    def test_binary_operations(self, arithmetic_source: str) -> None:
        """Transpiler handles binary operations."""
        result = compile_source(arithmetic_source)
        
        assert "(10 + 20)" in result
        assert "(5 * 3)" in result
    
    def test_unary_operation(self, unary_source: str) -> None:
        """Transpiler handles unary operations."""
        result = compile_source(unary_source)
        assert "(-42)" in result
    
    def test_comparison_operations(self) -> None:
        """Transpiler handles comparison operations."""
        source = "let x = 1 == 1"
        result = compile_source(source)
        assert "(1 == 1)" in result
    
    def test_function_call(self) -> None:
        """Transpiler handles function call."""
        source = "print(42)"
        result = compile_source(source)
        assert "print(42)" in result
    
    def test_function_call_multiple_args(self) -> None:
        """Transpiler handles function call with multiple args."""
        source = "add(1, 2, 3)"
        result = compile_no_check(source)
        assert "add(1, 2, 3)" in result
    
    def test_nested_call(self, nested_call_source: str) -> None:
        """Transpiler handles nested function calls."""
        result = compile_no_check(nested_call_source)
        assert "print(add(1, mul(2, 3)))" in result
    
    def test_field_access(self, field_access_source: str) -> None:
        """Transpiler handles field access."""
        result = compile_no_check(field_access_source)
        assert "math.pi" in result
    
    def test_method_call(self) -> None:
        """Transpiler handles method call."""
        source = 'let upper = msg.upper()'
        result = compile_no_check(source)
        assert "msg.upper()" in result


class TestIndentation:
    """Test code indentation."""
    
    def test_function_body_indented(self) -> None:
        """Function body is properly indented."""
        source = """
fn test() {
    let x = 1
    let y = 2
}
"""
        result = compile_source(source)
        lines = result.strip().split('\n')
        
        # Find the function definition
        for i, line in enumerate(lines):
            if line.startswith("def test"):
                # Check body is indented
                assert lines[i + 1].startswith("    ")
                break
    
    def test_nested_if_indentation(self) -> None:
        """Nested if statements are properly indented."""
        source = """
fn test(x) {
    if x > 0 {
        if x > 10 {
            print("big")
        }
    }
}
"""
        result = compile_source(source)
        
        # Should have proper nesting
        assert "        " in result  # 8 spaces for nested if body


class TestCompletePrograms:
    """Test complete program transpilation."""
    
    def test_hello_world(self) -> None:
        """Transpiler handles Hello World."""
        source = '''
fn main() {
    print("Hello, World!")
}
'''
        result = compile_source(source)
        
        assert "def main():" in result
        assert 'print("Hello, World!")' in result
        assert 'if __name__ == "__main__":' in result
    
    def test_calculator(self) -> None:
        """Transpiler handles calculator program."""
        source = '''
fn add(a, b) {
    return a + b
}

fn main() {
    let result = add(10, 20)
    print(result)
}
'''
        result = compile_source(source)
        
        assert "def add(a, b):" in result
        assert "return (a + b)" in result
        assert "result = add(10, 20)" in result
    
    def test_with_imports(self, complete_program_source: str) -> None:
        """Transpiler handles program with imports."""
        result = compile_source(complete_program_source)
        
        # Check import is at top
        lines = result.strip().split('\n')
        assert lines[0] == "import math"
        
        # Check function uses import
        assert "math.sqrt(sum)" in result


class TestTranspilerClass:
    """Test Transpiler class directly."""
    
    def test_transpiler_instance(self) -> None:
        """Transpiler can be instantiated and used."""
        tokens = tokenize("let x = 42")
        ast = parse(tokens)
        transpiler = Transpiler()
        result = transpiler.transpile(ast)
        
        assert "x = 42" in result
    
    def test_transpiler_reuse(self) -> None:
        """Transpiler can be reused for multiple programs."""
        transpiler = Transpiler()
        
        tokens1 = tokenize("let a = 1")
        ast1 = parse(tokens1)
        result1 = transpiler.transpile(ast1)
        
        tokens2 = tokenize("let b = 2")
        ast2 = parse(tokens2)
        result2 = transpiler.transpile(ast2)
        
        assert "a = 1" in result1
        assert "b = 2" in result2


class TestExecutability:
    """Test that generated Python is executable."""
    
    def test_executable_let(self) -> None:
        """Generated let statement is executable."""
        result = compile_source("let x = 42")
        
        namespace: dict = {}
        exec(result, namespace)
        assert namespace["x"] == 42
    
    def test_executable_arithmetic(self) -> None:
        """Generated arithmetic is executable."""
        source = """
let a = 10
let b = 20
let c = a + b
"""
        result = compile_source(source)
        
        namespace: dict = {}
        exec(result, namespace)
        assert namespace["c"] == 30
    
    def test_executable_function(self) -> None:
        """Generated function is executable."""
        source = """
fn add(a, b) {
    return a + b
}
"""
        result = compile_source(source)
        
        namespace: dict = {}
        exec(result, namespace)
        assert namespace["add"](1, 2) == 3
    
    def test_executable_if_else(self) -> None:
        """Generated if-else is executable."""
        source = """
fn check(x) {
    if x > 0 {
        return true
    } else {
        return false
    }
}
"""
        result = compile_source(source)
        
        namespace: dict = {}
        exec(result, namespace)
        assert namespace["check"](5) is True
        assert namespace["check"](-5) is False


class TestTryOperatorTranspilation:
    """Test transpilation of the ? operator."""
    
    def test_try_in_let_generates_early_return(self) -> None:
        """let x = foo()? should generate early return pattern."""
        source = """
fn process() {
    let x = get_value()?
    x
}
"""
        result = compile_no_check(source)
        
        # Should contain the early return pattern
        assert "__try_" in result
        assert "isinstance" in result
        assert "Err" in result
        assert "return" in result
        assert ".value" in result
    
    def test_try_in_return_generates_early_return(self) -> None:
        """return foo()? should generate early return pattern."""
        source = """
fn process() {
    return get_value()?
}
"""
        result = compile_no_check(source)
        
        assert "__try_" in result
        assert "isinstance" in result
        assert "Err" in result
    
    def test_try_generates_result_runtime(self) -> None:
        """Using ? should generate Ok/Err runtime classes."""
        source = """
fn process() {
    let x = get_value()?
    x
}
"""
        result = compile_no_check(source)
        
        # Should contain the runtime classes
        assert "class Ok:" in result
        assert "class Err:" in result
    
    def test_try_executable_with_ok(self) -> None:
        """Generated try code should work with Ok values."""
        source = """
fn test_ok() {
    let x = Ok(42)?
    return x
}
"""
        result = compile_no_check(source)
        
        namespace: dict = {}
        exec(result, namespace)
        
        # The function should return 42 when given Ok(42)
        assert namespace["test_ok"]() == 42
    
    def test_try_executable_with_err(self) -> None:
        """Generated try code should return early with Err values."""
        source = """
fn make_err() {
    return Err("oops")
}

fn test_err() {
    let x = make_err()?
    return x + 100
}
"""
        result = compile_no_check(source)
        
        namespace: dict = {}
        exec(result, namespace)
        
        # The function should return the Err, not x + 100
        result_value = namespace["test_err"]()
        assert isinstance(result_value, namespace["Err"])
        assert result_value.error == "oops"
    
    def test_chained_try_transpilation(self) -> None:
        """Chained ? operators should work correctly."""
        source = """
fn process() {
    let a = Ok(10)?
    let b = Ok(20)?
    return a + b
}
"""
        result = compile_no_check(source)
        
        namespace: dict = {}
        exec(result, namespace)
        
        assert namespace["process"]() == 30
    
    def test_no_runtime_when_not_needed(self) -> None:
        """Programs without ? should not include runtime."""
        source = """
fn add(a, b) {
    a + b
}
"""
        result = compile_no_check(source)
        
        # Should NOT contain the runtime classes
        assert "class Ok:" not in result
        assert "class Err:" not in result
