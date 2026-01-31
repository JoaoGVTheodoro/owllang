"""
Tests for the OwlLang Diagnostics Module (DX Phase 1)

Tests:
- Span creation and manipulation
- DiagnosticError creation with codes and messages
- Error factory functions
- Pretty printer output
- Multiple errors in same file
"""

import pytest

from owllang.diagnostics import (
    # Span
    Span, Position, DUMMY_SPAN,
    # Error
    DiagnosticError, Severity, ErrorCode,
    # Factory functions
    type_mismatch_error, undefined_variable_error, undefined_function_error,
    return_type_mismatch_error, invalid_operation_error, incompatible_comparison_error,
    branch_type_mismatch_error, condition_not_bool_error, wrong_arg_count_error,
    cannot_negate_error,
    # Printer
    DiagnosticPrinter, print_diagnostics,
)


class TestPosition:
    """Test Position class."""
    
    def test_position_creation(self) -> None:
        """Position stores line, column, and optional offset."""
        pos = Position(line=5, column=10)
        assert pos.line == 5
        assert pos.column == 10
        assert pos.offset == 0
    
    def test_position_with_offset(self) -> None:
        """Position can store byte offset."""
        pos = Position(line=5, column=10, offset=42)
        assert pos.offset == 42
    
    def test_position_str(self) -> None:
        """Position string representation."""
        pos = Position(line=5, column=10)
        assert str(pos) == "5:10"
    
    def test_position_comparison(self) -> None:
        """Positions can be compared."""
        pos1 = Position(1, 5)
        pos2 = Position(1, 10)
        pos3 = Position(2, 1)
        
        assert pos1 < pos2  # Same line, different column
        assert pos2 < pos3  # Different line
        assert not pos2 < pos1


class TestSpan:
    """Test Span class."""
    
    def test_span_creation(self) -> None:
        """Span has start and end positions."""
        span = Span(
            start=Position(1, 5),
            end=Position(1, 10),
            filename="test.ow"
        )
        assert span.start.line == 1
        assert span.start.column == 5
        assert span.end.column == 10
        assert span.filename == "test.ow"
    
    def test_span_from_positions(self) -> None:
        """Create span from line/column positions."""
        span = Span.from_positions(1, 5, 1, 10, "test.ow")
        assert span.start.line == 1
        assert span.start.column == 5
        assert span.end.column == 10
    
    def test_span_single(self) -> None:
        """Create single-line span."""
        span = Span.single(5, 10, length=5, filename="test.ow")
        assert span.start.line == 5
        assert span.start.column == 10
        assert span.end.line == 5
        assert span.end.column == 14  # 10 + 5 - 1
    
    def test_span_from_token(self) -> None:
        """Create span from token value."""
        span = Span.from_token(3, 5, "hello", "test.ow")
        assert span.start.line == 3
        assert span.start.column == 5
        assert span.length == 5
    
    def test_span_str_single_line(self) -> None:
        """Single-line span string representation."""
        span = Span.single(5, 10, 3, "test.ow")
        assert str(span) == "test.ow:5:10"
    
    def test_span_str_multi_line(self) -> None:
        """Multi-line span string representation."""
        span = Span.from_positions(1, 5, 3, 10, "test.ow")
        assert "test.ow:1:5" in str(span)
    
    def test_span_merge(self) -> None:
        """Merge two spans."""
        span1 = Span.single(1, 5, 3)
        span2 = Span.single(1, 15, 5)
        merged = span1.merge(span2)
        assert merged.start.column == 5
        assert merged.end.column == 19
    
    def test_span_is_multiline(self) -> None:
        """Check if span is multiline."""
        single = Span.single(1, 5, 3)
        multi = Span.from_positions(1, 5, 3, 10)
        
        assert not single.is_multiline
        assert multi.is_multiline
    
    def test_span_length(self) -> None:
        """Span length for single-line spans."""
        span = Span.single(1, 5, 10)
        assert span.length == 10


class TestDiagnosticError:
    """Test DiagnosticError class."""
    
    def test_error_creation(self) -> None:
        """Create basic diagnostic error."""
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
            span=Span.single(5, 10, 5),
        )
        assert error.code == "E0301"
        assert error.message == "type mismatch"
        assert error.severity == Severity.ERROR
    
    def test_error_with_notes(self) -> None:
        """Error with notes."""
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
        ).with_note("expected Int").with_note("found String")
        
        assert len(error.notes) == 2
        assert "expected Int" in error.notes
        assert "found String" in error.notes
    
    def test_error_with_hints(self) -> None:
        """Error with hints."""
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
        ).with_hint("change the type annotation")
        
        assert len(error.hints) == 1
        assert "change the type annotation" in error.hints
    
    def test_error_with_labels(self) -> None:
        """Error with labeled spans."""
        span1 = Span.single(5, 10, 3)
        span2 = Span.single(5, 20, 5)
        
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
            span=span1,
        ).with_label(span2, "found this")
        
        assert len(error.labels) == 1
        assert error.labels[0][1] == "found this"
    
    def test_error_str(self) -> None:
        """Error string representation."""
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
            span=Span.single(5, 10, 3, "test.ow"),
        )
        assert "error[E0301]" in str(error)
        assert "type mismatch" in str(error)


class TestErrorFactories:
    """Test error factory functions."""
    
    def test_type_mismatch_error(self) -> None:
        """Type mismatch error factory."""
        span = Span.single(5, 10, 5)
        error = type_mismatch_error("Int", "String", span)
        
        assert error.code == ErrorCode.TYPE_MISMATCH
        assert "incompatible" in error.message
        assert any("expected Int" in note for note in error.notes)
        assert any("found String" in note for note in error.notes)
    
    def test_undefined_variable_error(self) -> None:
        """Undefined variable error factory."""
        span = Span.single(3, 5, 3)
        error = undefined_variable_error("xyz", span)
        
        assert error.code == ErrorCode.UNDEFINED_VARIABLE
        assert "xyz" in error.message
    
    def test_undefined_function_error(self) -> None:
        """Undefined function error factory."""
        span = Span.single(7, 1, 5)
        error = undefined_function_error("foo", span)
        
        assert error.code == ErrorCode.UNDEFINED_FUNCTION
        assert "foo" in error.message
    
    def test_return_type_mismatch_error(self) -> None:
        """Return type mismatch error factory."""
        span = Span.single(10, 5, 10)
        error = return_type_mismatch_error("Int", "String", span)
        
        assert error.code == ErrorCode.RETURN_TYPE_MISMATCH
        assert "return" in error.message.lower()
    
    def test_invalid_operation_error(self) -> None:
        """Invalid operation error factory."""
        span = Span.single(5, 10, 1)
        error = invalid_operation_error("+", "Int", "String", span)
        
        assert error.code == ErrorCode.INVALID_OPERATION
        assert "+" in error.message
    
    def test_branch_type_mismatch_error(self) -> None:
        """Branch type mismatch error factory."""
        span = Span.single(8, 1, 20)
        error = branch_type_mismatch_error("Int", "String", span)
        
        assert error.code == ErrorCode.BRANCH_TYPE_MISMATCH
        assert "branch" in error.message.lower()


class TestDiagnosticPrinter:
    """Test DiagnosticPrinter class."""
    
    def test_format_simple_error(self) -> None:
        """Format a simple error."""
        source = "let x: Int = \"hello\""
        source_lines = source.split("\n")
        printer = DiagnosticPrinter(source_lines, use_color=False)
        
        error = DiagnosticError(
            code="E0301",
            message="incompatible types",
            span=Span.single(1, 14, 7, "test.ow"),
        ).with_note("expected Int").with_note("found String")
        
        output = printer.format_error(error)
        
        assert "error[E0301]" in output
        assert "incompatible types" in output
        assert "test.ow:1:14" in output
        assert "let x: Int = \"hello\"" in output
        assert "expected Int" in output
        assert "found String" in output
    
    def test_format_error_with_underline(self) -> None:
        """Error output includes underline."""
        source = "let x: Int = \"hello\""
        printer = DiagnosticPrinter([source], use_color=False)
        
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
            span=Span.single(1, 14, 7),
        )
        
        output = printer.format_error(error)
        # Should have carets (^) for underlining
        assert "^" in output
    
    def test_format_error_with_hint(self) -> None:
        """Error output includes hint."""
        source = "let x = undefined_var"
        printer = DiagnosticPrinter([source], use_color=False)
        
        error = DiagnosticError(
            code="E0302",
            message="undefined variable",
            span=Span.single(1, 9, 13),
        ).with_hint("did you mean to define it?")
        
        output = printer.format_error(error)
        assert "hint:" in output
        assert "did you mean to define it?" in output
    
    def test_format_multiple_errors(self) -> None:
        """Format multiple errors."""
        source = """let x: Int = "hello"
let y = unknown
let z: String = 42"""
        source_lines = source.split("\n")
        printer = DiagnosticPrinter(source_lines, use_color=False)
        
        errors = [
            DiagnosticError(
                code="E0301",
                message="type mismatch",
                span=Span.single(1, 14, 7),
            ),
            DiagnosticError(
                code="E0302",
                message="undefined variable",
                span=Span.single(2, 9, 7),
            ),
            DiagnosticError(
                code="E0301",
                message="type mismatch",
                span=Span.single(3, 17, 2),
            ),
        ]
        
        output = printer.format_errors(errors)
        
        # Should include all three errors
        assert output.count("error[E0301]") == 2
        assert output.count("error[E0302]") == 1
        # Should have summary
        assert "3 error(s)" in output
    
    def test_print_diagnostics_convenience(self) -> None:
        """Test print_diagnostics convenience function."""
        source = "let x = bad_var"
        error = DiagnosticError(
            code="E0302",
            message="undefined variable `bad_var`",
            span=Span.single(1, 9, 7),
        )
        
        output = print_diagnostics([error], source, use_color=False)
        
        assert "error[E0302]" in output
        assert "undefined variable" in output
        assert "let x = bad_var" in output


class TestPrinterWithColors:
    """Test printer with ANSI colors."""
    
    def test_colored_output(self) -> None:
        """Colored output contains ANSI escape codes."""
        source = "let x: Int = \"hello\""
        printer = DiagnosticPrinter([source], use_color=True)
        
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
            span=Span.single(1, 14, 7),
        )
        
        output = printer.format_error(error)
        # ANSI escape codes start with \033[
        assert "\033[" in output
    
    def test_no_color_output(self) -> None:
        """No color output has no ANSI escape codes."""
        source = "let x: Int = \"hello\""
        printer = DiagnosticPrinter([source], use_color=False)
        
        error = DiagnosticError(
            code="E0301",
            message="type mismatch",
            span=Span.single(1, 14, 7),
        )
        
        output = printer.format_error(error)
        assert "\033[" not in output


class TestIntegrationWithTypeChecker:
    """Test integration between diagnostics and type checker."""
    
    def test_type_checker_has_diagnostics_list(self) -> None:
        """TypeChecker has diagnostics list."""
        from owllang.typechecker import TypeChecker
        
        checker = TypeChecker(filename="test.ow")
        assert hasattr(checker, 'diagnostics')
        assert isinstance(checker.diagnostics, list)
    
    def test_type_checker_filename(self) -> None:
        """TypeChecker stores filename."""
        from owllang.typechecker import TypeChecker
        
        checker = TypeChecker(filename="example.ow")
        assert checker.filename == "example.ow"
