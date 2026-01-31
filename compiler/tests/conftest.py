"""
Pytest fixtures for OwlLang compiler tests.
"""

from pathlib import Path

import pytest


# =============================================================================
# Sample Source Code Fixtures
# =============================================================================

@pytest.fixture
def simple_let_source() -> str:
    """Simple let statement."""
    return "let x = 42"


@pytest.fixture
def simple_function_source() -> str:
    """Simple function declaration."""
    return """
fn greet() {
    print("Hello")
}
"""


@pytest.fixture
def function_with_params_source() -> str:
    """Function with parameters."""
    return """
fn add(a, b) {
    return a + b
}
"""


@pytest.fixture
def complete_program_source() -> str:
    """Complete OwlLang program."""
    return """
from python import math

fn calculate(x, y) {
    let sum = x + y
    return math.sqrt(sum)
}

fn main() {
    let result = calculate(9.0, 16.0)
    print(result)
}
"""


@pytest.fixture
def arithmetic_source() -> str:
    """Arithmetic expressions."""
    return """
let a = 10 + 20
let b = 5 * 3
let c = a - b
let d = 100 / 4
"""


@pytest.fixture
def string_source() -> str:
    """String literals."""
    return 'let msg = "Hello, World!"'


@pytest.fixture
def boolean_source() -> str:
    """Boolean literals."""
    return """
let yes = true
let no = false
"""


@pytest.fixture
def if_else_source() -> str:
    """If-else statement."""
    return """
fn check(x) {
    if x > 10 {
        return true
    } else {
        return false
    }
}
"""


@pytest.fixture
def python_import_source() -> str:
    """Python import statement."""
    return "from python import json"


@pytest.fixture
def python_from_import_source() -> str:
    """Python from import statement."""
    return "from python.os.path import join, exists"


@pytest.fixture
def python_import_alias_source() -> str:
    """Python import with alias."""
    return "from python import numpy as np"


@pytest.fixture
def nested_call_source() -> str:
    """Nested function calls."""
    return "print(add(1, mul(2, 3)))"


@pytest.fixture
def field_access_source() -> str:
    """Field access expression."""
    return "let pi = math.pi"


@pytest.fixture
def comparison_source() -> str:
    """Comparison operators."""
    return """
let a = 1 == 1
let b = 2 != 3
let c = 4 < 5
let d = 6 > 5
let e = 7 <= 7
let f = 8 >= 8
"""


@pytest.fixture
def unary_source() -> str:
    """Unary operators."""
    return "let neg = -42"


@pytest.fixture
def comment_source() -> str:
    """Source with comments."""
    return """
// This is a comment
let x = 10  // inline comment
// Another comment
let y = 20
"""


@pytest.fixture
def escape_string_source() -> str:
    """String with escape sequences."""
    return r'let msg = "Hello\nWorld\t!"'


@pytest.fixture
def float_source() -> str:
    """Float literals."""
    return "let pi = 3.14159"


# =============================================================================
# Test File Fixtures
# =============================================================================

@pytest.fixture
def test_files_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with test .ow files."""
    # hello.ow
    (tmp_path / "hello.ow").write_text('''
fn main() {
    print("Hello, World!")
}
''')
    
    # math_test.ow
    (tmp_path / "math_test.ow").write_text('''
from python import math

fn main() {
    let x = math.sqrt(16.0)
    print(x)
}
''')
    
    # arithmetic.ow
    (tmp_path / "arithmetic.ow").write_text('''
let a = 10
let b = 20
let c = a + b
print(c)
''')
    
    return tmp_path


@pytest.fixture
def hello_owl_file(tmp_path: Path) -> Path:
    """Create a hello world .ow file."""
    owl_file = tmp_path / "hello.ow"
    owl_file.write_text('''
fn main() {
    print("Hello from OwlLang!")
}
''')
    return owl_file


# =============================================================================
# Expected Output Fixtures
# =============================================================================

@pytest.fixture
def simple_let_expected_python() -> str:
    """Expected Python output for simple let."""
    return "x = 42"


@pytest.fixture
def simple_function_expected_python() -> str:
    """Expected Python output for simple function."""
    return '''def greet():
    print("Hello")
'''


@pytest.fixture
def complete_program_expected_python() -> str:
    """Expected Python output for complete program."""
    return '''import math

def calculate(x, y):
    sum = (x + y)
    return math.sqrt(sum)

def main():
    result = calculate(9.0, 16.0)
    print(result)

if __name__ == "__main__":
    main()'''
