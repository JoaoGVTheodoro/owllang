"""
Tests for the OwlLang Parser.
"""

import pytest

from owllang import tokenize, parse
from owllang.ast import (
    Program,
    FnDecl,
    Parameter,
    PythonImport,
    PythonFromImport,
    LetStmt,
    ExprStmt,
    ReturnStmt,
    IfStmt,
    IntLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
    Identifier,
    BinaryOp,
    UnaryOp,
    Call,
    FieldAccess,
)
from owllang.parser import Parser, ParseError


class TestProgramParsing:
    """Test top-level program parsing."""
    
    def test_empty_program(self) -> None:
        """Parser handles empty source."""
        tokens = tokenize("")
        program = parse(tokens)
        
        assert isinstance(program, Program)
        assert program.imports == []
        assert program.functions == []
        assert program.statements == []
    
    def test_program_with_imports(self, python_import_source: str) -> None:
        """Parser recognizes imports at program level."""
        tokens = tokenize(python_import_source)
        program = parse(tokens)
        
        assert len(program.imports) == 1
        assert isinstance(program.imports[0], PythonImport)
    
    def test_program_with_functions(self, simple_function_source: str) -> None:
        """Parser recognizes functions at program level."""
        tokens = tokenize(simple_function_source)
        program = parse(tokens)
        
        assert len(program.functions) == 1
        assert isinstance(program.functions[0], FnDecl)
    
    def test_program_with_statements(self, simple_let_source: str) -> None:
        """Parser recognizes top-level statements."""
        tokens = tokenize(simple_let_source)
        program = parse(tokens)
        
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], LetStmt)


class TestImportParsing:
    """Test import statement parsing."""
    
    def test_simple_import(self, python_import_source: str) -> None:
        """Parser handles simple Python import."""
        tokens = tokenize(python_import_source)
        program = parse(tokens)
        
        imp = program.imports[0]
        assert isinstance(imp, PythonImport)
        assert imp.module == "json"
        assert imp.alias is None
    
    def test_import_with_alias(self, python_import_alias_source: str) -> None:
        """Parser handles import with alias."""
        tokens = tokenize(python_import_alias_source)
        program = parse(tokens)
        
        imp = program.imports[0]
        assert isinstance(imp, PythonImport)
        assert imp.module == "numpy"
        assert imp.alias == "np"
    
    def test_from_import(self, python_from_import_source: str) -> None:
        """Parser handles from import."""
        tokens = tokenize(python_from_import_source)
        program = parse(tokens)
        
        imp = program.imports[0]
        assert isinstance(imp, PythonFromImport)
        assert imp.module == "os.path"
        assert ("join", None) in imp.names
        assert ("exists", None) in imp.names


class TestFunctionParsing:
    """Test function declaration parsing."""
    
    def test_function_no_params(self, simple_function_source: str) -> None:
        """Parser handles function without parameters."""
        tokens = tokenize(simple_function_source)
        program = parse(tokens)
        
        fn = program.functions[0]
        assert fn.name == "greet"
        assert fn.params == []
        assert len(fn.body) == 1
    
    def test_function_with_params(self, function_with_params_source: str) -> None:
        """Parser handles function with parameters."""
        tokens = tokenize(function_with_params_source)
        program = parse(tokens)
        
        fn = program.functions[0]
        assert fn.name == "add"
        assert len(fn.params) == 2
        assert fn.params[0].name == "a"
        assert fn.params[1].name == "b"
    
    def test_function_with_return_type(self) -> None:
        """Parser handles function with return type annotation."""
        source = "fn getValue() -> int { return 42 }"
        tokens = tokenize(source)
        program = parse(tokens)
        
        fn = program.functions[0]
        assert fn.return_type == "int"
    
    def test_function_param_with_type(self) -> None:
        """Parser handles parameter with type annotation."""
        source = "fn greet(name: str) { print(name) }"
        tokens = tokenize(source)
        program = parse(tokens)
        
        fn = program.functions[0]
        assert fn.params[0].name == "name"
        assert fn.params[0].type_annotation == "str"


class TestStatementParsing:
    """Test statement parsing."""
    
    def test_let_statement(self, simple_let_source: str) -> None:
        """Parser handles let statement."""
        tokens = tokenize(simple_let_source)
        program = parse(tokens)
        
        stmt = program.statements[0]
        assert isinstance(stmt, LetStmt)
        assert stmt.name == "x"
        assert isinstance(stmt.value, IntLiteral)
        assert stmt.value.value == 42
    
    def test_let_with_type_annotation(self) -> None:
        """Parser handles let with type annotation."""
        source = "let x: int = 42"
        tokens = tokenize(source)
        program = parse(tokens)
        
        stmt = program.statements[0]
        assert isinstance(stmt, LetStmt)
        assert stmt.type_annotation == "int"
    
    def test_return_statement(self) -> None:
        """Parser handles return statement."""
        source = "fn test() { return 42 }"
        tokens = tokenize(source)
        program = parse(tokens)
        
        return_stmt = program.functions[0].body[0]
        assert isinstance(return_stmt, ReturnStmt)
        assert isinstance(return_stmt.value, IntLiteral)
    
    def test_empty_return(self) -> None:
        """Parser handles empty return."""
        source = "fn test() { return }"
        tokens = tokenize(source)
        program = parse(tokens)
        
        return_stmt = program.functions[0].body[0]
        assert isinstance(return_stmt, ReturnStmt)
        assert return_stmt.value is None
    
    def test_if_statement(self, if_else_source: str) -> None:
        """Parser handles if-else statement."""
        tokens = tokenize(if_else_source)
        program = parse(tokens)
        
        fn = program.functions[0]
        if_stmt = fn.body[0]
        assert isinstance(if_stmt, IfStmt)
        assert isinstance(if_stmt.condition, BinaryOp)
        assert len(if_stmt.then_body) == 1
        assert if_stmt.else_body is not None
        assert len(if_stmt.else_body) == 1
    
    def test_expression_statement(self) -> None:
        """Parser handles expression statement."""
        source = "print(42)"
        tokens = tokenize(source)
        program = parse(tokens)
        
        stmt = program.statements[0]
        assert isinstance(stmt, ExprStmt)
        assert isinstance(stmt.expr, Call)


class TestExpressionParsing:
    """Test expression parsing."""
    
    def test_integer_literal(self) -> None:
        """Parser handles integer literal."""
        tokens = tokenize("let x = 42")
        program = parse(tokens)
        
        value = program.statements[0].value
        assert isinstance(value, IntLiteral)
        assert value.value == 42
    
    def test_float_literal(self, float_source: str) -> None:
        """Parser handles float literal."""
        tokens = tokenize(float_source)
        program = parse(tokens)
        
        value = program.statements[0].value
        assert isinstance(value, FloatLiteral)
        assert value.value == pytest.approx(3.14159)
    
    def test_string_literal(self, string_source: str) -> None:
        """Parser handles string literal."""
        tokens = tokenize(string_source)
        program = parse(tokens)
        
        value = program.statements[0].value
        assert isinstance(value, StringLiteral)
        assert value.value == "Hello, World!"
    
    def test_boolean_literals(self, boolean_source: str) -> None:
        """Parser handles boolean literals."""
        tokens = tokenize(boolean_source)
        program = parse(tokens)
        
        yes_val = program.statements[0].value
        no_val = program.statements[1].value
        
        assert isinstance(yes_val, BoolLiteral)
        assert yes_val.value is True
        assert isinstance(no_val, BoolLiteral)
        assert no_val.value is False
    
    def test_identifier(self) -> None:
        """Parser handles identifier."""
        source = "let y = x"
        tokens = tokenize(source)
        program = parse(tokens)
        
        value = program.statements[0].value
        assert isinstance(value, Identifier)
        assert value.name == "x"
    
    def test_binary_operations(self, arithmetic_source: str) -> None:
        """Parser handles binary operations."""
        tokens = tokenize(arithmetic_source)
        program = parse(tokens)
        
        # let a = 10 + 20
        add_expr = program.statements[0].value
        assert isinstance(add_expr, BinaryOp)
        assert add_expr.operator == "+"
    
    def test_unary_operation(self, unary_source: str) -> None:
        """Parser handles unary operations."""
        tokens = tokenize(unary_source)
        program = parse(tokens)
        
        value = program.statements[0].value
        assert isinstance(value, UnaryOp)
        assert value.operator == "-"
        assert isinstance(value.operand, IntLiteral)
    
    def test_comparison_operations(self, comparison_source: str) -> None:
        """Parser handles comparison operations."""
        tokens = tokenize(comparison_source)
        program = parse(tokens)
        
        # Check first comparison: 1 == 1
        eq_expr = program.statements[0].value
        assert isinstance(eq_expr, BinaryOp)
        assert eq_expr.operator == "=="
    
    def test_function_call(self) -> None:
        """Parser handles function call."""
        source = "print(42)"
        tokens = tokenize(source)
        program = parse(tokens)
        
        call = program.statements[0].expr
        assert isinstance(call, Call)
        assert isinstance(call.callee, Identifier)
        assert call.callee.name == "print"
        assert len(call.arguments) == 1
    
    def test_nested_call(self, nested_call_source: str) -> None:
        """Parser handles nested function calls."""
        tokens = tokenize(nested_call_source)
        program = parse(tokens)
        
        outer_call = program.statements[0].expr
        assert isinstance(outer_call, Call)
        
        inner_call = outer_call.arguments[0]
        assert isinstance(inner_call, Call)
    
    def test_field_access(self, field_access_source: str) -> None:
        """Parser handles field access."""
        tokens = tokenize(field_access_source)
        program = parse(tokens)
        
        value = program.statements[0].value
        assert isinstance(value, FieldAccess)
        assert value.field == "pi"
    
    def test_grouped_expression(self) -> None:
        """Parser handles grouped expression."""
        source = "let x = (1 + 2) * 3"
        tokens = tokenize(source)
        program = parse(tokens)
        
        value = program.statements[0].value
        assert isinstance(value, BinaryOp)
        assert value.operator == "*"
        assert isinstance(value.left, BinaryOp)
        assert value.left.operator == "+"


class TestPrecedence:
    """Test operator precedence."""
    
    def test_multiplication_before_addition(self) -> None:
        """Multiplication has higher precedence than addition."""
        source = "let x = 1 + 2 * 3"
        tokens = tokenize(source)
        program = parse(tokens)
        
        # Should parse as 1 + (2 * 3)
        value = program.statements[0].value
        assert isinstance(value, BinaryOp)
        assert value.operator == "+"
        assert isinstance(value.right, BinaryOp)
        assert value.right.operator == "*"
    
    def test_comparison_lowest_precedence(self) -> None:
        """Comparison has lowest precedence."""
        source = "let x = 1 + 2 == 3"
        tokens = tokenize(source)
        program = parse(tokens)
        
        # Should parse as (1 + 2) == 3
        value = program.statements[0].value
        assert isinstance(value, BinaryOp)
        assert value.operator == "=="


class TestErrors:
    """Test error handling."""
    
    def test_missing_equals_in_let(self) -> None:
        """Parser raises error for missing = in let."""
        with pytest.raises(ParseError) as exc_info:
            tokens = tokenize("let x 42")
            parse(tokens)
        
        assert "Expected '='" in str(exc_info.value)
    
    def test_missing_closing_paren(self) -> None:
        """Parser raises error for missing closing paren."""
        with pytest.raises(ParseError) as exc_info:
            tokens = tokenize("fn test( { }")
            parse(tokens)
        
        assert "Expected" in str(exc_info.value)
    
    def test_missing_closing_brace(self) -> None:
        """Parser raises error for missing closing brace."""
        with pytest.raises(ParseError) as exc_info:
            tokens = tokenize("fn test() { let x = 1")
            parse(tokens)
        
        assert "Expected '}'" in str(exc_info.value)
    
    def test_unexpected_token(self) -> None:
        """Parser raises error for unexpected token."""
        with pytest.raises(ParseError) as exc_info:
            tokens = tokenize("let x = }")
            parse(tokens)
        
        assert "Unexpected token" in str(exc_info.value)
    
    def test_error_includes_position(self) -> None:
        """Parse error includes position information."""
        with pytest.raises(ParseError) as exc_info:
            tokens = tokenize("let x 42")
            parse(tokens)
        
        error = exc_info.value
        assert error.token is not None
        assert error.token.line == 1


class TestParserClass:
    """Test Parser class directly."""
    
    def test_parser_instance(self) -> None:
        """Parser can be instantiated and used."""
        tokens = tokenize("let x = 42")
        parser = Parser(tokens)
        program = parser.parse()
        
        assert isinstance(program, Program)
        assert len(program.statements) == 1
