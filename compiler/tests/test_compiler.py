"""
OwlLang Compiler Tests

Run with: python -m pytest tests/test_compiler.py -v
Or simply: python tests/test_compiler.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from owl import (
    tokenize, parse, transpile, compile_source,
    TokenType, LexerError, ParseError
)


# =============================================================================
# Lexer Tests
# =============================================================================

def test_lexer_keywords():
    """Test keyword recognition."""
    source = "fn let from python import as if else return true false"
    tokens = tokenize(source)
    
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    expected = [
        TokenType.FN, TokenType.LET, TokenType.FROM,
        TokenType.PYTHON, TokenType.IMPORT, TokenType.AS,
        TokenType.IF, TokenType.ELSE, TokenType.RETURN,
        TokenType.TRUE, TokenType.FALSE
    ]
    assert types == expected, f"Expected {expected}, got {types}"
    print("✓ test_lexer_keywords")


def test_lexer_literals():
    """Test literal recognition."""
    source = '42 3.14 "hello" true false'
    tokens = tokenize(source)
    
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    expected = [
        TokenType.INT, TokenType.FLOAT, TokenType.STRING,
        TokenType.TRUE, TokenType.FALSE
    ]
    assert types == expected
    
    # Check values
    assert tokens[0].value == "42"
    assert tokens[1].value == "3.14"
    assert tokens[2].value == "hello"
    print("✓ test_lexer_literals")


def test_lexer_operators():
    """Test operator recognition."""
    source = "+ - * / % == != < > <= >= = -> ."
    tokens = tokenize(source)
    
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    expected = [
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
        TokenType.SLASH, TokenType.PERCENT, TokenType.EQ,
        TokenType.NE, TokenType.LT, TokenType.GT,
        TokenType.LE, TokenType.GE, TokenType.ASSIGN,
        TokenType.ARROW, TokenType.DOT
    ]
    assert types == expected
    print("✓ test_lexer_operators")


def test_lexer_delimiters():
    """Test delimiter recognition."""
    source = "( ) { } , :"
    tokens = tokenize(source)
    
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    expected = [
        TokenType.LPAREN, TokenType.RPAREN,
        TokenType.LBRACE, TokenType.RBRACE,
        TokenType.COMMA, TokenType.COLON
    ]
    assert types == expected
    print("✓ test_lexer_delimiters")


def test_lexer_comments():
    """Test comment handling."""
    source = """
    let x = 10 // this is a comment
    let y = 20
    """
    tokens = tokenize(source)
    
    # Comments should be skipped
    ident_tokens = [t for t in tokens if t.type == TokenType.IDENT]
    names = [t.value for t in ident_tokens]
    assert names == ["x", "y"]
    print("✓ test_lexer_comments")


# =============================================================================
# Parser Tests
# =============================================================================

def test_parser_let_statement():
    """Test let statement parsing."""
    source = "let x = 42"
    tokens = tokenize(source)
    ast = parse(tokens)
    
    assert len(ast.statements) == 1
    stmt = ast.statements[0]
    assert stmt.name == "x"
    assert stmt.value.value == 42
    print("✓ test_parser_let_statement")


def test_parser_function():
    """Test function declaration parsing."""
    source = """
    fn add(a, b) {
        return a + b
    }
    """
    tokens = tokenize(source)
    ast = parse(tokens)
    
    assert len(ast.functions) == 1
    fn = ast.functions[0]
    assert fn.name == "add"
    assert len(fn.params) == 2
    assert fn.params[0].name == "a"
    assert fn.params[1].name == "b"
    print("✓ test_parser_function")


def test_parser_import():
    """Test import statement parsing."""
    source = "from python import math"
    tokens = tokenize(source)
    ast = parse(tokens)
    
    assert len(ast.imports) == 1
    imp = ast.imports[0]
    assert imp.module == "math"
    print("✓ test_parser_import")


def test_parser_import_with_alias():
    """Test import with alias."""
    source = "from python import numpy as np"
    tokens = tokenize(source)
    ast = parse(tokens)
    
    assert len(ast.imports) == 1
    imp = ast.imports[0]
    assert imp.module == "numpy"
    assert imp.alias == "np"
    print("✓ test_parser_import_with_alias")


def test_parser_binary_ops():
    """Test binary operator parsing."""
    source = "let x = 1 + 2 * 3"
    tokens = tokenize(source)
    ast = parse(tokens)
    
    stmt = ast.statements[0]
    # Should parse as 1 + (2 * 3) due to precedence
    assert stmt.value.operator == "+"
    assert stmt.value.left.value == 1
    assert stmt.value.right.operator == "*"
    print("✓ test_parser_binary_ops")


def test_parser_function_call():
    """Test function call parsing."""
    source = "print(42)"
    tokens = tokenize(source)
    ast = parse(tokens)
    
    stmt = ast.statements[0]
    call = stmt.expr
    assert call.callee.name == "print"
    assert len(call.arguments) == 1
    assert call.arguments[0].value == 42
    print("✓ test_parser_function_call")


def test_parser_field_access():
    """Test field access parsing."""
    source = "math.sqrt(16)"
    tokens = tokenize(source)
    ast = parse(tokens)
    
    stmt = ast.statements[0]
    call = stmt.expr
    assert call.callee.field == "sqrt"
    assert call.callee.object.name == "math"
    print("✓ test_parser_field_access")


# =============================================================================
# Transpiler Tests
# =============================================================================

def test_transpile_let():
    """Test let statement transpilation."""
    source = "let x = 42"
    result = compile_source(source)
    assert "x = 42" in result
    print("✓ test_transpile_let")


def test_transpile_function():
    """Test function transpilation."""
    source = """
    fn add(a, b) {
        return a + b
    }
    """
    result = compile_source(source)
    assert "def add(a, b):" in result
    assert "return (a + b)" in result
    print("✓ test_transpile_function")


def test_transpile_import():
    """Test import transpilation."""
    source = "from python import math"
    result = compile_source(source)
    assert "import math" in result
    print("✓ test_transpile_import")


def test_transpile_import_alias():
    """Test import with alias transpilation."""
    source = "from python import numpy as np"
    result = compile_source(source)
    assert "import numpy as np" in result
    print("✓ test_transpile_import_alias")


def test_transpile_main_guard():
    """Test main function guard."""
    source = """
    fn main() {
        print("hello")
    }
    """
    result = compile_source(source)
    assert 'if __name__ == "__main__":' in result
    assert "main()" in result
    print("✓ test_transpile_main_guard")


def test_transpile_string():
    """Test string literal transpilation."""
    source = 'let msg = "Hello, World!"'
    result = compile_source(source)
    assert 'msg = "Hello, World!"' in result
    print("✓ test_transpile_string")


def test_transpile_bool():
    """Test boolean transpilation."""
    source = """
    let a = true
    let b = false
    """
    result = compile_source(source)
    assert "a = True" in result
    assert "b = False" in result
    print("✓ test_transpile_bool")


# =============================================================================
# Integration Tests
# =============================================================================

def test_full_program():
    """Test complete program compilation."""
    source = """
from python import math

fn add(a, b) {
    return a + b
}

fn main() {
    let x = 10
    let y = 20
    print(add(x, y))
    print(math.sqrt(16.0))
}
"""
    result = compile_source(source)
    
    # Check all expected parts
    assert "import math" in result
    assert "def add(a, b):" in result
    assert "def main():" in result
    assert "x = 10" in result
    assert "y = 20" in result
    assert 'if __name__ == "__main__":' in result
    
    print("✓ test_full_program")
    print("\nGenerated Python:")
    print("-" * 40)
    print(result)


# =============================================================================
# Run All Tests
# =============================================================================

def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("OwlLang Compiler Tests")
    print("=" * 50)
    
    # Lexer tests
    print("\n--- Lexer Tests ---")
    test_lexer_keywords()
    test_lexer_literals()
    test_lexer_operators()
    test_lexer_delimiters()
    test_lexer_comments()
    
    # Parser tests
    print("\n--- Parser Tests ---")
    test_parser_let_statement()
    test_parser_function()
    test_parser_import()
    test_parser_import_with_alias()
    test_parser_binary_ops()
    test_parser_function_call()
    test_parser_field_access()
    
    # Transpiler tests
    print("\n--- Transpiler Tests ---")
    test_transpile_let()
    test_transpile_function()
    test_transpile_import()
    test_transpile_import_alias()
    test_transpile_main_guard()
    test_transpile_string()
    test_transpile_bool()
    
    # Integration tests
    print("\n--- Integration Tests ---")
    test_full_program()
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
