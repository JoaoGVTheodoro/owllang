"""
OwlLang Lexer

Converts source code into a stream of tokens.
"""

from __future__ import annotations

from ..ast import Token, TokenType


class LexerError(Exception):
    """Error during lexical analysis."""
    
    def __init__(self, message: str, line: int, column: int, hint: str | None = None) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.hint = hint
        super().__init__(f"Lexer error at {line}:{column}: {message}")


class Lexer:
    """
    Tokenizes OwlLang source code.
    
    Usage:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
    """
    
    # Keywords mapping
    KEYWORDS: dict[str, TokenType] = {
        'fn': TokenType.FN,
        'let': TokenType.LET,
        'mut': TokenType.MUT,
        'while': TokenType.WHILE,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'loop': TokenType.LOOP,
        'from': TokenType.FROM,
        'python': TokenType.PYTHON,
        'import': TokenType.IMPORT,
        'as': TokenType.AS,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'return': TokenType.RETURN,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'match': TokenType.MATCH,
    }
    
    # Single-character tokens
    SINGLE_CHARS: dict[str, TokenType] = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.STAR,
        '/': TokenType.SLASH,
        '%': TokenType.PERCENT,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        ',': TokenType.COMMA,
        ':': TokenType.COLON,
        '.': TokenType.DOT,
        '?': TokenType.QUESTION,
    }
    
    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        # Cache source length to avoid repeated len() calls
        self.source_len = len(source)
    
    def tokenize(self) -> list[Token]:
        """Convert source code to list of tokens."""
        while not self._is_at_end():
            self._scan_token()
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def _is_at_end(self) -> bool:
        """Check if we've consumed all source code."""
        return self.pos >= self.source_len
    
    def _peek(self, offset: int = 0) -> str:
        """Look at current character without consuming."""
        pos = self.pos + offset
        if pos >= self.source_len:
            return '\0'
        return self.source[pos]
    
    def _advance(self) -> str:
        """Consume and return current character."""
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def _add_token(self, token_type: TokenType, value: str, line: int, column: int) -> None:
        """Add a token to the list."""
        self.tokens.append(Token(token_type, value, line, column))
    
    def _skip_whitespace(self) -> None:
        """Skip spaces, tabs (but not newlines for now)."""
        while not self._is_at_end() and self._peek() in ' \t\r':
            self._advance()
    
    def _skip_comment(self) -> None:
        """Skip // comments until end of line."""
        while not self._is_at_end() and self._peek() != '\n':
            self._advance()
    
    def _skip_multiline_comment(self, start_line: int, start_column: int) -> None:
        """Skip /** ... */ multi-line comments."""
        # Skip opening /**
        self._advance()  # /
        self._advance()  # *
        self._advance()  # *
        
        while not self._is_at_end():
            if self._peek() == '*' and self._peek(1) == '/':
                self._advance()  # *
                self._advance()  # /
                return
            self._advance()
        
        # If we reach here, comment was not closed
        raise LexerError(
            "Unterminated multi-line comment",
            start_line,
            start_column,
            hint="did you forget to close the comment with '*/'?"
        )
    
    def _scan_token(self) -> None:
        """Scan the next token."""
        self._skip_whitespace()
        
        if self._is_at_end():
            return
        
        start_line = self.line
        start_column = self.column
        char = self._peek()
        
        # Newlines
        if char == '\n':
            self._advance()
            return  # Skip newlines (we don't need NEWLINE tokens for MVP)
        
        # Multi-line comments (/** ... */)
        if char == '/' and self._peek(1) == '*' and self._peek(2) == '*':
            self._skip_multiline_comment(start_line, start_column)
            return
        
        # Single-line comments (//)
        if char == '/' and self._peek(1) == '/':
            self._skip_comment()
            return
        
        # Two-character operators
        if char == '-' and self._peek(1) == '>':
            self._advance()
            self._advance()
            self._add_token(TokenType.ARROW, '->', start_line, start_column)
            return
        
        if char == '=' and self._peek(1) == '>':
            self._advance()
            self._advance()
            self._add_token(TokenType.FAT_ARROW, '=>', start_line, start_column)
            return
        
        if char == '=' and self._peek(1) == '=':
            self._advance()
            self._advance()
            self._add_token(TokenType.EQ, '==', start_line, start_column)
            return
        
        if char == '!' and self._peek(1) == '=':
            self._advance()
            self._advance()
            self._add_token(TokenType.NE, '!=', start_line, start_column)
            return
        
        if char == '<' and self._peek(1) == '=':
            self._advance()
            self._advance()
            self._add_token(TokenType.LE, '<=', start_line, start_column)
            return
        
        if char == '>' and self._peek(1) == '=':
            self._advance()
            self._advance()
            self._add_token(TokenType.GE, '>=', start_line, start_column)
            return
        
        # Single-character operators
        if char == '=':
            self._advance()
            self._add_token(TokenType.ASSIGN, '=', start_line, start_column)
            return
        
        if char == '<':
            self._advance()
            self._add_token(TokenType.LT, '<', start_line, start_column)
            return
        
        if char == '>':
            self._advance()
            self._add_token(TokenType.GT, '>', start_line, start_column)
            return
        
        if char in self.SINGLE_CHARS:
            self._advance()
            self._add_token(self.SINGLE_CHARS[char], char, start_line, start_column)
            return
        
        # String literals
        if char == '"':
            self._scan_string(start_line, start_column)
            return
        
        # Numbers
        if char.isdigit():
            self._scan_number(start_line, start_column)
            return
        
        # Identifiers and keywords
        if char.isalpha() or char == '_':
            self._scan_identifier(start_line, start_column)
            return
        
        raise LexerError(f"Unexpected character: {char!r}", start_line, start_column)
    
    def _scan_string(self, start_line: int, start_column: int) -> None:
        """Scan a string literal."""
        self._advance()  # Opening quote
        value = ''
        
        while not self._is_at_end() and self._peek() != '"':
            if self._peek() == '\n':
                raise LexerError(
                    "Unterminated string (newline in string literal)",
                    start_line,
                    start_column,
                    hint="strings cannot span multiple lines; use \\n for newlines"
                )
            
            if self._peek() == '\\':
                self._advance()
                escape_char = self._advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"'}
                value += escape_map.get(escape_char, escape_char)
            else:
                value += self._advance()
        
        if self._is_at_end():
            raise LexerError(
                "Unterminated string",
                start_line,
                start_column,
                hint="did you forget to close the string with '\"'?"
            )
        
        self._advance()  # Closing quote
        self._add_token(TokenType.STRING, value, start_line, start_column)
    
    def _scan_number(self, start_line: int, start_column: int) -> None:
        """Scan an integer or float literal."""
        # Optimized: use slice instead of building string character by character
        start_pos = self.pos
        source = self.source
        source_len = self.source_len
        pos = self.pos
        
        # Scan integer part
        while pos < source_len and source[pos].isdigit():
            pos += 1
        
        # Check for float
        is_float = False
        if pos < source_len and source[pos] == '.' and pos + 1 < source_len and source[pos + 1].isdigit():
            is_float = True
            pos += 1  # Skip '.'
            while pos < source_len and source[pos].isdigit():
                pos += 1
        
        value = source[start_pos:pos]
        
        # Update position and column
        chars_consumed = pos - self.pos
        self.column += chars_consumed
        self.pos = pos
        
        if is_float:
            self._add_token(TokenType.FLOAT, value, start_line, start_column)
        else:
            self._add_token(TokenType.INT, value, start_line, start_column)
    
    def _scan_identifier(self, start_line: int, start_column: int) -> None:
        """Scan an identifier or keyword."""
        # Optimized: use slice instead of building string character by character
        start_pos = self.pos
        source = self.source
        source_len = self.source_len
        pos = self.pos
        
        # Scan while identifier character
        while pos < source_len:
            char = source[pos]
            if char.isalnum() or char == '_':
                pos += 1
            else:
                break
        
        value = source[start_pos:pos]
        
        # Update position and column
        chars_consumed = pos - self.pos
        self.column += chars_consumed
        self.pos = pos
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(value, TokenType.IDENT)
        self._add_token(token_type, value, start_line, start_column)


def tokenize(source: str) -> list[Token]:
    """Convenience function to tokenize source code."""
    lexer = Lexer(source)
    return lexer.tokenize()
