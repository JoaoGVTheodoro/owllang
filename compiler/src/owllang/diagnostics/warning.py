"""
OwlLang Warnings

Structured warning representation for non-fatal diagnostics.
Warnings do not block compilation but indicate potential issues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .span import Span, DUMMY_SPAN
from .codes import WarningCode

if TYPE_CHECKING:
    pass


@dataclass
class Warning:
    """
    A structured compiler warning.
    
    Warnings indicate potential issues but do not block compilation.
    
    Attributes:
        code: Warning code (e.g., "W0101")
        message: Short description of the warning
        span: Source location of the warning
        notes: Additional explanatory notes
        hints: Suggestions for addressing the warning
    """
    
    code: WarningCode
    message: str
    span: Span = field(default_factory=lambda: DUMMY_SPAN)
    notes: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"warning[{self.code.value}]: {self.message} at {self.span}"
    
    def with_note(self, note: str) -> "Warning":
        """Add a note to this warning."""
        self.notes.append(note)
        return self
    
    def with_hint(self, hint: str) -> "Warning":
        """Add a hint to this warning."""
        self.hints.append(hint)
        return self


# =============================================================================
# Warning Factory Functions
# =============================================================================

def unused_variable_warning(name: str, span: Span | None = None) -> Warning:
    """Create a warning for an unused variable."""
    return Warning(
        code=WarningCode.UNUSED_VARIABLE,
        message=f"unused variable `{name}`",
        span=span or DUMMY_SPAN,
    ).with_hint(f"if this is intentional, prefix with underscore: `_{name}`")


def unused_parameter_warning(name: str, fn_name: str | None = None, span: Span | None = None) -> Warning:
    """Create a warning for an unused function parameter."""
    if fn_name:
        msg = f"unused parameter `{name}` in function `{fn_name}`"
    else:
        msg = f"unused parameter `{name}`"
    return Warning(
        code=WarningCode.UNUSED_PARAMETER,
        message=msg,
        span=span or DUMMY_SPAN,
    ).with_hint(f"if this is intentional, prefix with underscore: `_{name}`")


def unreachable_code_warning(span: Span) -> Warning:
    """Create a warning for unreachable code."""
    return Warning(
        code=WarningCode.UNREACHABLE_CODE,
        message="unreachable code",
        span=span,
    ).with_note("this code will never execute")


def variable_shadows_warning(name: str, span: Span, original_span: Span | None = None) -> Warning:
    """Create a warning for variable shadowing."""
    warning = Warning(
        code=WarningCode.VARIABLE_SHADOWS,
        message=f"variable `{name}` shadows a variable in outer scope",
        span=span,
    )
    if original_span:
        warning.with_note(f"original variable defined at {original_span}")
    return warning.with_hint("consider using a different name to avoid confusion")


def redundant_match_warning(span: Span) -> Warning:
    """Create a warning for a match with only one arm."""
    return Warning(
        code=WarningCode.REDUNDANT_MATCH,
        message="match expression with single case is redundant",
        span=span,
    ).with_hint("consider using a simple expression instead")


def unnecessary_else_warning(span: Span) -> Warning:
    """Create a warning for else after return."""
    return Warning(
        code=WarningCode.UNNECESSARY_ELSE,
        message="unnecessary else after return",
        span=span,
    ).with_hint("the else branch can be removed since the if branch returns")


def variable_never_mutated_warning(name: str, span: Span) -> Warning:
    """Create a warning for mutable variable that is never mutated."""
    return Warning(
        code=WarningCode.VARIABLE_NEVER_MUTATED,
        message=f"variable `{name}` is declared as mutable but never mutated",
        span=span,
    ).with_hint("consider using `let` instead of `var`")
