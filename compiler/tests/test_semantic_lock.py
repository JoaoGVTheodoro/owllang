"""
Semantic Lock Tests for OwlLang v0.2.4.5-alpha.

These tests lock specific semantic behaviors that must NEVER change.
They serve as regression guards before adding new features (e.g., Structs).

Each test documents:
- The invariant being locked
- Why it matters
- What would break if it changed

If any of these tests fail, it indicates a semantic regression that MUST be fixed.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


# =============================================================================
# Test Helpers
# =============================================================================

def run_cli(*args) -> subprocess.CompletedProcess:
    """Run the owl CLI with given arguments."""
    cmd = [sys.executable, "-m", "owllang.cli"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )


def compile_source(source: str) -> tuple[bool, str, str]:
    """Compile source and return (success, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ow', delete=False) as f:
        f.write(source)
        f.flush()
        result = run_cli("check", f.name)
        Path(f.name).unlink()
        return result.returncode == 0, result.stdout, result.stderr


def run_source(source: str) -> tuple[bool, str, str]:
    """Run source and return (success, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ow', delete=False) as f:
        f.write(source)
        f.flush()
        result = run_cli("run", f.name)
        Path(f.name).unlink()
        return result.returncode == 0, result.stdout, result.stderr


# =============================================================================
# LOCK 1: Immutability Semantics
# =============================================================================

class TestImmutabilityLock:
    """Lock: Variables are immutable by default; assignment to immutable is E0323."""
    
    def test_let_is_immutable(self) -> None:
        """LOCK: `let x = value` creates immutable binding."""
        source = """
fn main() {
    let x = 1
    x = 2
}
"""
        success, stdout, stderr = compile_source(source)
        
        # MUST fail with E0323
        assert not success, "Assignment to `let` variable MUST fail"
        assert "E0323" in stderr, "Assignment to `let` MUST produce E0323"
    
    def test_let_mut_is_mutable(self) -> None:
        """LOCK: `let mut x = value` creates mutable binding."""
        source = """
fn main() {
    let mut x = 1
    x = 2
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        
        # MUST succeed
        assert success, f"Assignment to `let mut` MUST be allowed: {stderr}"
        assert "2" in stdout


# =============================================================================
# LOCK 2: Type System Basics
# =============================================================================

class TestTypeLock:
    """Lock: Core type checking behavior."""
    
    def test_type_mismatch_is_error(self) -> None:
        """LOCK: Assigning wrong type to annotated variable is error."""
        source = """
fn main() {
    let x: Int = "hello"
}
"""
        success, stdout, stderr = compile_source(source)
        
        # MUST fail with type error
        assert not success, "Type mismatch MUST fail"
        assert "Type mismatch" in stderr, "Type mismatch MUST be reported"
    
    def test_function_return_type_checked(self) -> None:
        """LOCK: Function return type mismatch is error."""
        source = """
fn f() -> Int {
    "not an int"
}
"""
        success, stdout, stderr = compile_source(source)
        
        # MUST fail
        assert not success, "Return type mismatch MUST fail"


# =============================================================================
# LOCK 3: Option and Result Semantics
# =============================================================================

class TestOptionResultLock:
    """Lock: Option and Result type handling."""
    
    def test_match_option_requires_both_arms(self) -> None:
        """LOCK: Match on Option must cover Some and None."""
        source = """
fn f(opt: Option[Int]) -> Int {
    match opt {
        Some(x) => x
    }
}
"""
        success, stdout, stderr = compile_source(source)
        
        # MUST fail with non-exhaustive match
        assert not success, "Non-exhaustive Option match MUST fail"
        assert "E0503" in stderr, "Non-exhaustive match MUST produce E0503"
    
    def test_match_result_requires_both_arms(self) -> None:
        """LOCK: Match on Result must cover Ok and Err."""
        source = """
fn f(res: Result[Int, String]) -> Int {
    match res {
        Ok(x) => x
    }
}
"""
        success, stdout, stderr = compile_source(source)
        
        # MUST fail with non-exhaustive match
        assert not success, "Non-exhaustive Result match MUST fail"
        assert "E0503" in stderr, "Non-exhaustive match MUST produce E0503"
    
    def test_try_operator_requires_result_return(self) -> None:
        """LOCK: `?` operator only valid in functions returning Result."""
        source = """
fn f(res: Result[Int, String]) {
    let x = res?
}
"""
        success, stdout, stderr = compile_source(source)
        
        # MUST fail
        assert not success, "Try operator in non-Result function MUST fail"
        assert "E0312" in stderr, "Try outside Result fn MUST produce E0312"


# =============================================================================
# LOCK 4: Control Flow Semantics
# =============================================================================

class TestControlFlowLock:
    """Lock: Control flow construct semantics."""
    
    def test_break_outside_loop_is_error(self) -> None:
        """LOCK: `break` outside loop is error E0505."""
        source = """
fn main() {
    break
}
"""
        success, stdout, stderr = compile_source(source)
        
        assert not success, "Break outside loop MUST fail"
        assert "E0505" in stderr, "Break outside loop MUST produce E0505"
    
    def test_continue_outside_loop_is_error(self) -> None:
        """LOCK: `continue` outside loop is error E0506."""
        source = """
fn main() {
    continue
}
"""
        success, stdout, stderr = compile_source(source)
        
        assert not success, "Continue outside loop MUST fail"
        assert "E0506" in stderr, "Continue outside loop MUST produce E0506"
    
    def test_while_condition_must_be_bool(self) -> None:
        """LOCK: While condition must be Bool."""
        source = """
fn main() {
    while 1 {
        break
    }
}
"""
        success, stdout, stderr = compile_source(source)
        
        # MUST fail with type error
        assert not success, "While with non-Bool condition MUST fail"
    
    def test_if_else_is_expression(self) -> None:
        """LOCK: if/else with both branches is an expression that returns value."""
        source = """
fn classify(n: Int) -> String {
    if n > 0 {
        "positive"
    } else {
        "zero or negative"
    }
}

fn main() {
    print(classify(5))
}
"""
        success, stdout, stderr = run_source(source)
        
        # MUST succeed
        assert success, f"if/else as expression MUST work: {stderr}"
        assert "positive" in stdout


# =============================================================================
# LOCK 5: Scope Semantics
# =============================================================================

class TestScopeLock:
    """Lock: Scoping and visibility rules."""
    
    def test_undefined_variable_is_error(self) -> None:
        """LOCK: Using undefined variable is error."""
        source = """
fn main() {
    print(undefined_var)
}
"""
        success, stdout, stderr = compile_source(source)
        
        assert not success, "Undefined variable MUST fail"
        assert "Undefined variable" in stderr, "Undefined variable MUST be reported"
    
    def test_variable_visible_after_declaration(self) -> None:
        """LOCK: Variable is visible after its declaration."""
        source = """
fn main() {
    let x = 42
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, "Variable after declaration MUST be visible"
        assert "42" in stdout
    
    def test_shadowing_is_allowed(self) -> None:
        """LOCK: Inner scope can shadow outer variable."""
        source = """
fn main() {
    let x = 1
    if true {
        let x = 2
        print(x)
    }
}
"""
        success, stdout, stderr = run_source(source)
        
        # MUST succeed and inner x is printed
        assert success, f"Shadowing MUST be allowed: {stderr}"
        assert "2" in stdout


# =============================================================================
# LOCK 6: Warning Semantics
# =============================================================================

class TestWarningLock:
    """Lock: Warning behavior."""
    
    def test_unused_variable_warns(self) -> None:
        """LOCK: Unused variable produces warning W0101."""
        source = """
fn main() {
    let unused = 42
}
"""
        success, stdout, stderr = compile_source(source)
        
        # Should succeed but with warning
        assert success, "Unused variable should still compile"
        assert "W0101" in stderr, "Unused variable MUST produce W0101"
    
    def test_underscore_prefix_suppresses_warning(self) -> None:
        """LOCK: Underscore prefix suppresses unused warnings."""
        source = """
fn main() {
    let _unused = 42
}
"""
        success, stdout, stderr = compile_source(source)
        
        assert success, "Should compile"
        assert "W0101" not in stderr, "Underscore prefix MUST suppress W0101"
    
    def test_unreachable_code_warns(self) -> None:
        """LOCK: Code after return is unreachable, produces warning."""
        source = """
fn f() -> Int {
    return 1
    let x = 2
    x
}
"""
        success, stdout, stderr = compile_source(source)
        
        # Should succeed (unreachable is warning, not error)
        assert "W0201" in stderr, "Unreachable code MUST produce W0201"


# =============================================================================
# LOCK 7: Expression vs Statement
# =============================================================================

class TestExpressionStatementLock:
    """Lock: Expression/statement classification."""
    
    def test_match_is_always_expression(self) -> None:
        """LOCK: match always produces a value."""
        source = """
fn f(opt: Option[Int]) -> Int {
    let x = match opt {
        Some(n) => n,
        None => 0
    }
    x
}
"""
        success, stdout, stderr = compile_source(source)
        
        assert success, f"match as expression MUST work: {stderr}"
    
    def test_result_ignored_warns(self) -> None:
        """LOCK: Ignoring Result value in statement position warns."""
        source = """
fn get_result() -> Result[Int, String] {
    Ok(42)
}

fn main() {
    get_result()
}
"""
        success, stdout, stderr = compile_source(source)
        
        # Should warn about ignored Result
        assert "W0304" in stderr, "Ignored Result MUST produce W0304"


# =============================================================================
# LOCK 8: Built-in Functions
# =============================================================================

class TestBuiltinLock:
    """Lock: Built-in function availability and types."""
    
    def test_print_exists(self) -> None:
        """LOCK: print() is a built-in function."""
        source = """
fn main() {
    print("hello")
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, "print() MUST be available"
        assert "hello" in stdout
    
    def test_len_exists(self) -> None:
        """LOCK: len() is a built-in function."""
        source = """
fn main() {
    let xs = [1, 2, 3]
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"len() MUST be available: {stderr}"
        assert "3" in stdout
    
    def test_range_exists(self) -> None:
        """LOCK: range() is a built-in function."""
        source = """
fn main() {
    let xs = range(0, 3)
    print(len(xs))
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"range() MUST be available: {stderr}"
        assert "3" in stdout
    
    def test_get_exists(self) -> None:
        """LOCK: get() is a built-in function."""
        source = """
fn main() {
    let xs = [10, 20, 30]
    print(get(xs, 1))
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"get() MUST be available: {stderr}"
        assert "20" in stdout
    
    def test_push_exists(self) -> None:
        """LOCK: push() is a built-in function."""
        source = """
fn main() {
    let xs = [1, 2]
    let ys = push(xs, 3)
    print(len(ys))
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"push() MUST be available: {stderr}"
        assert "3" in stdout
    
    def test_is_empty_exists(self) -> None:
        """LOCK: is_empty() is a built-in function."""
        source = """
fn main() {
    let xs: List[Int] = []
    if is_empty(xs) {
        print("empty")
    }
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"is_empty() MUST be available: {stderr}"
        assert "empty" in stdout


# =============================================================================
# LOCK 9: Implicit Return
# =============================================================================

class TestImplicitReturnLock:
    """Lock: Last expression is implicit return value."""
    
    def test_last_expression_is_return(self) -> None:
        """LOCK: Last expression in function is returned."""
        source = """
fn add(a: Int, b: Int) -> Int {
    a + b
}

fn main() {
    print(add(1, 2))
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"Implicit return MUST work: {stderr}"
        assert "3" in stdout
    
    def test_explicit_return_works(self) -> None:
        """LOCK: Explicit return also works."""
        source = """
fn f() -> Int {
    return 42
}

fn main() {
    print(f())
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"Explicit return MUST work: {stderr}"
        assert "42" in stdout


# =============================================================================
# LOCK 10: Diagnostic Code Stability
# =============================================================================

class TestDiagnosticCodeLock:
    """Lock: Specific error codes for specific conditions."""
    
    def test_e0301_type_mismatch(self) -> None:
        """LOCK: E0301 is type mismatch."""
        from owllang.diagnostics import ErrorCode
        assert ErrorCode.TYPE_MISMATCH.value == "E0301"
    
    def test_e0302_undefined_variable(self) -> None:
        """LOCK: E0302 is undefined variable."""
        from owllang.diagnostics import ErrorCode
        assert ErrorCode.UNDEFINED_VARIABLE.value == "E0302"
    
    def test_e0323_assignment_to_immutable(self) -> None:
        """LOCK: E0323 is assignment to immutable."""
        from owllang.diagnostics import ErrorCode
        assert ErrorCode.ASSIGNMENT_TO_IMMUTABLE.value == "E0323"
    
    def test_e0503_non_exhaustive_match(self) -> None:
        """LOCK: E0503 is non-exhaustive match."""
        from owllang.diagnostics import ErrorCode
        assert ErrorCode.NON_EXHAUSTIVE_MATCH.value == "E0503"
    
    def test_e0505_break_outside_loop(self) -> None:
        """LOCK: E0505 is break outside loop."""
        from owllang.diagnostics import ErrorCode
        assert ErrorCode.BREAK_OUTSIDE_LOOP.value == "E0505"
    
    def test_e0506_continue_outside_loop(self) -> None:
        """LOCK: E0506 is continue outside loop."""
        from owllang.diagnostics import ErrorCode
        assert ErrorCode.CONTINUE_OUTSIDE_LOOP.value == "E0506"
    
    def test_w0101_unused_variable(self) -> None:
        """LOCK: W0101 is unused variable."""
        from owllang.diagnostics import WarningCode
        assert WarningCode.UNUSED_VARIABLE.value == "W0101"
    
    def test_w0201_unreachable_code(self) -> None:
        """LOCK: W0201 is unreachable code."""
        from owllang.diagnostics import WarningCode
        assert WarningCode.UNREACHABLE_CODE.value == "W0201"


# =============================================================================
# LOCK 11: Loop Constructs
# =============================================================================

class TestLoopLock:
    """Lock: Loop construct semantics."""
    
    def test_while_loop_works(self) -> None:
        """LOCK: while loop with condition."""
        source = """
fn main() {
    let mut i = 0
    while i < 3 {
        print(i)
        i = i + 1
    }
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"while loop MUST work: {stderr}"
        assert "0" in stdout
        assert "1" in stdout
        assert "2" in stdout
    
    def test_for_in_loop_works(self) -> None:
        """LOCK: for-in loop over list."""
        source = """
fn main() {
    let xs = [10, 20, 30]
    for x in xs {
        print(x)
    }
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"for-in loop MUST work: {stderr}"
        assert "10" in stdout
        assert "20" in stdout
        assert "30" in stdout
    
    def test_loop_infinite_with_break(self) -> None:
        """LOCK: loop runs until break."""
        source = """
fn main() {
    let mut i = 0
    loop {
        print(i)
        i = i + 1
        if i >= 3 {
            break
        }
    }
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"loop with break MUST work: {stderr}"
        assert "0" in stdout
        assert "2" in stdout


# =============================================================================
# LOCK 12: Python Interop
# =============================================================================

class TestPythonInteropLock:
    """Lock: Python interop syntax."""
    
    def test_python_import_works(self) -> None:
        """LOCK: from python import module works."""
        source = """
from python import math

fn main() {
    let x = math.sqrt(16.0)
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"Python import MUST work: {stderr}"
        assert "4" in stdout
    
    def test_python_from_import_works(self) -> None:
        """LOCK: from python.module import name works."""
        source = """
from python.math import floor

fn main() {
    let x = floor(3.7)
    print(x)
}
"""
        success, stdout, stderr = run_source(source)
        
        assert success, f"Python from import MUST work: {stderr}"
        assert "3" in stdout
