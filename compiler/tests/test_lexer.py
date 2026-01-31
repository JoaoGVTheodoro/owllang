"""
Tests for the OwlLang Lexer.
"""

import pytest

from owllang import tokenize, Token, TokenType
from owllang.lexer import Lexer, LexerError


class TestTokenTypes:
    """Test individual token recognition."""
    
    def test_integer_literal(self) -> None:
        """Lexer recognizes integer literals."""
        tokens = tokenize("42")
        assert len(tokens) == 2  # INT + EOF
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == "42"
    
    def test_float_literal(self, float_source: str) -> None:
        """Lexer recognizes float literals."""
        tokens = tokenize(float_source)
        float_token = next(t for t in tokens if t.type == TokenType.FLOAT)
        assert float_token.value == "3.14159"
    
    def test_string_literal(self) -> None:
        """Lexer recognizes string literals."""
        tokens = tokenize('"Hello"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "Hello"
    
    def test_string_escape_sequences(self) -> None:
        """Lexer handles escape sequences in strings."""
        tokens = tokenize(r'"Hello\nWorld"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "Hello\nWorld"
    
    def test_boolean_true(self) -> None:
        """Lexer recognizes true keyword."""
        tokens = tokenize("true")
        assert tokens[0].type == TokenType.TRUE
    
    def test_boolean_false(self) -> None:
        """Lexer recognizes false keyword."""
        tokens = tokenize("false")
        assert tokens[0].type == TokenType.FALSE
    
    def test_identifier(self) -> None:
        """Lexer recognizes identifiers."""
        tokens = tokenize("myVar")
        assert tokens[0].type == TokenType.IDENT
        assert tokens[0].value == "myVar"
    
    def test_identifier_with_underscore(self) -> None:
        """Lexer recognizes identifiers with underscores."""
        tokens = tokenize("my_var_123")
        assert tokens[0].type == TokenType.IDENT
        assert tokens[0].value == "my_var_123"


class TestKeywords:
    """Test keyword recognition."""
    
    @pytest.mark.parametrize("keyword,expected_type", [
        ("fn", TokenType.FN),
        ("let", TokenType.LET),
        ("from", TokenType.FROM),
        ("python", TokenType.PYTHON),
        ("import", TokenType.IMPORT),
        ("as", TokenType.AS),
        ("if", TokenType.IF),
        ("else", TokenType.ELSE),
        ("return", TokenType.RETURN),
    ])
    def test_keywords(self, keyword: str, expected_type: TokenType) -> None:
        """Lexer recognizes all keywords."""
        tokens = tokenize(keyword)
        assert tokens[0].type == expected_type


class TestOperators:
    """Test operator recognition."""
    
    @pytest.mark.parametrize("operator,expected_type", [
        ("+", TokenType.PLUS),
        ("-", TokenType.MINUS),
        ("*", TokenType.STAR),
        ("/", TokenType.SLASH),
        ("%", TokenType.PERCENT),
        ("=", TokenType.ASSIGN),
        ("==", TokenType.EQ),
        ("!=", TokenType.NE),
        ("<", TokenType.LT),
        (">", TokenType.GT),
        ("<=", TokenType.LE),
        (">=", TokenType.GE),
        ("->", TokenType.ARROW),
    ])
    def test_operators(self, operator: str, expected_type: TokenType) -> None:
        """Lexer recognizes all operators."""
        tokens = tokenize(operator)
        assert tokens[0].type == expected_type


class TestDelimiters:
    """Test delimiter recognition."""
    
    @pytest.mark.parametrize("delimiter,expected_type", [
        ("(", TokenType.LPAREN),
        (")", TokenType.RPAREN),
        ("{", TokenType.LBRACE),
        ("}", TokenType.RBRACE),
        (",", TokenType.COMMA),
        (":", TokenType.COLON),
        (".", TokenType.DOT),
    ])
    def test_delimiters(self, delimiter: str, expected_type: TokenType) -> None:
        """Lexer recognizes all delimiters."""
        tokens = tokenize(delimiter)
        assert tokens[0].type == expected_type


class TestComments:
    """Test comment handling."""
    
    def test_single_line_comment(self) -> None:
        """Lexer skips single-line comments."""
        tokens = tokenize("// this is a comment\n42")
        assert tokens[0].type == TokenType.INT
        assert tokens[0].value == "42"
    
    def test_inline_comment(self, comment_source: str) -> None:
        """Lexer handles inline comments."""
        tokens = tokenize(comment_source)
        # Should have: LET, IDENT, ASSIGN, INT, LET, IDENT, ASSIGN, INT, EOF
        let_tokens = [t for t in tokens if t.type == TokenType.LET]
        assert len(let_tokens) == 2


class TestComplexTokenization:
    """Test tokenization of complex expressions."""
    
    def test_let_statement(self, simple_let_source: str) -> None:
        """Lexer tokenizes let statement correctly."""
        tokens = tokenize(simple_let_source)
        
        assert tokens[0].type == TokenType.LET
        assert tokens[1].type == TokenType.IDENT
        assert tokens[1].value == "x"
        assert tokens[2].type == TokenType.ASSIGN
        assert tokens[3].type == TokenType.INT
        assert tokens[3].value == "42"
        assert tokens[4].type == TokenType.EOF
    
    def test_function_declaration(self, simple_function_source: str) -> None:
        """Lexer tokenizes function declaration."""
        tokens = tokenize(simple_function_source)
        
        token_types = [t.type for t in tokens]
        assert TokenType.FN in token_types
        assert TokenType.LPAREN in token_types
        assert TokenType.RPAREN in token_types
        assert TokenType.LBRACE in token_types
        assert TokenType.RBRACE in token_types
    
    def test_python_import(self, python_import_source: str) -> None:
        """Lexer tokenizes Python import."""
        tokens = tokenize(python_import_source)
        
        assert tokens[0].type == TokenType.FROM
        assert tokens[1].type == TokenType.PYTHON
        assert tokens[2].type == TokenType.IMPORT
        assert tokens[3].type == TokenType.IDENT
        assert tokens[3].value == "json"


class TestPositionTracking:
    """Test line and column tracking."""
    
    def test_line_numbers(self) -> None:
        """Lexer tracks line numbers correctly."""
        source = "let x = 1\nlet y = 2"
        tokens = tokenize(source)
        
        first_let = tokens[0]
        second_let = [t for t in tokens if t.type == TokenType.LET][1]
        
        assert first_let.line == 1
        assert second_let.line == 2
    
    def test_column_numbers(self) -> None:
        """Lexer tracks column numbers correctly."""
        tokens = tokenize("let x = 42")
        
        assert tokens[0].column == 1   # let
        assert tokens[1].column == 5   # x
        assert tokens[2].column == 7   # =
        assert tokens[3].column == 9   # 42


class TestErrors:
    """Test error handling."""
    
    def test_unterminated_string(self) -> None:
        """Lexer raises error for unterminated string."""
        with pytest.raises(LexerError) as exc_info:
            tokenize('"unterminated')
        
        assert "Unterminated string" in str(exc_info.value)
    
    def test_unexpected_character(self) -> None:
        """Lexer raises error for unexpected character."""
        with pytest.raises(LexerError) as exc_info:
            tokenize("let x = @invalid")
        
        assert "Unexpected character" in str(exc_info.value)
    
    def test_error_position(self) -> None:
        """Lexer error includes correct position."""
        with pytest.raises(LexerError) as exc_info:
            tokenize("let x = @")
        
        error = exc_info.value
        assert error.line == 1
        assert error.column == 9


class TestLexerClass:
    """Test Lexer class directly."""
    
    def test_lexer_instance(self) -> None:
        """Lexer can be instantiated and used."""
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.INT
    
    def test_multiple_tokenizations(self) -> None:
        """Multiple tokenize calls work correctly."""
        source = "let x = 1"
        
        tokens1 = tokenize(source)
        tokens2 = tokenize(source)
        
        assert len(tokens1) == len(tokens2)
        for t1, t2 in zip(tokens1, tokens2):
            assert t1.type == t2.type
            assert t1.value == t2.value
