"""
Integration tests for OwlLang examples.

These tests ensure all example files in examples/ remain valid
and serve as living documentation for the language.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Path to the examples directory
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"

# Valid examples that should pass type checking
VALID_EXAMPLES = [
    "00_hello_world.ow",
    "01_variables_and_types.ow",
    "02_functions.ow",
    "03_if_expression.ow",
    "04_option_basic.ow",
    "05_result_basic.ow",
    "07_python_import.ow",
    "08_try_operator.ow",
]

# Invalid examples that should fail type checking
INVALID_EXAMPLES = [
    "06_type_errors.ow",
]


class TestExamplesExist:
    """Verify all required example files exist."""

    @pytest.mark.parametrize("filename", VALID_EXAMPLES + INVALID_EXAMPLES)
    def test_example_file_exists(self, filename: str) -> None:
        """Each example file should exist."""
        filepath = EXAMPLES_DIR / filename
        assert filepath.exists(), f"Missing example file: {filename}"

    def test_examples_directory_exists(self) -> None:
        """The examples directory should exist."""
        assert EXAMPLES_DIR.exists(), f"Examples directory not found: {EXAMPLES_DIR}"


class TestValidExamples:
    """Test that valid examples pass type checking."""

    @pytest.mark.parametrize("filename", VALID_EXAMPLES)
    def test_example_passes_type_check(self, filename: str) -> None:
        """Valid example should pass owl check without errors."""
        filepath = EXAMPLES_DIR / filename
        
        result = subprocess.run(
            [sys.executable, "-m", "owllang", "check", str(filepath), "--no-warnings"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,  # compiler directory
        )
        
        assert result.returncode == 0, (
            f"{filename} failed type check:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        # Check for success message
        assert "No errors found" in result.stdout or "No issues found" in result.stdout


class TestInvalidExamples:
    """Test that invalid examples fail type checking."""

    @pytest.mark.parametrize("filename", INVALID_EXAMPLES)
    def test_example_fails_type_check(self, filename: str) -> None:
        """Invalid example should fail owl check with errors."""
        filepath = EXAMPLES_DIR / filename
        
        result = subprocess.run(
            [sys.executable, "-m", "owllang", "check", str(filepath)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,  # compiler directory
        )
        
        assert result.returncode != 0, (
            f"{filename} should have type errors but passed"
        )
        assert "Type errors" in result.stdout or "error" in result.stdout.lower()


class TestExampleQuality:
    """Test that examples meet quality standards."""

    @pytest.mark.parametrize("filename", VALID_EXAMPLES + INVALID_EXAMPLES)
    def test_example_has_comment_header(self, filename: str) -> None:
        """Each example should have a comment header."""
        filepath = EXAMPLES_DIR / filename
        content = filepath.read_text()
        
        # First line should be a comment
        first_line = content.strip().split("\n")[0]
        assert first_line.startswith("//"), (
            f"{filename} should start with a comment header"
        )

    @pytest.mark.parametrize("filename", VALID_EXAMPLES + INVALID_EXAMPLES)
    def test_example_is_concise(self, filename: str) -> None:
        """Each example should be ~30 lines or less."""
        filepath = EXAMPLES_DIR / filename
        content = filepath.read_text()
        
        line_count = len(content.strip().split("\n"))
        assert line_count <= 35, (
            f"{filename} has {line_count} lines, should be ~30 or less"
        )

    @pytest.mark.parametrize("filename", VALID_EXAMPLES)
    def test_valid_example_has_main(self, filename: str) -> None:
        """Valid examples should have a main function."""
        filepath = EXAMPLES_DIR / filename
        content = filepath.read_text()
        
        assert "fn main()" in content, (
            f"{filename} should have a main function"
        )
