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
    "01_hello_world.ow",
    "02_variables.ow",
    "03_functions.ow",
    "04_if_expression.ow",
    "05_option.ow",
    "06_result.ow",
    "07_try_operator.ow",
    "08_match.ow",
    "09_lists.ow",
    "10_while_loop.ow",
    "11_for_loop.ow",
    "12_loop_range.ow",
    "13_break_continue.ow",
]

# Invalid examples that should fail type checking
INVALID_EXAMPLES = [
    # None currently - removed type_errors.ow in cleanup
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
        # Check for success message (now goes to stderr)
        assert "No errors found" in result.stderr or "No issues found" in result.stderr


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
        # Error messages now go to stderr
        assert "error" in result.stderr.lower()


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
        """Each example should be reasonably sized."""
        filepath = EXAMPLES_DIR / filename
        content = filepath.read_text()
        
        line_count = len(content.strip().split("\n"))
        # Allow longer examples for complex topics (lists, loops, match)
        assert line_count <= 250, (
            f"{filename} has {line_count} lines, should be 250 or less"
        )

    @pytest.mark.parametrize("filename", VALID_EXAMPLES)
    def test_valid_example_has_main(self, filename: str) -> None:
        """Valid examples should have a main function."""
        filepath = EXAMPLES_DIR / filename
        content = filepath.read_text()
        
        assert "fn main()" in content, (
            f"{filename} should have a main function"
        )
