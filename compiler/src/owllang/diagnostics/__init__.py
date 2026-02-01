"""
OwlLang Diagnostics Module

Provides rich, structured error reporting with:
- Precise source location tracking (Span)
- Error codes and structured errors (DiagnosticError)
- Warning codes and structured warnings (Warning)
- Pretty printing for terminal output (DiagnosticPrinter)
"""

from .span import Span, Position, DUMMY_SPAN
from .codes import ErrorCode, WarningCode
from .error import (
    DiagnosticError,
    Severity,
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
    match_not_exhaustive_error,
    match_invalid_pattern_error,
    assignment_to_immutable_error,
    break_outside_loop_error,
    continue_outside_loop_error,
)
from .warning import (
    Warning,
    unused_variable_warning,
    unused_parameter_warning,
    unreachable_code_warning,
    result_ignored_warning,
    option_ignored_warning,
    constant_condition_warning,
)
from .printer import DiagnosticPrinter, print_diagnostics

__all__ = [
    # Span
    "Span",
    "Position",
    "DUMMY_SPAN",
    # Codes
    "ErrorCode",
    "WarningCode",
    # Error
    "DiagnosticError",
    "Severity",
    # Error factory functions
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
    "match_not_exhaustive_error",
    "match_invalid_pattern_error",
    "assignment_to_immutable_error",
    # Warning
    "Warning",
    # Warning factory functions
    "unused_variable_warning",
    "unused_parameter_warning",
    "unreachable_code_warning",
    "result_ignored_warning",
    "option_ignored_warning",
    "constant_condition_warning",
    # Printer
    "DiagnosticPrinter",
    "print_diagnostics",
]

