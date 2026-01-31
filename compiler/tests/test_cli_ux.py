"""
CLI UX tests for OwlLang.

Tests for:
1. Directory support in check command
2. Exit codes (0, 1, 2)
3. JSON output format
4. Output consistency (stderr/stdout separation)
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with test files."""
    # Valid file
    valid_file = tmp_path / "valid.ow"
    valid_file.write_text("""
// Valid OwlLang program
fn main() -> Void {
    print("Hello")
}
""")
    
    # File with warnings
    warning_file = tmp_path / "with_warnings.ow"
    warning_file.write_text("""
// File with unused variable warning
fn main() -> Void {
    let x = 42
    print("Hello")
}
""")
    
    # File with errors
    error_file = tmp_path / "with_errors.ow"
    error_file.write_text("""
// File with type error
fn broken() -> Int {
    "not an int"
}
fn main() -> Void {
    broken()
}
""")
    
    return tmp_path


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run the owllang CLI with given arguments."""
    cmd = [sys.executable, "-m", "owllang.cli"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or Path(__file__).parent.parent,
    )


# =============================================================================
# 1. Directory Support Tests
# =============================================================================

class TestDirectorySupport:
    """Test directory support in check command."""
    
    def test_check_single_file(self, temp_dir: Path) -> None:
        """Check single file works."""
        result = run_cli("check", str(temp_dir / "valid.ow"))
        assert result.returncode == 0
        assert "No issues found" in result.stderr
    
    def test_check_directory(self, temp_dir: Path) -> None:
        """Check directory finds all .ow files."""
        result = run_cli("check", str(temp_dir))
        # Should find valid.ow, with_warnings.ow, with_errors.ow
        assert "Checked 3 files" in result.stderr
    
    def test_check_directory_reports_errors(self, temp_dir: Path) -> None:
        """Check directory reports errors from all files."""
        result = run_cli("check", str(temp_dir))
        assert result.returncode == 1
        assert "error" in result.stderr.lower()
    
    def test_check_nonexistent_path(self) -> None:
        """Check nonexistent path returns error."""
        result = run_cli("check", "/nonexistent/path")
        assert result.returncode == 1
        assert "not found" in result.stderr.lower()
    
    def test_check_empty_directory(self, tmp_path: Path) -> None:
        """Check empty directory returns error."""
        result = run_cli("check", str(tmp_path))
        assert result.returncode == 1
        assert "No .ow files found" in result.stderr


# =============================================================================
# 2. Exit Code Tests
# =============================================================================

class TestExitCodes:
    """Test CLI exit codes."""
    
    def test_exit_0_on_success(self, temp_dir: Path) -> None:
        """Exit code 0 on successful check."""
        result = run_cli("check", str(temp_dir / "valid.ow"))
        assert result.returncode == 0
    
    def test_exit_1_on_error(self, temp_dir: Path) -> None:
        """Exit code 1 on compilation error."""
        result = run_cli("check", str(temp_dir / "with_errors.ow"))
        assert result.returncode == 1
    
    def test_exit_0_on_warnings_default(self, temp_dir: Path) -> None:
        """Exit code 0 with warnings by default."""
        result = run_cli("check", str(temp_dir / "with_warnings.ow"))
        assert result.returncode == 0
    
    def test_exit_2_on_warnings_deny(self, temp_dir: Path) -> None:
        """Exit code 2 when warnings treated as errors."""
        result = run_cli("check", str(temp_dir / "with_warnings.ow"), "--deny-warnings")
        assert result.returncode == 2
    
    def test_exit_2_with_W_flag(self, temp_dir: Path) -> None:
        """Exit code 2 with -W flag."""
        result = run_cli("check", str(temp_dir / "with_warnings.ow"), "-W")
        assert result.returncode == 2


# =============================================================================
# 3. JSON Output Tests
# =============================================================================

class TestJsonOutput:
    """Test JSON output format."""
    
    def test_json_output_valid_file(self, temp_dir: Path) -> None:
        """JSON output for valid file."""
        result = run_cli("check", str(temp_dir / "valid.ow"), "--json")
        assert result.returncode == 0
        
        data = json.loads(result.stdout)
        assert "version" in data
        assert "files" in data
        assert "summary" in data
        assert len(data["files"]) == 1
        assert data["files"][0]["success"] is True
    
    def test_json_output_with_warnings(self, temp_dir: Path) -> None:
        """JSON output includes warnings."""
        result = run_cli("check", str(temp_dir / "with_warnings.ow"), "--json")
        
        data = json.loads(result.stdout)
        assert data["summary"]["total_warnings"] > 0
        assert len(data["files"][0]["warnings"]) > 0
        
        warning = data["files"][0]["warnings"][0]
        assert "severity" in warning
        assert "code" in warning
        assert "message" in warning
        assert "file" in warning
        assert "line" in warning
        assert "column" in warning
    
    def test_json_output_with_errors(self, temp_dir: Path) -> None:
        """JSON output includes errors."""
        result = run_cli("check", str(temp_dir / "with_errors.ow"), "--json")
        assert result.returncode == 1
        
        data = json.loads(result.stdout)
        assert data["summary"]["total_errors"] > 0
        assert data["files"][0]["success"] is False
    
    def test_json_output_directory(self, temp_dir: Path) -> None:
        """JSON output for directory check."""
        result = run_cli("check", str(temp_dir), "--json")
        
        data = json.loads(result.stdout)
        assert data["summary"]["total_files"] == 3
    
    def test_json_structure_complete(self, temp_dir: Path) -> None:
        """JSON output has complete structure."""
        result = run_cli("check", str(temp_dir / "with_warnings.ow"), "--json")
        
        data = json.loads(result.stdout)
        
        # Check top-level structure
        assert set(data.keys()) == {"version", "files", "summary"}
        
        # Check summary structure
        summary_keys = {"total_files", "files_with_errors", "total_errors", "total_warnings"}
        assert set(data["summary"].keys()) == summary_keys
        
        # Check file structure
        file_keys = {"file", "success", "errors", "warnings"}
        assert set(data["files"][0].keys()) == file_keys


# =============================================================================
# 4. Output Consistency Tests
# =============================================================================

class TestOutputConsistency:
    """Test output goes to correct streams."""
    
    def test_diagnostics_go_to_stderr(self, temp_dir: Path) -> None:
        """Errors and warnings go to stderr."""
        result = run_cli("check", str(temp_dir / "with_warnings.ow"))
        
        # Warning should be in stderr
        assert "warning" in result.stderr.lower()
        # stdout should be empty
        assert result.stdout == ""
    
    def test_json_goes_to_stdout(self, temp_dir: Path) -> None:
        """JSON output goes to stdout."""
        result = run_cli("check", str(temp_dir / "valid.ow"), "--json")
        
        # JSON should be valid and in stdout
        data = json.loads(result.stdout)
        assert data is not None
    
    def test_success_message_to_stderr(self, temp_dir: Path) -> None:
        """Success message goes to stderr."""
        result = run_cli("check", str(temp_dir / "valid.ow"))
        
        assert "No issues found" in result.stderr
        assert result.stdout == ""
    
    def test_error_message_to_stderr(self, temp_dir: Path) -> None:
        """Error message goes to stderr."""
        result = run_cli("check", str(temp_dir / "with_errors.ow"))
        
        assert "error" in result.stderr.lower()
        assert result.stdout == ""


# =============================================================================
# 5. Compile and Run UX Tests
# =============================================================================

class TestCompileRunUx:
    """Test compile and run command UX."""
    
    def test_compile_no_output_on_error(self, temp_dir: Path) -> None:
        """Compile should not create output file on error."""
        error_file = temp_dir / "with_errors.ow"
        output_file = temp_dir / "with_errors.py"
        
        # Ensure output doesn't exist
        if output_file.exists():
            output_file.unlink()
        
        result = run_cli("compile", str(error_file))
        
        assert result.returncode == 1
        assert not output_file.exists()
        assert "no output generated" in result.stderr.lower()
    
    def test_compile_creates_output_on_success(self, temp_dir: Path) -> None:
        """Compile should create output file on success."""
        valid_file = temp_dir / "valid.ow"
        output_file = temp_dir / "valid.py"
        
        # Ensure output doesn't exist
        if output_file.exists():
            output_file.unlink()
        
        result = run_cli("compile", str(valid_file))
        
        assert result.returncode == 0
        assert output_file.exists()
        assert "Compiled successfully" in result.stderr
    
    def test_run_fails_on_error(self, temp_dir: Path) -> None:
        """Run should fail with clear message on error."""
        result = run_cli("run", str(temp_dir / "with_errors.ow"))
        
        assert result.returncode == 1
        assert "Cannot run" in result.stderr


# =============================================================================
# 6. Deterministic Order Tests
# =============================================================================

class TestDeterministicOrder:
    """Test that output is deterministic."""
    
    def test_warnings_ordered_by_line(self, temp_dir: Path) -> None:
        """Warnings should be ordered by line number."""
        # Create file with multiple warnings
        multi_warn = temp_dir / "multi_warn.ow"
        multi_warn.write_text("""
fn main() -> Void {
    let a = 1
    let b = 2
    let c = 3
    print("done")
}
""")
        
        result = run_cli("check", str(multi_warn), "--json")
        data = json.loads(result.stdout)
        
        warnings = data["files"][0]["warnings"]
        if len(warnings) > 1:
            # Check warnings are in order
            lines = [w["line"] for w in warnings]
            assert lines == sorted(lines)
    
    def test_directory_files_sorted(self, temp_dir: Path) -> None:
        """Files in directory should be sorted."""
        result = run_cli("check", str(temp_dir), "--json")
        data = json.loads(result.stdout)
        
        files = [f["file"] for f in data["files"]]
        assert files == sorted(files)
