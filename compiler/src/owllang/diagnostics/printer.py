"""
OwlLang Diagnostic Printer

Pretty prints diagnostic errors in the style of modern compilers.
Displays source code context with highlighted spans.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .span import Span
from .error import DiagnosticError, Severity

if TYPE_CHECKING:
    pass


# ANSI color codes
class Colors:
    """ANSI escape codes for terminal colors."""
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BOLD_RED = "\033[1;31m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_CYAN = "\033[1;36m"


class DiagnosticPrinter:
    """
    Pretty printer for diagnostic errors.
    
    Outputs errors in a format similar to Rust/Zig compilers:
    
    error[E0301]: incompatible types in assignment
      --> example.ow:5:9
       |
    5  | let x: Int = "hello"
       |        ^^^   ^^^^^^^
       |
       = expected Int
       = found String
       = hint: change the type annotation or convert the value
    """
    
    def __init__(self, source_lines: list[str], use_color: bool = True) -> None:
        """
        Initialize the printer.
        
        Args:
            source_lines: Lines of source code (for context display)
            use_color: Whether to use ANSI colors in output
        """
        self.source_lines = source_lines
        self.use_color = use_color
    
    def _color(self, text: str, color: str) -> str:
        """Apply color if enabled."""
        if self.use_color:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def _severity_color(self, severity: Severity) -> str:
        """Get color for severity level."""
        match severity:
            case Severity.ERROR:
                return Colors.BOLD_RED
            case Severity.WARNING:
                return Colors.BOLD_YELLOW
            case Severity.INFO:
                return Colors.BOLD_BLUE
            case Severity.HINT:
                return Colors.BOLD_CYAN
    
    def _severity_symbol(self, severity: Severity) -> str:
        """Get symbol for severity level."""
        match severity:
            case Severity.ERROR:
                return "^"
            case Severity.WARNING:
                return "~"
            case _:
                return "-"
    
    def format_error(self, error: DiagnosticError) -> str:
        """Format a single diagnostic error."""
        lines: list[str] = []
        
        # Header: error[E0301]: message
        severity_str = self._color(
            f"{error.severity.value}[{error.code}]",
            self._severity_color(error.severity)
        )
        lines.append(f"{severity_str}: {self._color(error.message, Colors.BOLD)}")
        
        # Location: --> file:line:column
        location_prefix = self._color("-->", Colors.BLUE)
        lines.append(f"  {location_prefix} {error.span}")
        
        # Source context
        span = error.span
        if span.start.line > 0 and span.start.line <= len(self.source_lines):
            line_num = span.start.line
            source_line = self.source_lines[line_num - 1] if line_num <= len(self.source_lines) else ""
            
            # Line number gutter width
            gutter_width = len(str(line_num)) + 1
            pipe = self._color("|", Colors.BLUE)
            
            # Empty line with pipe
            lines.append(f"{' ' * gutter_width} {pipe}")
            
            # Source line
            line_num_str = self._color(str(line_num).rjust(gutter_width - 1), Colors.BLUE)
            lines.append(f"{line_num_str} {pipe} {source_line.rstrip()}")
            
            # Underline/highlight
            underline = self._build_underline(span, source_line)
            if underline.strip():
                underline_colored = self._color(underline, self._severity_color(error.severity))
                lines.append(f"{' ' * gutter_width} {pipe} {underline_colored}")
            
            # Empty line with pipe
            lines.append(f"{' ' * gutter_width} {pipe}")
        
        # Notes
        for note in error.notes:
            note_prefix = self._color("=", Colors.BLUE)
            lines.append(f"   {note_prefix} {note}")
        
        # Hints
        for hint in error.hints:
            hint_prefix = self._color("= hint:", Colors.CYAN)
            lines.append(f"   {hint_prefix} {hint}")
        
        return "\n".join(lines)
    
    def _build_underline(self, span: Span, source_line: str) -> str:
        """Build underline string for highlighting."""
        if span.is_multiline:
            # For multiline spans, underline from start to end of line
            start_col = span.start.column - 1
            end_col = len(source_line)
        else:
            start_col = span.start.column - 1
            end_col = span.end.column
        
        # Ensure valid range
        start_col = max(0, start_col)
        end_col = min(len(source_line), end_col)
        
        # Build underline
        underline = " " * start_col + "^" * max(1, end_col - start_col)
        return underline
    
    def format_errors(self, errors: list[DiagnosticError]) -> str:
        """Format multiple errors with separators."""
        if not errors:
            return ""
        
        formatted = []
        for error in errors:
            formatted.append(self.format_error(error))
        
        # Summary
        error_count = sum(1 for e in errors if e.severity == Severity.ERROR)
        warning_count = sum(1 for e in errors if e.severity == Severity.WARNING)
        
        summary_parts = []
        if error_count:
            summary_parts.append(
                self._color(f"{error_count} error(s)", Colors.BOLD_RED)
            )
        if warning_count:
            summary_parts.append(
                self._color(f"{warning_count} warning(s)", Colors.BOLD_YELLOW)
            )
        
        if summary_parts:
            formatted.append("")
            formatted.append(" ".join(summary_parts) + " emitted")
        
        return "\n\n".join(formatted[:len(errors)]) + "\n" + "\n".join(formatted[len(errors):])


def print_diagnostics(
    errors: list[DiagnosticError],
    source: str,
    use_color: bool = True
) -> str:
    """
    Convenience function to format and print diagnostics.
    
    Args:
        errors: List of diagnostic errors
        source: Full source code string
        use_color: Whether to use ANSI colors
    
    Returns:
        Formatted error output string
    """
    source_lines = source.split("\n")
    printer = DiagnosticPrinter(source_lines, use_color)
    return printer.format_errors(errors)
