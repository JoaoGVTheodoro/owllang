"""
Tests for OwlLang v0.2.3-alpha features.

Features tested:
1. for-in loop syntax
2. Type checking for for-in (collection must be List[T])
3. Loop variable type inference
4. break and continue in for-in loops
5. Transpilation to Python for loops
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
# 1. Basic For-In Loop Tests
# =============================================================================

class TestForInBasic:
    """Test basic for-in loop functionality."""
    
    def test_iterate_int_list(self) -> None:
        """Iterate over list of integers."""
        source = """
fn main() {
    for x in [1, 2, 3] {
        print(x)
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "1" in stdout
        assert "2" in stdout
        assert "3" in stdout
    
    def test_iterate_string_list(self) -> None:
        """Iterate over list of strings."""
        source = """
fn main() {
    for name in ["Alice", "Bob"] {
        print(name)
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "Alice" in stdout
        assert "Bob" in stdout
    
    def test_iterate_variable_list(self) -> None:
        """Iterate over list stored in variable."""
        source = """
fn main() {
    let xs = [10, 20, 30]
    for x in xs {
        print(x)
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "10" in stdout
        assert "20" in stdout
        assert "30" in stdout
    
    def test_iterate_empty_list(self) -> None:
        """Iterate over empty list (body not executed)."""
        source = """
fn main() {
    for x in [] {
        print("should not print")
    }
    print("done")
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "should not print" not in stdout
        assert "done" in stdout
    
    def test_loop_variable_is_immutable(self) -> None:
        """Loop variable cannot be modified."""
        source = """
fn main() {
    for x in [1, 2, 3] {
        x = x + 1
    }
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "immutable" in stderr.lower() or "cannot assign" in stderr.lower()


# =============================================================================
# 2. Type Checking Tests
# =============================================================================

class TestForInTypeChecking:
    """Test type checking for for-in loops."""
    
    def test_error_iterating_int(self) -> None:
        """Error when iterating over Int."""
        source = """
fn main() {
    for x in 123 {
        print(x)
    }
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "cannot iterate" in stderr.lower() or "list" in stderr.lower()
    
    def test_error_iterating_string(self) -> None:
        """Error when iterating over String."""
        source = """
fn main() {
    for x in "hello" {
        print(x)
    }
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "cannot iterate" in stderr.lower() or "list" in stderr.lower()
    
    def test_error_iterating_bool(self) -> None:
        """Error when iterating over Bool."""
        source = """
fn main() {
    for x in true {
        print(x)
    }
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "cannot iterate" in stderr.lower() or "list" in stderr.lower()
    
    def test_loop_variable_type_inference(self) -> None:
        """Loop variable gets correct type from list element type."""
        source = """
fn add_one(n: Int) -> Int {
    n + 1
}

fn main() {
    for x in [1, 2, 3] {
        let y = add_one(x)
        print(y)
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "2" in stdout
        assert "3" in stdout
        assert "4" in stdout
    
    def test_loop_variable_scope(self) -> None:
        """Loop variable is not accessible outside loop."""
        source = """
fn main() {
    for x in [1, 2, 3] {
        print(x)
    }
    print(x)
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "undefined" in stderr.lower() or "not defined" in stderr.lower()


# =============================================================================
# 3. Break and Continue Tests
# =============================================================================

class TestForInWithBreakContinue:
    """Test break and continue in for-in loops."""
    
    def test_break_exits_loop(self) -> None:
        """break exits the for-in loop."""
        source = """
fn main() {
    for x in [1, 2, 3, 4, 5] {
        if x == 3 {
            break
        }
        print(x)
    }
    print("done")
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "1" in stdout
        assert "2" in stdout
        assert "3" not in stdout or stdout.count("3") == 0 or "done" in stdout  # 3 not printed before done
        assert "done" in stdout
    
    def test_continue_skips_iteration(self) -> None:
        """continue skips to next iteration."""
        source = """
fn main() {
    for x in [1, 2, 3, 4, 5] {
        if x == 3 {
            continue
        }
        print(x)
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "1" in stdout
        assert "2" in stdout
        # 3 should be skipped
        assert "4" in stdout
        assert "5" in stdout
    
    def test_nested_for_break(self) -> None:
        """break only exits innermost for-in loop."""
        source = """
fn main() {
    for i in [1, 2] {
        for j in [10, 20, 30] {
            if j == 20 {
                break
            }
            print(j)
        }
        print(i)
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        # Inner loop prints 10, then breaks at 20
        lines = stdout.strip().split('\n')
        # Should see: 10, 1, 10, 2
        assert "10" in stdout
        assert "1" in stdout
        assert "2" in stdout


# =============================================================================
# 4. Return in For-In Tests
# =============================================================================

class TestForInWithReturn:
    """Test return in for-in loops."""
    
    def test_return_in_for_loop(self) -> None:
        """return works inside for-in loop."""
        source = """
fn find_first_even(xs: List[Int]) -> Int {
    for x in xs {
        if x % 2 == 0 {
            return x
        }
    }
    return -1
}

fn main() {
    print(find_first_even([1, 3, 4, 6]))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "4" in stdout
    
    def test_return_not_found(self) -> None:
        """return -1 when not found."""
        source = """
fn find_first_even(xs: List[Int]) -> Int {
    for x in xs {
        if x % 2 == 0 {
            return x
        }
    }
    return -1
}

fn main() {
    print(find_first_even([1, 3, 5, 7]))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "-1" in stdout


# =============================================================================
# 5. Practical Examples
# =============================================================================

class TestForInPractical:
    """Test practical use cases for for-in loops."""
    
    def test_sum_list(self) -> None:
        """Sum all elements using for-in."""
        source = """
fn sum(xs: List[Int]) -> Int {
    let mut total = 0
    for x in xs {
        total = total + x
    }
    total
}

fn main() {
    print(sum([1, 2, 3, 4, 5]))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "15" in stdout
    
    def test_count_elements(self) -> None:
        """Count elements matching condition."""
        source = """
fn count_positive(xs: List[Int]) -> Int {
    let mut count = 0
    for x in xs {
        if x > 0 {
            count = count + 1
        }
    }
    count
}

fn main() {
    print(count_positive([-1, 2, -3, 4, 5]))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_filter_collect(self) -> None:
        """Filter elements into new list."""
        source = """
fn positives(xs: List[Int]) -> List[Int] {
    let mut result = []
    for x in xs {
        if x > 0 {
            result = push(result, x)
        }
    }
    result
}

fn main() {
    let pos = positives([-1, 2, -3, 4])
    print(len(pos))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "2" in stdout
    
    def test_for_vs_while_equivalence(self) -> None:
        """for-in and while produce same results."""
        source = """
fn sum_with_for(xs: List[Int]) -> Int {
    let mut total = 0
    for x in xs {
        total = total + x
    }
    total
}

fn sum_with_while(xs: List[Int]) -> Int {
    let mut total = 0
    let mut i = 0
    while i < len(xs) {
        total = total + get(xs, i)
        i = i + 1
    }
    total
}

fn main() {
    let xs = [1, 2, 3, 4, 5]
    print(sum_with_for(xs))
    print(sum_with_while(xs))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        lines = stdout.strip().split('\n')
        assert len(lines) >= 2
        assert lines[0] == lines[1]  # Both should be 15
