"""
Tests for OwlLang v0.2.2-alpha features.

Features tested:
1. List[T] type system
2. List literals [1, 2, 3]
3. Built-in functions: len, get, push, is_empty
4. Type checking for homogeneous lists
5. Transpilation to Python lists
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
# 1. List Literal Tests
# =============================================================================

class TestListLiteral:
    """Test list literal syntax and parsing."""
    
    def test_empty_list(self) -> None:
        """Empty list literal []."""
        source = """
fn main() {
    let xs = []
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "0" in stdout
    
    def test_int_list(self) -> None:
        """List of integers [1, 2, 3]."""
        source = """
fn main() {
    let xs = [1, 2, 3]
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_string_list(self) -> None:
        """List of strings."""
        source = """
fn main() {
    let xs = ["a", "b", "c"]
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_bool_list(self) -> None:
        """List of booleans."""
        source = """
fn main() {
    let xs = [true, false, true]
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_trailing_comma(self) -> None:
        """List with trailing comma."""
        source = """
fn main() {
    let xs = [1, 2, 3,]
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_single_element(self) -> None:
        """Single element list."""
        source = """
fn main() {
    let xs = [42]
    print(get(xs, 0))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "42" in stdout


# =============================================================================
# 2. Built-in Function Tests
# =============================================================================

class TestLen:
    """Test len() built-in function."""
    
    def test_len_empty(self) -> None:
        """len of empty list is 0."""
        source = """
fn main() {
    print(len([]))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "0" in stdout
    
    def test_len_non_empty(self) -> None:
        """len returns correct count."""
        source = """
fn main() {
    print(len([1, 2, 3, 4, 5]))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "5" in stdout


class TestGet:
    """Test get() built-in function."""
    
    def test_get_first(self) -> None:
        """get(list, 0) returns first element."""
        source = """
fn main() {
    let xs = [10, 20, 30]
    print(get(xs, 0))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "10" in stdout
    
    def test_get_middle(self) -> None:
        """get(list, 1) returns second element."""
        source = """
fn main() {
    let xs = [10, 20, 30]
    print(get(xs, 1))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "20" in stdout
    
    def test_get_last(self) -> None:
        """get(list, len-1) returns last element."""
        source = """
fn main() {
    let xs = [10, 20, 30]
    print(get(xs, 2))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "30" in stdout


class TestPush:
    """Test push() built-in function."""
    
    def test_push_to_empty(self) -> None:
        """push to empty list creates single element list."""
        source = """
fn main() {
    let xs = push([], 1)
    print(len(xs))
    print(get(xs, 0))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "1" in stdout
    
    def test_push_to_existing(self) -> None:
        """push adds element to end."""
        source = """
fn main() {
    let xs = [1, 2]
    let ys = push(xs, 3)
    print(len(ys))
    print(get(ys, 2))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_push_immutable(self) -> None:
        """push returns new list, original unchanged."""
        source = """
fn main() {
    let xs = [1, 2]
    let ys = push(xs, 3)
    print(len(xs))
    print(len(ys))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        lines = stdout.strip().split('\n')
        assert "2" in lines[0]
        assert "3" in lines[1]


class TestIsEmpty:
    """Test is_empty() built-in function."""
    
    def test_is_empty_true(self) -> None:
        """is_empty([]) returns true."""
        source = """
fn main() {
    if is_empty([]) {
        print("empty")
    } else {
        print("not empty")
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "empty" in stdout
    
    def test_is_empty_false(self) -> None:
        """is_empty([1]) returns false."""
        source = """
fn main() {
    if is_empty([1, 2, 3]) {
        print("empty")
    } else {
        print("not empty")
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "not empty" in stdout


# =============================================================================
# 3. Type Checking Tests
# =============================================================================

class TestListTypeChecking:
    """Test type checking for lists."""
    
    def test_homogeneous_list_int(self) -> None:
        """All integers is valid."""
        source = """
fn main() {
    let xs: List[Int] = [1, 2, 3]
    print(len(xs))
}
"""
        success, stdout, stderr = compile_source(source)
        assert success
    
    def test_homogeneous_list_string(self) -> None:
        """All strings is valid."""
        source = """
fn main() {
    let xs: List[String] = ["a", "b"]
    print(len(xs))
}
"""
        success, stdout, stderr = compile_source(source)
        assert success
    
    def test_heterogeneous_list_error(self) -> None:
        """Mixed types is invalid."""
        source = """
fn main() {
    let xs = [1, "two", 3]
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "type" in stderr.lower() or "mismatch" in stderr.lower()
    
    def test_get_returns_element_type(self) -> None:
        """get(List[Int], Int) returns Int."""
        source = """
fn add_one(x: Int) -> Int {
    x + 1
}

fn main() {
    let xs = [1, 2, 3]
    let y = add_one(get(xs, 0))
    print(y)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "2" in stdout
    
    def test_push_type_mismatch(self) -> None:
        """push with wrong type is error."""
        source = """
fn main() {
    let xs = [1, 2, 3]
    let ys = push(xs, "four")
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "type" in stderr.lower() or "mismatch" in stderr.lower()
    
    def test_get_wrong_index_type(self) -> None:
        """get with non-Int index is error."""
        source = """
fn main() {
    let xs = [1, 2, 3]
    let y = get(xs, "zero")
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "type" in stderr.lower() or "mismatch" in stderr.lower()


# =============================================================================
# 4. Integration with While Loops
# =============================================================================

class TestListWithWhile:
    """Test lists with while loops."""
    
    def test_iterate_with_index(self) -> None:
        """Iterate over list using index."""
        source = """
fn main() {
    let xs = [10, 20, 30]
    let mut i = 0
    while i < len(xs) {
        print(get(xs, i))
        i = i + 1
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "10" in stdout
        assert "20" in stdout
        assert "30" in stdout
    
    def test_sum_list(self) -> None:
        """Sum all elements in a list."""
        source = """
fn main() {
    let xs = [1, 2, 3, 4, 5]
    let mut sum = 0
    let mut i = 0
    while i < len(xs) {
        sum = sum + get(xs, i)
        i = i + 1
    }
    print(sum)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "15" in stdout
    
    def test_find_element(self) -> None:
        """Find element in list."""
        source = """
fn main() {
    let xs = [5, 10, 15, 20]
    let target = 15
    let mut i = 0
    let mut found = false
    while i < len(xs) {
        if get(xs, i) == target {
            found = true
            break
        }
        i = i + 1
    }
    if found {
        print("found at index")
        print(i)
    } else {
        print("not found")
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "found at index" in stdout
        assert "2" in stdout
    
    def test_build_list_with_push(self) -> None:
        """Build list using push in a loop."""
        source = """
fn main() {
    let mut xs = []
    let mut i = 0
    while i < 5 {
        xs = push(xs, i)
        i = i + 1
    }
    print(len(xs))
    print(get(xs, 4))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "5" in stdout
        assert "4" in stdout


# =============================================================================
# 5. Return Type Tests
# =============================================================================

class TestListReturnTypes:
    """Test functions returning lists."""
    
    def test_function_returns_list(self) -> None:
        """Function can return a list."""
        source = """
fn make_list() -> List[Int] {
    [1, 2, 3]
}

fn main() {
    let xs = make_list()
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_function_takes_list(self) -> None:
        """Function can take list parameter."""
        source = """
fn sum_list(xs: List[Int]) -> Int {
    let mut total = 0
    let mut i = 0
    while i < len(xs) {
        total = total + get(xs, i)
        i = i + 1
    }
    total
}

fn main() {
    let result = sum_list([1, 2, 3, 4])
    print(result)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "10" in stdout


# =============================================================================
# 6. Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and corner cases."""
    
    def test_nested_function_calls(self) -> None:
        """Nested list function calls."""
        source = """
fn main() {
    let xs = push(push(push([], 1), 2), 3)
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_list_in_expression(self) -> None:
        """List used in expression context."""
        source = """
fn main() {
    if len([1, 2, 3]) > 2 {
        print("yes")
    } else {
        print("no")
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "yes" in stdout
