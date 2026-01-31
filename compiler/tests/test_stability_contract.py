"""
Stability Contract Tests for OwlLang v0.1.6-alpha.

These tests verify the stability guarantees defined in docs/STABILITY.md.
Any breaking changes to these tests require a major version bump.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


# =============================================================================
# Helpers
# =============================================================================

def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the owllang CLI with given arguments."""
    cmd = [sys.executable, "-m", "owllang.cli"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )


# =============================================================================
# 1. CLI Interface Contract
# =============================================================================

class TestCliInterfaceContract:
    """Test stable CLI interface (STABILITY.md: 🟢 Stable)."""
    
    def test_compile_command_exists(self, tmp_path: Path) -> None:
        """owl compile <file> is a stable command."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("compile", str(f))
        # Should not fail with "unknown command"
        assert "unknown" not in result.stderr.lower()
    
    def test_run_command_exists(self, tmp_path: Path) -> None:
        """owl run <file> is a stable command."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() { print(\"hello\") }\n")
        result = run_cli("run", str(f))
        assert "unknown" not in result.stderr.lower()
    
    def test_check_command_exists(self, tmp_path: Path) -> None:
        """owl check <file> is a stable command."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f))
        assert "unknown" not in result.stderr.lower()
    
    def test_version_flag_exists(self) -> None:
        """owl --version is a stable flag."""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "owllang" in result.stdout.lower() or "owllang" in result.stderr.lower()
    
    def test_json_flag_exists(self, tmp_path: Path) -> None:
        """owl check --json is a stable flag."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f), "--json")
        # Should produce valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, dict)


# =============================================================================
# 2. Exit Code Contract
# =============================================================================

class TestExitCodeContract:
    """Test stable exit codes (STABILITY.md: 🟢 Stable)."""
    
    def test_exit_0_means_success(self, tmp_path: Path) -> None:
        """Exit code 0 = success (no errors, no warnings-as-errors)."""
        f = tmp_path / "valid.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f))
        assert result.returncode == 0
    
    def test_exit_1_means_error(self, tmp_path: Path) -> None:
        """Exit code 1 = compilation error."""
        f = tmp_path / "broken.ow"
        f.write_text("fn broken() -> Int { \"not int\" }\nfn main() { broken() }\n")
        result = run_cli("check", str(f))
        assert result.returncode == 1
    
    def test_exit_2_means_warnings_as_errors(self, tmp_path: Path) -> None:
        """Exit code 2 = warnings treated as errors."""
        f = tmp_path / "warning.ow"
        f.write_text("fn main() { let x = 1 }\n")
        result = run_cli("check", str(f), "--deny-warnings")
        assert result.returncode == 2
    
    def test_W_flag_is_alias_for_deny_warnings(self, tmp_path: Path) -> None:
        """-W is alias for --deny-warnings."""
        f = tmp_path / "warning.ow"
        f.write_text("fn main() { let x = 1 }\n")
        result_long = run_cli("check", str(f), "--deny-warnings")
        result_short = run_cli("check", str(f), "-W")
        assert result_long.returncode == result_short.returncode == 2


# =============================================================================
# 3. JSON Schema Contract
# =============================================================================

class TestJsonSchemaContract:
    """Test stable JSON output schema (STABILITY.md: 🟢 Stable)."""
    
    def test_json_has_version_field(self, tmp_path: Path) -> None:
        """JSON must have 'version' field."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        assert "version" in data
        assert isinstance(data["version"], str)
    
    def test_json_has_files_array(self, tmp_path: Path) -> None:
        """JSON must have 'files' array."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        assert "files" in data
        assert isinstance(data["files"], list)
    
    def test_json_has_summary_object(self, tmp_path: Path) -> None:
        """JSON must have 'summary' object."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        assert "summary" in data
        assert isinstance(data["summary"], dict)
    
    def test_json_summary_has_required_fields(self, tmp_path: Path) -> None:
        """Summary must have stable fields."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        summary = data["summary"]
        
        assert "total_files" in summary
        assert "files_with_errors" in summary
        assert "total_errors" in summary
        assert "total_warnings" in summary
    
    def test_json_file_entry_has_required_fields(self, tmp_path: Path) -> None:
        """Each file entry must have stable fields."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() {}\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        file_entry = data["files"][0]
        
        assert "file" in file_entry
        assert "success" in file_entry
        assert "errors" in file_entry
        assert "warnings" in file_entry
    
    def test_json_diagnostic_has_required_fields(self, tmp_path: Path) -> None:
        """Diagnostics must have stable fields."""
        f = tmp_path / "warning.ow"
        f.write_text("fn main() { let x = 1 }\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        warning = data["files"][0]["warnings"][0]
        
        assert "severity" in warning
        assert "code" in warning
        assert "message" in warning
        assert "file" in warning
        assert "line" in warning
        assert "column" in warning


# =============================================================================
# 4. Diagnostic Code Contract
# =============================================================================

class TestDiagnosticCodeContract:
    """Test stable diagnostic code format (STABILITY.md: 🟢 Stable)."""
    
    def test_error_code_format(self, tmp_path: Path) -> None:
        """Error codes must match Exxxx format."""
        f = tmp_path / "error.ow"
        f.write_text("fn broken() -> Int { \"nope\" }\nfn main() { broken() }\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        
        for error in data["files"][0]["errors"]:
            code = error["code"]
            assert len(code) == 5, f"Code {code} should be 5 chars"
            assert code[0] == "E", f"Error code {code} should start with E"
            assert code[1:].isdigit(), f"Code {code} should have 4 digits"
    
    def test_warning_code_format(self, tmp_path: Path) -> None:
        """Warning codes must match Wxxxx format."""
        f = tmp_path / "warning.ow"
        f.write_text("fn main() { let x = 1 }\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        
        for warning in data["files"][0]["warnings"]:
            code = warning["code"]
            assert len(code) == 5, f"Code {code} should be 5 chars"
            assert code[0] == "W", f"Warning code {code} should start with W"
            assert code[1:].isdigit(), f"Code {code} should have 4 digits"


# =============================================================================
# 5. Language Semantics Contract (Core Types)
# =============================================================================

class TestLanguageSemanticsContract:
    """Test stable language semantics (STABILITY.md: 🟢 Stable)."""
    
    def test_core_types_valid(self, tmp_path: Path) -> None:
        """Core types Int, Float, String, Bool, Void, Any are valid."""
        f = tmp_path / "types.ow"
        f.write_text("""
fn test_int() -> Int { 42 }
fn test_float() -> Float { 3.14 }
fn test_string() -> String { "hello" }
fn test_bool() -> Bool { true }
fn test_void() -> Void { }
fn test_any() -> Any { 1 }
fn main() {}
""")
        result = run_cli("check", str(f))
        assert result.returncode == 0
    
    def test_option_type_valid(self, tmp_path: Path) -> None:
        """Option[T] type is valid."""
        f = tmp_path / "option.ow"
        f.write_text("""
fn maybe() -> Option[Int] { Some(42) }
fn handle(opt: Option[Int]) -> Int {
    match opt {
        Some(n) => n,
        None => 0
    }
}
fn main() { let _ = handle(maybe()) }
""")
        result = run_cli("check", str(f))
        assert result.returncode == 0
    
    def test_result_type_valid(self, tmp_path: Path) -> None:
        """Result[T, E] type is valid."""
        f = tmp_path / "result.ow"
        f.write_text("""
fn try_it() -> Result[Int, String] { Ok(42) }
fn handle(res: Result[Int, String]) -> Int {
    match res {
        Ok(n) => n,
        Err(e) => 0
    }
}
fn main() { let _ = handle(try_it()) }
""")
        result = run_cli("check", str(f))
        assert result.returncode == 0
    
    def test_try_operator_valid(self, tmp_path: Path) -> None:
        """? operator for Result propagation is valid."""
        f = tmp_path / "try_op.ow"
        f.write_text("""
fn inner() -> Result[Int, String] { Ok(42) }
fn outer() -> Result[Int, String] {
    let x = inner()?
    Ok(x + 1)
}
fn main() { let _ = outer() }
""")
        result = run_cli("check", str(f))
        assert result.returncode == 0


# =============================================================================
# 6. Determinism Contract
# =============================================================================

class TestDeterminismContract:
    """Test deterministic output (INVARIANTS.md: Invariant 3)."""
    
    def test_same_input_same_output(self, tmp_path: Path) -> None:
        """Same input must produce same output."""
        f = tmp_path / "test.ow"
        f.write_text("fn main() { let x = 1; let y = 2 }\n")
        
        results = []
        for _ in range(3):
            result = run_cli("check", str(f), "--json")
            results.append(result.stdout)
        
        assert results[0] == results[1] == results[2]
    
    def test_warnings_order_deterministic(self, tmp_path: Path) -> None:
        """Warnings order must be deterministic."""
        f = tmp_path / "multi.ow"
        f.write_text("fn main() { let a = 1; let b = 2; let c = 3 }\n")
        
        results = []
        for _ in range(3):
            result = run_cli("check", str(f), "--json")
            data = json.loads(result.stdout)
            warnings = [w["code"] + str(w["line"]) for w in data["files"][0]["warnings"]]
            results.append(warnings)
        
        assert results[0] == results[1] == results[2]


# =============================================================================
# 7. Warning Suppression Contract
# =============================================================================

class TestWarningSuppressionContract:
    """Test underscore prefix suppresses warnings (INVARIANTS.md: Invariant 7)."""
    
    def test_underscore_suppresses_unused_warning(self, tmp_path: Path) -> None:
        """Variables starting with _ suppress unused warnings."""
        f = tmp_path / "suppress.ow"
        f.write_text("fn main() { let _unused = 42 }\n")
        result = run_cli("check", str(f))
        assert result.returncode == 0
        assert "warning" not in result.stderr.lower() or "No issues found" in result.stderr
    
    def test_underscore_param_suppresses_warning(self, tmp_path: Path) -> None:
        """Parameters starting with _ suppress unused warnings."""
        f = tmp_path / "suppress_param.ow"
        f.write_text("fn ignore(_x: Int) -> Void {}\nfn main() { ignore(42) }\n")
        result = run_cli("check", str(f), "--json")
        data = json.loads(result.stdout)
        # Should have no warnings about _x
        for w in data["files"][0]["warnings"]:
            assert "_x" not in w["message"]
