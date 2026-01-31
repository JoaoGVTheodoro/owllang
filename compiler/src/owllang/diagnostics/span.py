"""
OwlLang Span - Source Location Tracking

A Span represents a range of source code with start and end positions.
Used for precise error reporting and source highlighting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Position:
    """A single position in source code (1-indexed)."""
    
    line: int
    column: int
    offset: int = 0  # Byte offset from start of file
    
    def __str__(self) -> str:
        return f"{self.line}:{self.column}"
    
    def __lt__(self, other: Position) -> bool:
        if self.line != other.line:
            return self.line < other.line
        return self.column < other.column


@dataclass(frozen=True)
class Span:
    """
    A range of source code.
    
    Represents everything from start position to end position (inclusive).
    Used to highlight the exact location of errors, warnings, and other diagnostics.
    """
    
    start: Position
    end: Position
    filename: str = "<unknown>"
    
    def __str__(self) -> str:
        if self.start.line == self.end.line:
            return f"{self.filename}:{self.start.line}:{self.start.column}"
        return f"{self.filename}:{self.start.line}:{self.start.column}-{self.end.line}:{self.end.column}"
    
    @classmethod
    def from_positions(
        cls,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
        filename: str = "<unknown>"
    ) -> Span:
        """Create a span from line/column positions."""
        return cls(
            start=Position(start_line, start_col),
            end=Position(end_line, end_col),
            filename=filename
        )
    
    @classmethod
    def single(cls, line: int, column: int, length: int = 1, filename: str = "<unknown>") -> Span:
        """Create a span for a single-line region."""
        return cls(
            start=Position(line, column),
            end=Position(line, column + length - 1),
            filename=filename
        )
    
    @classmethod
    def from_token(cls, line: int, column: int, value: str, filename: str = "<unknown>") -> Span:
        """Create a span from a token's position and value."""
        return cls.single(line, column, len(value), filename)
    
    def merge(self, other: Span) -> Span:
        """Merge two spans into one that covers both."""
        start = self.start if self.start < other.start else other.start
        end = other.end if other.end.line > self.end.line or (
            other.end.line == self.end.line and other.end.column > self.end.column
        ) else self.end
        return Span(start, end, self.filename)
    
    @property
    def is_multiline(self) -> bool:
        """Check if the span covers multiple lines."""
        return self.start.line != self.end.line
    
    @property
    def length(self) -> int:
        """Length of the span (only valid for single-line spans)."""
        if self.is_multiline:
            return 0
        return self.end.column - self.start.column + 1


# Sentinel for missing spans
DUMMY_SPAN = Span(Position(1, 1), Position(1, 1), "<no location>")
