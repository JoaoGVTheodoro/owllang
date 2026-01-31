"""
OwlLang Diagnostics Module

Provides rich, structured error reporting with:
- Precise source location tracking (Span)
- Error codes and structured errors (DiagnosticError)
- Pretty printing for terminal output (DiagnosticPrinter)
"""

from .span import Span, Position, DUMMY_SPAN
from .error import (
    DiagnosticError,
    Severity,
    ErrorCode,
    # Factory functions
    type_mismatch_error,
    undefined_variable_error,
    undefined_function_error,
    return_type_mismatch_error,
    invalid_operation_error,
    incompatible_comparison_error,
    branch_type_mismatch_error,
    condition_not_bool_error,
    wrong_arg_count_error,
    cannot_negate_error,
    try_not_result_error,
    try_outside_result_fn_error,
    try_error_type_mismatch_error,
    wrong_type_arity_error,
    unknown_type_error,
)
from .printer import DiagnosticPrinter, print_diagnostics

__all__ = [
    # Span
    "Span",
    "Position",
    "DUMMY_SPAN",
    # Error
    "DiagnosticError",
    "Severity",
    "ErrorCode",
    # Factory functions
    "type_mismatch_error",
    "undefined_variable_error",
    "undefined_function_error",
    "return_type_mismatch_error",
    "invalid_operation_error",
    "incompatible_comparison_error",
    "branch_type_mismatch_error",
    "condition_not_bool_error",
    "wrong_arg_count_error",
    "cannot_negate_error",
    "try_not_result_error",
    "try_outside_result_fn_error",
    "try_error_type_mismatch_error",
    "wrong_type_arity_error",
    "unknown_type_error",
    # Printer
    "DiagnosticPrinter",
    "print_diagnostics",
]
