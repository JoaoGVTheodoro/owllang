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


# Note: The following warning factory functions are planned but not yet implemented:
# - variable_shadows_warning: for detecting variable shadowing
# - redundant_match_warning: for match with single case
# - unnecessary_else_warning: for else after return
# - variable_never_mutated_warning: for var that is never mutated
# These are kept in WarningCode enum for future implementation.
