"""
Tests for OwlLang v0.2.1-alpha features.

Features tested:
1. break statement
2. continue statement
3. Error diagnostics for break/continue outside loop
4. Interaction with return
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
# 1. Break Statement Tests
# =============================================================================

class TestBreakStatement:
    """Test break statement functionality."""
    
    def test_break_exits_loop(self) -> None:
        """break exits the loop immediately."""
        source = """
fn main() {
    let mut i = 0
    while i < 10 {
        i = i + 1
        if i == 5 {
            break
        }
        print(i)
    }
    print("done")
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "1" in stdout
        assert "2" in stdout
        assert "3" in stdout
        assert "4" in stdout
        assert "5" not in stdout
        assert "done" in stdout
    
    def test_break_in_nested_loop(self) -> None:
        """break only exits the innermost loop."""
        source = """
fn main() {
    let mut i = 0
    while i < 3 {
        let mut j = 0
        while j < 3 {
            if j == 1 {
                break
            }
            print(j)
            j = j + 1
        }
        i = i + 1
    }
    print("done")
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        # Should print 0 three times (once per outer iteration, then break)
        assert stdout.count("0") == 3
        assert "done" in stdout
    
    def test_break_outside_loop_error(self) -> None:
        """break outside of loop is an error."""
        source = """
fn main() {
    break
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "E0505" in stderr
        assert "outside of loop" in stderr
    
    def test_break_outside_loop_hint(self) -> None:
        """Error message includes helpful hint."""
        source = """
fn main() {
    break
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "while" in stderr  # hint mentions while loops


# =============================================================================
# 2. Continue Statement Tests
# =============================================================================

class TestContinueStatement:
    """Test continue statement functionality."""
    
    def test_continue_skips_iteration(self) -> None:
        """continue skips to next iteration."""
        source = """
fn main() {
    let mut i = 0
    while i < 5 {
        i = i + 1
        if i == 3 {
            continue
        }
        print(i)
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "1" in stdout
        assert "2" in stdout
        assert "3" not in stdout  # skipped
        assert "4" in stdout
        assert "5" in stdout
    
    def test_continue_in_nested_loop(self) -> None:
        """continue only affects the innermost loop."""
        source = """
fn main() {
    let mut i = 0
    while i < 2 {
        let mut j = 0
        while j < 3 {
            j = j + 1
            if j == 2 {
                continue
            }
            print(j)
        }
        i = i + 1
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        # Should print 1, 3 twice (skip 2)
        assert stdout.count("1") == 2
        assert stdout.count("3") == 2
        assert "2" not in stdout
    
    def test_continue_outside_loop_error(self) -> None:
        """continue outside of loop is an error."""
        source = """
fn main() {
    continue
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "E0506" in stderr
        assert "outside of loop" in stderr
    
    def test_continue_outside_loop_hint(self) -> None:
        """Error message includes helpful hint."""
        source = """
fn main() {
    continue
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "while" in stderr  # hint mentions while loops


# =============================================================================
# 3. Interaction with Return
# =============================================================================

class TestLoopControlWithReturn:
    """Test break/continue interaction with return."""
    
    def test_return_inside_loop(self) -> None:
        """return works normally inside a loop."""
        source = """
fn find_first_even(n: Int) -> Int {
    let mut i = 1
    while i <= n {
        if i % 2 == 0 {
            return i
        }
        i = i + 1
    }
    0
}

fn main() {
    print(find_first_even(10))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "2" in stdout
    
    def test_break_and_return_in_same_loop(self) -> None:
        """break and return can both be used in the same loop."""
        source = """
fn search(target: Int) -> Int {
    let mut i = 0
    while i < 100 {
        if i == target {
            return i
        }
        if i > 50 {
            break
        }
        i = i + 1
    }
    -1
}

fn main() {
    print(search(25))
    print(search(75))
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "25" in stdout  # found
        assert "-1" in stdout  # not found, broke out


# =============================================================================
# 4. Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases for break/continue."""
    
    def test_break_in_if_inside_loop(self) -> None:
        """break inside if inside loop works."""
        source = """
fn main() {
    let mut i = 0
    while true {
        i = i + 1
        if i >= 3 {
            break
        }
    }
    print(i)
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "3" in stdout
    
    def test_continue_at_end_of_loop(self) -> None:
        """continue at end of loop body works (is a no-op)."""
        source = """
fn main() {
    let mut i = 0
    while i < 3 {
        print(i)
        i = i + 1
        continue
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "0" in stdout
        assert "1" in stdout
        assert "2" in stdout
    
    def test_break_in_else_inside_loop(self) -> None:
        """break in else branch inside loop works."""
        source = """
fn main() {
    let mut i = 0
    while i < 10 {
        if i < 3 {
            print(i)
        } else {
            break
        }
        i = i + 1
    }
    print("done")
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        assert "0" in stdout
        assert "1" in stdout
        assert "2" in stdout
        assert "done" in stdout
    
    def test_break_in_if_outside_loop_error(self) -> None:
        """break in if but outside loop is an error."""
        source = """
fn main() {
    if true {
        break
    }
}
"""
        success, stdout, stderr = compile_source(source)
        assert not success
        assert "E0505" in stderr
    
    def test_multiple_breaks_in_loop(self) -> None:
        """Multiple break statements in same loop compile fine."""
        source = """
fn main() {
    let mut i = 0
    while i < 10 {
        if i == 3 {
            break
        }
        if i == 7 {
            break
        }
        print(i)
        i = i + 1
    }
}
"""
        success, stdout, stderr = run_source(source)
        assert success
        # Only 0, 1, 2 should be printed
        assert "0" in stdout
        assert "1" in stdout
        assert "2" in stdout
        assert "3" not in stdout
