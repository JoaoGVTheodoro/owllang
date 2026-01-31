"""
OwlLang Diagnostic Errors

Structured error representation with codes, spans, notes, and hints.
Follows the pattern of modern compilers (Rust, Swift, Zig).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .span import Span, DUMMY_SPAN

if TYPE_CHECKING:
    pass


class Severity(Enum):
    """Severity level of a diagnostic."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class DiagnosticError:
    """
    A structured diagnostic error.
    
    Attributes:
        code: Error code (e.g., "E0301")
        message: Short description of the error
        span: Source location of the error
        severity: Error severity level
        notes: Additional explanatory notes
        hints: Suggestions for fixing the error
        labels: Additional labeled spans (for highlighting related code)
    """
    
    code: str
    message: str
    span: Span = field(default_factory=lambda: DUMMY_SPAN)
    severity: Severity = Severity.ERROR
    notes: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    labels: list[tuple[Span, str]] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.severity.value}[{self.code}]: {self.message} at {self.span}"
    
    def with_note(self, note: str) -> DiagnosticError:
        """Add a note to this diagnostic."""
        self.notes.append(note)
        return self
    
    def with_hint(self, hint: str) -> DiagnosticError:
        """Add a hint to this diagnostic."""
        self.hints.append(hint)
        return self
    
    def with_label(self, span: Span, label: str) -> DiagnosticError:
        """Add a labeled span to this diagnostic."""
        self.labels.append((span, label))
        return self


# Import ErrorCode from codes module for backward compatibility
from .codes import ErrorCode


# =============================================================================
# Error Factory Functions
# =============================================================================

def type_mismatch_error(
    expected: str,
    found: str,
    span: Span,
    hint: str | None = None
) -> DiagnosticError:
    """Create a type mismatch error."""
    error = DiagnosticError(
        code=ErrorCode.TYPE_MISMATCH.value,
        message="incompatible types in assignment",
        span=span,
    ).with_note(f"expected {expected}").with_note(f"found {found}")
    
    if hint:
        error.with_hint(hint)
    else:
        error.with_hint("change the type annotation or convert the value")
    
    return error


def undefined_variable_error(name: str, span: Span) -> DiagnosticError:
    """Create an undefined variable error."""
    return DiagnosticError(
        code=ErrorCode.UNDEFINED_VARIABLE.value,
        message=f"undefined variable `{name}`",
        span=span,
    ).with_hint(f"did you mean to define `{name}` first?")


def undefined_function_error(name: str, span: Span) -> DiagnosticError:
    """Create an undefined function error."""
    return DiagnosticError(
        code=ErrorCode.UNDEFINED_FUNCTION.value,
        message=f"undefined function `{name}`",
        span=span,
    ).with_hint(f"did you mean to define `{name}` or import it?")


def return_type_mismatch_error(
    expected: str,
    found: str,
    span: Span
) -> DiagnosticError:
    """Create a return type mismatch error."""
    return DiagnosticError(
        code=ErrorCode.RETURN_TYPE_MISMATCH.value,
        message="return type mismatch",
        span=span,
    ).with_note(f"expected {expected}").with_note(f"found {found}")


def invalid_operation_error(
    op: str,
    left: str,
    right: str,
    span: Span
) -> DiagnosticError:
    """Create an invalid operation error."""
    return DiagnosticError(
        code=ErrorCode.INVALID_OPERATION.value,
        message=f"cannot apply `{op}` to `{left}` and `{right}`",
        span=span,
    ).with_hint(f"operator `{op}` is not defined for these types")


def incompatible_comparison_error(
    left: str,
    right: str,
    op: str,
    span: Span
) -> DiagnosticError:
    """Create an incompatible comparison error."""
    return DiagnosticError(
        code=ErrorCode.INCOMPATIBLE_TYPES.value,
        message=f"cannot compare `{left}` with `{right}`",
        span=span,
    ).with_note(f"operator `{op}` requires operands of the same type")


def branch_type_mismatch_error(
    then_type: str,
    else_type: str,
    span: Span
) -> DiagnosticError:
    """Create a branch type mismatch error."""
    return DiagnosticError(
        code=ErrorCode.BRANCH_TYPE_MISMATCH.value,
        message="incompatible types in if/else branches",
        span=span,
    ).with_note(f"then branch has type {then_type}").with_note(f"else branch has type {else_type}").with_hint("both branches must return the same type")


def condition_not_bool_error(found: str, span: Span) -> DiagnosticError:
    """Create a condition not bool error."""
    return DiagnosticError(
        code=ErrorCode.CONDITION_NOT_BOOL.value,
        message="condition must be a boolean",
        span=span,
    ).with_note(f"found {found}").with_hint("use a comparison or boolean expression")


def wrong_arg_count_error(
    fn_name: str,
    expected: int,
    found: int,
    span: Span
) -> DiagnosticError:
    """Create a wrong argument count error."""
    return DiagnosticError(
        code=ErrorCode.WRONG_ARG_COUNT.value,
        message=f"wrong number of arguments for `{fn_name}`",
        span=span,
    ).with_note(f"expected {expected} argument(s)").with_note(f"found {found} argument(s)")


def cannot_negate_error(typ: str, span: Span) -> DiagnosticError:
    """Create a cannot negate error."""
    return DiagnosticError(
        code=ErrorCode.CANNOT_NEGATE.value,
        message=f"cannot negate `{typ}`",
        span=span,
    ).with_hint("unary minus only works on Int and Float")


def try_not_result_error(found: str, span: Span) -> DiagnosticError:
    """Create an error for using ? on a non-Result type."""
    return DiagnosticError(
        code=ErrorCode.TRY_NOT_RESULT.value,
        message=f"the `?` operator can only be applied to `Result` types",
        span=span,
    ).with_note(f"found type `{found}`").with_hint("ensure the expression returns a Result[T, E]")


def try_outside_result_fn_error(span: Span) -> DiagnosticError:
    """Create an error for using ? outside a Result-returning function."""
    return DiagnosticError(
        code=ErrorCode.TRY_OUTSIDE_RESULT_FN.value,
        message="the `?` operator can only be used in functions that return `Result`",
        span=span,
    ).with_hint("change the function's return type to Result[T, E]")


def try_error_type_mismatch_error(
    operand_err: str,
    fn_err: str,
    span: Span
) -> DiagnosticError:
    """Create an error for incompatible error types with ?."""
    return DiagnosticError(
        code=ErrorCode.TRY_ERROR_TYPE_MISMATCH.value,
        message="incompatible error types for `?` operator",
        span=span,
    ).with_note(f"expression has error type `{operand_err}`").with_note(f"function returns error type `{fn_err}`").with_hint("ensure the error types are compatible")


def match_not_exhaustive_error(missing: set[str], span: Span) -> DiagnosticError:
    """Create an error for non-exhaustive match expression."""
    missing_list = ', '.join(sorted(missing))
    return DiagnosticError(
        code=ErrorCode.NON_EXHAUSTIVE_MATCH.value,
        message=f"match is not exhaustive",
        span=span,
    ).with_note(f"missing patterns: {missing_list}").with_hint("add arms for all possible patterns")


def match_invalid_pattern_error(
    pattern_name: str,
    subject_type: str,
    expected: set[str],
    span: Span
) -> DiagnosticError:
    """Create an error for invalid pattern in match."""
    expected_list = ', '.join(sorted(expected))
    return DiagnosticError(
        code=ErrorCode.INVALID_PATTERN.value,
        message=f"pattern `{pattern_name}` is not valid for type `{subject_type}`",
        span=span,
    ).with_note(f"expected patterns: {expected_list}")


def wrong_type_arity_error(
    type_name: str,
    expected: int,
    found: int,
    span: Span
) -> DiagnosticError:
    """Create an error for wrong number of type parameters."""
    expected_str = "parameter" if expected == 1 else "parameters"
    found_str = "was" if found == 1 else "were"
    return DiagnosticError(
        code=ErrorCode.WRONG_TYPE_ARITY.value,
        message=f"`{type_name}` expects {expected} type {expected_str}, but {found} {found_str} provided",
        span=span,
    ).with_hint(f"use `{type_name}[...]` with {expected} type {expected_str}")


def unknown_type_error(type_name: str, span: Span) -> DiagnosticError:
    """Create an error for unknown type name."""
    return DiagnosticError(
        code=ErrorCode.UNKNOWN_TYPE.value,
        message=f"unknown type `{type_name}`",
        span=span,
    ).with_hint("valid types are: Int, Float, String, Bool, Void, Option[T], Result[T, E]")
