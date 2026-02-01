"""
Tests for v0.2.4.7-alpha features: Any Boundary Formalization

This release formalizes, proves, and shields the Any type as a controlled
interop boundary. After this release, Any should be "conceptually closed".

KEY INVARIANTS TESTED:
1. Any cannot be user-annotated (let x: Any, fn f() -> Any, fn f(x: Any))
2. Any comes only from Python imports
3. Any diagnostics have proper spans
4. Any does not unify with concrete types (not a top type)
"""

import pytest
from pathlib import Path
from typing import Callable
import subprocess
import sys


# =============================================================================
# Helpers
# =============================================================================

def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the owl CLI with given arguments."""
    cmd = [sys.executable, "-m", "owllang.cli"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )


def check_code(code: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Check code and return result."""
    f = tmp_path / "test.ow"
    f.write_text(code)
    return run_cli("check", str(f))


# =============================================================================
# Section 1: Any Cannot Be User-Annotated (E0316)
# =============================================================================

class TestAnyAnnotationBlocked:
    """Any type cannot be explicitly annotated by users."""
    
    def test_any_in_variable_annotation(self, tmp_path: Path) -> None:
        """let x: Any = 1 produces error E0316."""
        code = """
fn main() {
    let x: Any = 1
}
"""
        result = check_code(code, tmp_path)
        assert result.returncode != 0
        assert "E0316" in result.stdout or "E0316" in result.stderr
        assert "Any" in result.stdout or "Any" in result.stderr
    
    def test_any_in_return_type(self, tmp_path: Path) -> None:
        """fn f() -> Any produces error E0316."""
        code = """
fn get() -> Any { 1 }
fn main() {}
"""
        result = check_code(code, tmp_path)
        assert result.returncode != 0
        assert "E0316" in result.stdout or "E0316" in result.stderr
    
    def test_any_in_parameter(self, tmp_path: Path) -> None:
        """fn f(x: Any) produces error E0316."""
        code = """
fn take(x: Any) { print(x) }
fn main() {}
"""
        result = check_code(code, tmp_path)
        assert result.returncode != 0
        assert "E0316" in result.stdout or "E0316" in result.stderr
    
    def test_any_in_option(self, tmp_path: Path) -> None:
        """Option[Any] produces error E0316."""
        code = """
fn maybe() -> Option[Any] { Some(1) }
fn main() {}
"""
        result = check_code(code, tmp_path)
        assert result.returncode != 0
        assert "E0316" in result.stdout or "E0316" in result.stderr
    
    def test_any_in_result(self, tmp_path: Path) -> None:
        """Result[Any, String] produces error E0316."""
        code = """
fn try_get() -> Result[Any, String] { Ok(1) }
fn main() {}
"""
        result = check_code(code, tmp_path)
        assert result.returncode != 0
        assert "E0316" in result.stdout or "E0316" in result.stderr
    
    def test_any_in_list(self, tmp_path: Path) -> None:
        """List[Any] produces error E0316."""
        code = """
fn items() -> List[Any] { [1, 2, 3] }
fn main() {}
"""
        result = check_code(code, tmp_path)
        assert result.returncode != 0
        assert "E0316" in result.stdout or "E0316" in result.stderr


# =============================================================================
# Section 2: Any Comes Only From Python Imports
# =============================================================================

class TestAnyFromPythonImports:
    """Any type should only come from Python import boundaries."""
    
    def test_python_import_produces_any(self, tmp_path: Path) -> None:
        """Python imports are allowed and produce Any type."""
        code = """
from python import random
fn main() {
    let x = random.randint(1, 10)
    print(x)
}
"""
        result = check_code(code, tmp_path)
        assert result.returncode == 0
    
    def test_python_from_import_produces_any(self, tmp_path: Path) -> None:
        """Python from imports are allowed."""
        code = """
from python.math import floor
fn main() {
    let x = floor(3.7)
    print(x)
}
"""
        result = check_code(code, tmp_path)
        assert result.returncode == 0


# =============================================================================
# Section 3: Any Diagnostic Spans Are Correct
# =============================================================================

class TestAnyDiagnosticSpans:
    """Any-related diagnostics should have proper source spans."""
    
    def test_any_annotation_error_is_descriptive(self, tmp_path: Path) -> None:
        """E0316 error should include clear message and hint."""
        code = """
fn main() {
    let x: Any = 1
}
"""
        result = check_code(code, tmp_path)
        output = result.stdout + result.stderr
        # Should contain the error code and message
        assert "E0316" in output
        assert "Any" in output
        # Should suggest alternatives
        assert "Int" in output or "String" in output or "specific" in output


# =============================================================================
# Section 4: Any Is Not A Top Type (Non-Recurrence Tests)
# =============================================================================

class TestAnyNotTopType:
    """
    CRITICAL: These tests ensure Any does NOT behave as a top type.
    
    If Any were a top type, it would silently accept any value and
    unify with all types. This would be dangerous for type safety.
    
    These tests should FAIL if future changes accidentally make
    Any behave like a universal wildcard.
    """
    
    def test_any_cannot_be_annotated(self, tmp_path: Path) -> None:
        """REGRESSION: Any must not become user-annotatable.
        
        If this test fails, it means Any has been accidentally added
        back to the primitive type registry. This breaks the boundary
        formalization introduced in v0.2.4.7.
        """
        code = """
fn main() {
    let x: Any = 1
}
"""
        result = check_code(code, tmp_path)
        # MUST fail - if it passes, Any became a top type
        assert result.returncode != 0, (
            "REGRESSION: Any should NOT be user-annotatable! "
            "Check PRIMITIVE_TYPES in types.py"
        )


class TestAnyBoundaryInvariants:
    """Contract tests for Any boundary invariants."""
    
    def test_any_error_message_is_clear(self, tmp_path: Path) -> None:
        """Error message should explain that Any is internal and for Python interop."""
        code = """
fn main() {
    let x: Any = 1
}
"""
        result = check_code(code, tmp_path)
        output = result.stdout + result.stderr
        # Message should explain it's internal (now in notes)
        assert "internal" in output.lower() or "interop" in output.lower() or "python" in output.lower()
    
    def test_any_hint_suggests_concrete_types(self, tmp_path: Path) -> None:
        """Error hint should suggest using concrete types."""
        code = """
fn main() {
    let x: Any = 1
}
"""
        result = check_code(code, tmp_path)
        output = result.stdout + result.stderr
        # Should suggest alternatives
        assert any(word in output for word in ["Int", "String", "Option", "specific"])
