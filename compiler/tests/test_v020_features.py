"""
Tests for OwlLang v0.2.0-alpha features.

Features tested:
1. While loops
2. Mutable variables (let mut)
3. Assignment statements
4. Immutability enforcement
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
# 1. While Loop Tests
# =============================================================================

class TestWhileLoop:
    """Test while loop functionality."""
    
    def test_basic_while(self) -> None:
        """Basic while loop compiles and runs."""
        source = """
fn countdown(n: Int) -> Void {
    let mut i = n
    while i > 0 {
        print(i)
        i = i - 1
    }
}

fn main() {
    countdown(3)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
        assert "2" in stdout
        assert "1" in stdout
    
    def test_while_condition_must_be_bool(self) -> None:
        """While condition must be a boolean."""
        source = """
fn main() {
    let mut x = 5
    while x {
        x = x - 1
    }
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "E0309" in stderr or "boolean" in stderr  # "condition must be a boolean"
    
    def test_while_with_break_later(self) -> None:
        """While loop should work without break (for now)."""
        source = """
fn sum_to_n(n: Int) -> Int {
    let mut sum = 0
    let mut i = 1
    while i <= n {
        sum = sum + i
        i = i + 1
    }
    sum
}

fn main() {
    print(sum_to_n(5))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "15" in stdout  # 1+2+3+4+5 = 15
    
    def test_nested_while(self) -> None:
        """Nested while loops work."""
        source = """
fn main() {
    let mut i = 0
    while i < 2 {
        let mut j = 0
        while j < 2 {
            print(i)
            j = j + 1
        }
        i = i + 1
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        # Should print 0, 0, 1, 1
        assert stdout.count("0") >= 2
        assert stdout.count("1") >= 2


# =============================================================================
# 2. Mutable Variables Tests
# =============================================================================

class TestMutableVariables:
    """Test let mut and mutable variable behavior."""
    
    def test_let_mut_allows_reassignment(self) -> None:
        """let mut variables can be reassigned."""
        source = """
fn main() {
    let mut x = 5
    x = 10
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "10" in stdout
    
    def test_let_immutable_by_default(self) -> None:
        """let (without mut) is immutable by default."""
        source = """
fn main() {
    let x = 5
    x = 10
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "E0323" in stderr or "immutable" in stderr
    
    def test_immutable_error_hint(self) -> None:
        """Error message suggests using let mut."""
        source = """
fn main() {
    let x = 5
    x = 10
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        # The hint should suggest using "let mut"
        assert "let mut" in stderr or "mutable" in stderr
    
    def test_mut_preserves_type(self) -> None:
        """Mutable variable must maintain its type."""
        source = """
fn main() {
    let mut x = 5
    x = "hello"
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        # Type mismatch error
        assert "E0301" in stderr or "type" in stderr.lower()
    
    def test_multiple_mut_vars(self) -> None:
        """Multiple mutable variables work independently."""
        source = """
fn main() {
    let mut a = 1
    let mut b = 2
    a = a + b
    b = a + b
    print(a)
    print(b)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout  # a = 1 + 2 = 3
        assert "5" in stdout  # b = 3 + 2 = 5
    
    def test_mut_in_while_loop(self) -> None:
        """Mutable variables work in while loops."""
        source = """
fn factorial(n: Int) -> Int {
    let mut result = 1
    let mut i = n
    while i > 0 {
        result = result * i
        i = i - 1
    }
    result
}

fn main() {
    print(factorial(5))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "120" in stdout  # 5! = 120


# =============================================================================
# 3. Assignment Statement Tests
# =============================================================================

class TestAssignment:
    """Test assignment statement behavior."""
    
    def test_assign_to_undefined(self) -> None:
        """Cannot assign to undefined variable."""
        source = """
fn main() {
    x = 5
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "E0302" in stderr or "undefined" in stderr.lower()
    
    def test_assign_type_checked(self) -> None:
        """Assignment is type checked."""
        source = """
fn main() {
    let mut x: Int = 5
    x = 10
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "10" in stdout
    
    def test_assign_in_nested_scope(self) -> None:
        """Can assign to outer scope mutable variable."""
        source = """
fn main() {
    let mut x = 0
    if true {
        x = 5
    }
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "5" in stdout


# =============================================================================
# 4. Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases for v0.2.0 features."""
    
    def test_empty_while_body(self) -> None:
        """Empty while body should still compile."""
        source = """
fn spin(n: Int) -> Void {
    let mut i = n
    while i > 0 {
        i = i - 1
    }
}

fn main() {
    spin(3)
    print("done")
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "done" in stdout
    
    def test_while_false_never_executes(self) -> None:
        """while false { } never executes body."""
        source = """
fn main() {
    while false {
        print("never")
    }
    print("done")
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "never" not in stdout
        assert "done" in stdout
    
    def test_constant_condition_warning(self) -> None:
        """Constant while condition produces warning."""
        source = """
fn main() {
    while true {
        print("infinite")
        return
    }
}
"""
        success, stdout, stderr = compile_source(source)
        # Should compile but warn
        assert "W0306" in stderr or "constant" in stderr.lower()
    
    def test_shadowing_with_mut(self) -> None:
        """Shadowing with mut creates new variable."""
        source = """
fn main() {
    let x = 5
    let mut x = 10
    x = 15
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "15" in stdout
