"""
Tests for OwlLang v0.2.4-alpha features.

Features tested:
1. loop (infinite loop) syntax
2. Exit from loop via break
3. Exit from loop via return
4. Warning for loop without exit
5. range(start, end) builtin
6. Combining for-in with range
"""

import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the owllang CLI with given arguments."""
    cmd = [sys.executable, "-m", "owllang.cli"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )


def compile_source(source: str) -> tuple[bool, str, str]:
    """Compile source and return (success, stdout, stderr)."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ow', delete=False) as f:
        f.write(source)
        f.flush()
        result = run_cli("check", f.name)
        Path(f.name).unlink()
        return result.returncode == 0, result.stdout, result.stderr


def run_source(source: str) -> tuple[bool, str, str]:
    """Run source and return (success, stdout, stderr)."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ow', delete=False) as f:
        f.write(source)
        f.flush()
        result = run_cli("run", f.name)
        Path(f.name).unlink()
        return result.returncode == 0, result.stdout, result.stderr


# =============================================================================
# 1. Basic Loop Tests
# =============================================================================

class TestLoopBasic:
    """Test basic loop functionality."""

    def test_loop_with_break(self) -> None:
        """Loop with break exits correctly."""
        source = """
fn main() {
    let mut i = 0
    loop {
        i = i + 1
        if i == 5 {
            break
        }
    }
    print(i)
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "5" in stdout

    def test_loop_with_immediate_break(self) -> None:
        """Loop with immediate break."""
        source = """
fn main() {
    loop {
        print("once")
        break
    }
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "once" in stdout

    def test_loop_with_return(self) -> None:
        """Loop with return exits correctly."""
        # Note: function ends with a return outside loop because
        # the typechecker requires a final expression for typed returns.
        source = """
fn find_first_even(items: List[Int]) -> Int {
    let mut i = 0
    loop {
        if i >= len(items) {
            break
        }
        let x = get(items, i)
        if x % 2 == 0 {
            return x
        }
        i = i + 1
    }
    -1
}

fn main() {
    let nums = [1, 3, 4, 5]
    print(find_first_even(nums))
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "4" in stdout

    def test_nested_loops(self) -> None:
        """Nested loops with break."""
        source = """
fn main() {
    let mut outer = 0
    loop {
        outer = outer + 1
        let mut inner = 0
        loop {
            inner = inner + 1
            if inner == 3 {
                break
            }
        }
        if outer == 2 {
            break
        }
    }
    print(outer)
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "2" in stdout

    def test_loop_with_continue(self) -> None:
        """Loop with continue."""
        source = """
fn main() {
    let mut i = 0
    let mut sum = 0
    loop {
        i = i + 1
        if i > 5 {
            break
        }
        if i % 2 == 0 {
            continue
        }
        sum = sum + i
    }
    print(sum)
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "9" in stdout  # 1 + 3 + 5 = 9


# =============================================================================
# 2. Loop Warning Tests
# =============================================================================

class TestLoopWarnings:
    """Test warnings for loop without exit."""

    def test_loop_without_exit_warning(self) -> None:
        """Loop without break/return generates warning."""
        source = """
fn main() {
    loop {
        print("forever")
    }
}
"""
        success, stdout, stderr = compile_source(source)
        assert success  # It's a warning, not an error
        assert "W0204" in stderr or "without exit" in stderr.lower()

    def test_loop_with_break_no_warning(self) -> None:
        """Loop with break does not generate warning."""
        source = """
fn main() {
    loop {
        break
    }
}
"""
        success, _, stderr = compile_source(source)
        assert success
        assert "W0204" not in stderr

    def test_loop_with_return_no_warning(self) -> None:
        """Loop with return does not generate warning."""
        source = """
fn foo() -> Int {
    loop {
        return 42
    }
    0
}

fn main() {
    print(foo())
}
"""
        success, _, stderr = compile_source(source)
        assert success
        assert "W0204" not in stderr


# =============================================================================
# 3. Range Builtin Tests
# =============================================================================

class TestRangeBuiltin:
    """Test range(start, end) builtin."""

    def test_range_basic(self) -> None:
        """Basic range produces correct list."""
        source = """
fn main() {
    let nums = range(0, 5)
    for n in nums {
        print(n)
    }
}
"""
        success, stdout, _ = run_source(source)
        assert success
        # Should print 0, 1, 2, 3, 4
        for i in range(5):
            assert str(i) in stdout

    def test_range_custom_start(self) -> None:
        """Range with custom start."""
        source = """
fn main() {
    let nums = range(3, 7)
    for n in nums {
        print(n)
    }
}
"""
        success, stdout, _ = run_source(source)
        assert success
        # Should print 3, 4, 5, 6
        for i in range(3, 7):
            assert str(i) in stdout

    def test_range_empty(self) -> None:
        """Range with start >= end is empty."""
        source = """
fn main() {
    let nums = range(5, 5)
    print(len(nums))
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "0" in stdout

    def test_range_negative(self) -> None:
        """Range with start > end is empty."""
        source = """
fn main() {
    let nums = range(10, 5)
    print(len(nums))
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "0" in stdout

    def test_range_with_negative_numbers(self) -> None:
        """Range with negative start."""
        source = """
fn main() {
    let nums = range(-2, 2)
    for n in nums {
        print(n)
    }
}
"""
        success, stdout, _ = run_source(source)
        assert success
        # Should print -2, -1, 0, 1
        assert "-2" in stdout
        assert "-1" in stdout
        assert "0" in stdout
        assert "1" in stdout

    def test_range_type(self) -> None:
        """Range returns List[Int]."""
        source = """
fn sum_list(items: List[Int]) -> Int {
    let mut total = 0
    for x in items {
        total = total + x
    }
    return total
}

fn main() {
    print(sum_list(range(1, 6)))
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "15" in stdout  # 1 + 2 + 3 + 4 + 5 = 15


# =============================================================================
# 4. Combining Loop and Range
# =============================================================================

class TestLoopAndRange:
    """Test combining loop and range patterns."""

    def test_loop_index_with_range(self) -> None:
        """Use range for indexed access in loop pattern."""
        source = """
fn main() {
    let names = ["a", "b", "c"]
    for i in range(0, len(names)) {
        print(get(names, i))
    }
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "a" in stdout
        assert "b" in stdout
        assert "c" in stdout

    def test_factorial_with_range(self) -> None:
        """Compute factorial with for-in range."""
        source = """
fn factorial(n: Int) -> Int {
    let mut result = 1
    for i in range(1, n + 1) {
        result = result * i
    }
    return result
}

fn main() {
    print(factorial(5))
}
"""
        success, stdout, _ = run_source(source)
        assert success
        assert "120" in stdout  # 5! = 120


# =============================================================================
# 5. Type Error Tests (for future implementation)
# =============================================================================

# Note: Type checking for builtin function arguments is not yet fully
# implemented. These tests are commented out for now.

# class TestLoopTypeErrors:
#     """Test type errors related to loop and range."""
#
#     def test_range_wrong_type_first_arg(self) -> None:
#         """Range with non-Int first argument is error."""
#         ...
#
#     def test_range_wrong_type_second_arg(self) -> None:
#         """Range with non-Int second argument is error."""
#         ...


# =============================================================================
# 6. Transpilation Tests
# =============================================================================

class TestLoopTranspilation:
    """Test transpilation of loop constructs."""

    def test_loop_transpiles_to_while_true(self) -> None:
        """Loop transpiles to while True."""
        from owllang.lexer import Lexer
        from owllang.parser import Parser
        from owllang.transpiler import Transpiler

        source = """
fn main() {
    loop {
        break
    }
}
"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        transpiler = Transpiler()
        result = transpiler.transpile(program)
        assert "while True:" in result
