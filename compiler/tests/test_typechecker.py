"""
Tests for the OwlLang Type Checker (Phase 1 & 2)

Phase 1:
- Literals (Int, Float, String, Bool)
- Binary operations
- Variable definitions
- Function calls
- Return type checking
- Error detection

Phase 2:
- Option[T] and Result[T, E] types
- If/else as expression
- Implicit return
"""

import pytest

from owllang.ast import (
    IntLiteral, FloatLiteral, StringLiteral, BoolLiteral,
    Identifier, BinaryOp, UnaryOp, Call, TryExpr,
    LetStmt, ExprStmt, ReturnStmt, IfStmt,
    FnDecl, Parameter, Program, TypeAnnotation,
    # Pattern Matching
    MatchExpr, MatchArm, SomePattern, NonePattern, OkPattern, ErrPattern,
)
from owllang.typechecker import (
    TypeChecker, TypeError,
    INT, FLOAT, STRING, BOOL, VOID, ANY,
    OptionType, ResultType,
)


def T(type_str: str) -> TypeAnnotation:
    """Helper to create TypeAnnotation from string for tests."""
    # Parse simple types and parameterized types
    if "[" not in type_str:
        return TypeAnnotation(type_str)
    
    # Parse parameterized type: "Option[Int]" or "Result[Int, String]"
    name = type_str[:type_str.index("[")]
    params_str = type_str[type_str.index("[") + 1:-1]
    
    # Split params (handle nested brackets)
    params = []
    depth = 0
    current = ""
    for c in params_str:
        if c == "[":
            depth += 1
            current += c
        elif c == "]":
            depth -= 1
            current += c
        elif c == "," and depth == 0:
            params.append(T(current.strip()))
            current = ""
        else:
            current += c
    if current.strip():
        params.append(T(current.strip()))
    
    return TypeAnnotation(name, params)


class TestLiteralTypes:
    """Test that literals have correct types."""
    
    def test_int_literal(self) -> None:
        """Int literal should have Int type."""
        checker = TypeChecker()
        typ = checker._check_expr(IntLiteral(42))
        assert typ == INT
    
    def test_float_literal(self) -> None:
        """Float literal should have Float type."""
        checker = TypeChecker()
        typ = checker._check_expr(FloatLiteral(3.14))
        assert typ == FLOAT
    
    def test_string_literal(self) -> None:
        """String literal should have String type."""
        checker = TypeChecker()
        typ = checker._check_expr(StringLiteral("hello"))
        assert typ == STRING
    
    def test_bool_literal(self) -> None:
        """Bool literal should have Bool type."""
        checker = TypeChecker()
        typ = checker._check_expr(BoolLiteral(True))
        assert typ == BOOL


class TestArithmeticOperations:
    """Test type checking for arithmetic operations."""
    
    def test_int_plus_int(self) -> None:
        """Int + Int = Int"""
        checker = TypeChecker()
        expr = BinaryOp(IntLiteral(1), '+', IntLiteral(2))
        typ = checker._check_expr(expr)
        assert typ == INT
        assert len(checker.errors) == 0
    
    def test_float_plus_float(self) -> None:
        """Float + Float = Float"""
        checker = TypeChecker()
        expr = BinaryOp(FloatLiteral(1.0), '+', FloatLiteral(2.0))
        typ = checker._check_expr(expr)
        assert typ == FLOAT
        assert len(checker.errors) == 0
    
    def test_int_plus_float(self) -> None:
        """Int + Float = Float (numeric promotion)"""
        checker = TypeChecker()
        expr = BinaryOp(IntLiteral(1), '+', FloatLiteral(2.0))
        typ = checker._check_expr(expr)
        assert typ == FLOAT
        assert len(checker.errors) == 0
    
    def test_string_plus_string(self) -> None:
        """String + String = String (concatenation)"""
        checker = TypeChecker()
        expr = BinaryOp(StringLiteral("hello"), '+', StringLiteral(" world"))
        typ = checker._check_expr(expr)
        assert typ == STRING
        assert len(checker.errors) == 0
    
    def test_int_plus_string_error(self) -> None:
        """Int + String should produce error."""
        checker = TypeChecker()
        expr = BinaryOp(IntLiteral(1), '+', StringLiteral("hello"))
        checker._check_expr(expr)
        assert len(checker.errors) == 1
        # Error message should mention the operator issue
        msg = checker.errors[0].message.lower()
        assert "cannot apply" in msg or "+" in checker.errors[0].message
    
    def test_string_minus_string_error(self) -> None:
        """String - String should produce error."""
        checker = TypeChecker()
        expr = BinaryOp(StringLiteral("a"), '-', StringLiteral("b"))
        checker._check_expr(expr)
        assert len(checker.errors) == 1
        # Error message should mention the operator issue
        msg = checker.errors[0].message.lower()
        assert "cannot apply" in msg or "-" in checker.errors[0].message


class TestComparisonOperations:
    """Test type checking for comparison operations."""
    
    def test_int_equals_int(self) -> None:
        """Int == Int = Bool"""
        checker = TypeChecker()
        expr = BinaryOp(IntLiteral(1), '==', IntLiteral(2))
        typ = checker._check_expr(expr)
        assert typ == BOOL
        assert len(checker.errors) == 0
    
    def test_int_less_than_float(self) -> None:
        """Int < Float = Bool"""
        checker = TypeChecker()
        expr = BinaryOp(IntLiteral(1), '<', FloatLiteral(2.0))
        typ = checker._check_expr(expr)
        assert typ == BOOL
        assert len(checker.errors) == 0
    
    def test_string_less_than_int_error(self) -> None:
        """String < Int should produce error."""
        checker = TypeChecker()
        expr = BinaryOp(StringLiteral("a"), '<', IntLiteral(1))
        checker._check_expr(expr)
        assert len(checker.errors) == 1
        assert "cannot compare" in checker.errors[0].message.lower()
    
    def test_int_equals_string_error(self) -> None:
        """Int == String should produce error."""
        checker = TypeChecker()
        expr = BinaryOp(IntLiteral(1), '==', StringLiteral("1"))
        checker._check_expr(expr)
        assert len(checker.errors) == 1
        assert "cannot compare" in checker.errors[0].message.lower()


class TestUnaryOperations:
    """Test type checking for unary operations."""
    
    def test_negate_int(self) -> None:
        """-Int = Int"""
        checker = TypeChecker()
        expr = UnaryOp('-', IntLiteral(42))
        typ = checker._check_expr(expr)
        assert typ == INT
        assert len(checker.errors) == 0
    
    def test_negate_float(self) -> None:
        """-Float = Float"""
        checker = TypeChecker()
        expr = UnaryOp('-', FloatLiteral(3.14))
        typ = checker._check_expr(expr)
        assert typ == FLOAT
        assert len(checker.errors) == 0
    
    def test_negate_string_error(self) -> None:
        """-String should produce error."""
        checker = TypeChecker()
        expr = UnaryOp('-', StringLiteral("hello"))
        checker._check_expr(expr)
        assert len(checker.errors) == 1
        # Error message should indicate operator cannot be applied
        assert "-" in checker.errors[0].message or "negate" in checker.errors[0].message.lower()


class TestVariables:
    """Test type checking for variables."""
    
    def test_defined_variable(self) -> None:
        """Defined variable should have correct type."""
        checker = TypeChecker()
        checker.env.define_var("x", INT)
        typ = checker._check_expr(Identifier("x"))
        assert typ == INT
        assert len(checker.errors) == 0
    
    def test_undefined_variable_error(self) -> None:
        """Undefined variable should produce error."""
        checker = TypeChecker()
        checker._check_expr(Identifier("undefined_var"))
        assert len(checker.errors) == 1
        assert "undefined" in checker.errors[0].message.lower() and "variable" in checker.errors[0].message.lower()
    
    def test_let_statement(self) -> None:
        """Let statement should define variable with correct type."""
        checker = TypeChecker()
        stmt = LetStmt("x", IntLiteral(42))
        checker._check_let(stmt)
        typ = checker.env.lookup_var("x")
        assert typ == INT
        assert len(checker.errors) == 0
    
    def test_let_with_type_annotation(self) -> None:
        """Let with type annotation should verify type matches."""
        checker = TypeChecker()
        # let x: Int = 42
        stmt = LetStmt("x", IntLiteral(42), T("Int"))
        checker._check_let(stmt)
        assert len(checker.errors) == 0
    
    def test_let_with_wrong_type_annotation(self) -> None:
        """Let with wrong type annotation should produce error."""
        checker = TypeChecker()
        # let x: String = 42  # Error!
        stmt = LetStmt("x", IntLiteral(42), T("String"))
        checker._check_let(stmt)
        assert len(checker.errors) == 1
        # Message can be "Type mismatch" or "incompatible types"
        msg = checker.errors[0].message.lower()
        assert "type" in msg or "incompatible" in msg


class TestFunctions:
    """Test type checking for functions."""
    
    def test_function_return_type(self) -> None:
        """Function return type should be checked."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="get_number",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        ReturnStmt(IntLiteral(42))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_function_wrong_return_type(self) -> None:
        """Function with wrong return type should produce error."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="get_number",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        ReturnStmt(StringLiteral("hello"))  # Error!
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 1
        assert "return type mismatch" in errors[0].message.lower()
    
    def test_function_with_params(self) -> None:
        """Function parameters should be in scope."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="add",
                    params=[
                        Parameter("a", T("Int")),
                        Parameter("b", T("Int"))
                    ],
                    return_type=T("Int"),
                    body=[
                        ReturnStmt(BinaryOp(Identifier("a"), '+', Identifier("b")))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0


class TestIfStatement:
    """Test type checking for if statements."""
    
    def test_if_with_bool_condition(self) -> None:
        """If with bool condition should not produce error."""
        checker = TypeChecker()
        stmt = IfStmt(
            condition=BoolLiteral(True),
            then_body=[ExprStmt(IntLiteral(1))],
            else_body=None
        )
        checker._check_if(stmt)
        assert len(checker.errors) == 0
    
    def test_if_with_comparison_condition(self) -> None:
        """If with comparison condition should not produce error."""
        checker = TypeChecker()
        stmt = IfStmt(
            condition=BinaryOp(IntLiteral(1), '<', IntLiteral(2)),
            then_body=[ExprStmt(IntLiteral(1))],
            else_body=None
        )
        checker._check_if(stmt)
        assert len(checker.errors) == 0
    
    def test_if_with_int_condition_error(self) -> None:
        """If with int condition should produce error."""
        checker = TypeChecker()
        stmt = IfStmt(
            condition=IntLiteral(1),  # Error!
            then_body=[ExprStmt(IntLiteral(1))],
            else_body=None
        )
        checker._check_if(stmt)
        assert len(checker.errors) == 1
        assert "condition" in checker.errors[0].message.lower() and "bool" in checker.errors[0].message.lower()


class TestProgramIntegration:
    """Integration tests for full programs."""
    
    def test_valid_program(self) -> None:
        """Valid program should have no errors."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="main",
                    params=[],
                    return_type=T("Void"),
                    body=[
                        LetStmt("x", IntLiteral(10)),
                        LetStmt("y", IntLiteral(20)),
                        LetStmt("sum", BinaryOp(Identifier("x"), '+', Identifier("y"))),
                        ExprStmt(Call(Identifier("print"), [Identifier("sum")]))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_program_with_type_errors(self) -> None:
        """Program with type errors should report them."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="bad",
                    params=[],
                    return_type=T("Void"),
                    body=[
                        # x = 10 + "hello" # Error!
                        LetStmt("x", BinaryOp(IntLiteral(10), '+', StringLiteral("hello"))),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 1
        # Error message should mention the operator issue
        msg = errors[0].message.lower()
        assert "cannot apply" in msg or "+" in errors[0].message


# =============================================================================
# PHASE 2 TESTS: Option[T] and Result[T, E]
# =============================================================================

class TestOptionType:
    """Test Option[T] type checking."""
    
    def test_some_int_has_option_int_type(self) -> None:
        """Some(10) should have type Option[Int]."""
        checker = TypeChecker()
        # Some(10)
        expr = Call(Identifier("Some"), [IntLiteral(10)])
        typ = checker._check_expr(expr)
        assert isinstance(typ, OptionType)
        assert typ.inner == INT
    
    def test_some_string_has_option_string_type(self) -> None:
        """Some("hello") should have type Option[String]."""
        checker = TypeChecker()
        expr = Call(Identifier("Some"), [StringLiteral("hello")])
        typ = checker._check_expr(expr)
        assert isinstance(typ, OptionType)
        assert typ.inner == STRING
    
    def test_none_has_option_any_type(self) -> None:
        """None should have type Option[Any]."""
        checker = TypeChecker()
        expr = Identifier("None")
        typ = checker._check_expr(expr)
        assert isinstance(typ, OptionType)
        assert typ.inner == ANY
    
    def test_option_int_assignment_correct(self) -> None:
        """let x: Option[Int] = Some(10) should work."""
        checker = TypeChecker()
        # let x: Option[Int] = Some(10)
        stmt = LetStmt("x", Call(Identifier("Some"), [IntLiteral(10)]), T("Option[Int]"))
        checker._check_let(stmt)
        assert len(checker.errors) == 0
    
    def test_option_assigned_to_int_error(self) -> None:
        """let x: Int = Some(10) should produce error."""
        checker = TypeChecker()
        # let x: Int = Some(10)  # ERROR!
        stmt = LetStmt("x", Call(Identifier("Some"), [IntLiteral(10)]), T("Int"))
        checker._check_let(stmt)
        assert len(checker.errors) == 1
        # Message can be "Type mismatch" or "incompatible types"
        msg = checker.errors[0].message.lower()
        assert "type" in msg or "incompatible" in msg
    
    def test_none_assigned_to_option_correct(self) -> None:
        """let x: Option[Int] = None should work."""
        checker = TypeChecker()
        stmt = LetStmt("x", Identifier("None"), T("Option[Int]"))
        checker._check_let(stmt)
        assert len(checker.errors) == 0
    
    def test_some_requires_one_argument(self) -> None:
        """Some() with no arguments should error."""
        checker = TypeChecker()
        expr = Call(Identifier("Some"), [])
        checker._check_expr(expr)
        assert len(checker.errors) == 1
        assert "Some" in checker.errors[0].message


class TestResultType:
    """Test Result[T, E] type checking."""
    
    def test_ok_int_has_result_type(self) -> None:
        """Ok(10) should have type Result[Int, Any]."""
        checker = TypeChecker()
        expr = Call(Identifier("Ok"), [IntLiteral(10)])
        typ = checker._check_expr(expr)
        assert isinstance(typ, ResultType)
        assert typ.ok_type == INT
        assert typ.err_type == ANY
    
    def test_err_string_has_result_type(self) -> None:
        """Err("error") should have type Result[Any, String]."""
        checker = TypeChecker()
        expr = Call(Identifier("Err"), [StringLiteral("error")])
        typ = checker._check_expr(expr)
        assert isinstance(typ, ResultType)
        assert typ.ok_type == ANY
        assert typ.err_type == STRING
    
    def test_result_assignment_correct(self) -> None:
        """let x: Result[Int, String] = Ok(10) should work."""
        checker = TypeChecker()
        stmt = LetStmt("x", Call(Identifier("Ok"), [IntLiteral(10)]), T("Result[Int, String]"))
        checker._check_let(stmt)
        assert len(checker.errors) == 0
    
    def test_result_assigned_to_int_error(self) -> None:
        """let x: Int = Ok(10) should produce error."""
        checker = TypeChecker()
        stmt = LetStmt("x", Call(Identifier("Ok"), [IntLiteral(10)]), T("Int"))
        checker._check_let(stmt)
        assert len(checker.errors) == 1
        # Message can be "Type mismatch" or "incompatible types"
        msg = checker.errors[0].message.lower()
        assert "type" in msg or "incompatible" in msg
    
    def test_err_assigned_to_result_correct(self) -> None:
        """let x: Result[Int, String] = Err("oops") should work."""
        checker = TypeChecker()
        stmt = LetStmt("x", Call(Identifier("Err"), [StringLiteral("oops")]), T("Result[Int, String]"))
        checker._check_let(stmt)
        assert len(checker.errors) == 0
    
    def test_ok_requires_one_argument(self) -> None:
        """Ok() with no arguments should error."""
        checker = TypeChecker()
        expr = Call(Identifier("Ok"), [])
        checker._check_expr(expr)
        assert len(checker.errors) == 1
        assert "Ok" in checker.errors[0].message


class TestFunctionWithOptionResult:
    """Test functions returning Option/Result."""
    
    def test_function_returns_option_int(self) -> None:
        """Function returning Option[Int] with Some(x) should pass."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="maybe_number",
                    params=[],
                    return_type=T("Option[Int]"),
                    body=[
                        ReturnStmt(Call(Identifier("Some"), [IntLiteral(42)]))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_function_returns_result_ok(self) -> None:
        """Function returning Result[Int, String] with Ok(x) should pass."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="get_result",
                    params=[],
                    return_type=T("Result[Int, String]"),
                    body=[
                        ReturnStmt(Call(Identifier("Ok"), [IntLiteral(42)]))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_function_returns_wrong_option_type_error(self) -> None:
        """Function returning Option[Int] with Some("str") should error."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="bad_option",
                    params=[],
                    return_type=T("Option[Int]"),
                    body=[
                        ReturnStmt(Call(Identifier("Some"), [StringLiteral("wrong")]))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 1
        assert "return type mismatch" in errors[0].message.lower()


class TestIfAsExpression:
    """Test if/else as typed expression."""
    
    def test_if_else_same_type_valid(self) -> None:
        """If branches with same type should be valid."""
        checker = TypeChecker()
        # let x = if true { 10 } else { 20 }
        stmt = IfStmt(
            condition=BoolLiteral(True),
            then_body=[ExprStmt(IntLiteral(10))],
            else_body=[ExprStmt(IntLiteral(20))]
        )
        typ = checker._check_if_expr(stmt)
        assert typ == INT
        assert len(checker.errors) == 0
    
    def test_if_else_different_types_error(self) -> None:
        """If branches with different types should error."""
        checker = TypeChecker()
        # let x = if true { 10 } else { "nope" }  # ERROR!
        stmt = IfStmt(
            condition=BoolLiteral(True),
            then_body=[ExprStmt(IntLiteral(10))],
            else_body=[ExprStmt(StringLiteral("nope"))]
        )
        checker._check_if_expr(stmt)
        assert len(checker.errors) == 1
        assert "branch" in checker.errors[0].message.lower() or "incompatible" in checker.errors[0].message.lower()
    
    def test_if_without_else_returns_void(self) -> None:
        """If without else should have Void type."""
        checker = TypeChecker()
        stmt = IfStmt(
            condition=BoolLiteral(True),
            then_body=[ExprStmt(IntLiteral(10))],
            else_body=None
        )
        typ = checker._check_if_expr(stmt)
        assert typ == VOID
        assert len(checker.errors) == 0


class TestImplicitReturn:
    """Test implicit return (last expression as return value)."""
    
    def test_implicit_return_int(self) -> None:
        """Last expression should be implicit return."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="add",
                    params=[
                        Parameter("a", T("Int")),
                        Parameter("b", T("Int"))
                    ],
                    return_type=T("Int"),
                    body=[
                        # a + b  (implicit return)
                        ExprStmt(BinaryOp(Identifier("a"), '+', Identifier("b")))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_implicit_return_wrong_type_error(self) -> None:
        """Implicit return with wrong type should error."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="bad",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        # "hello"  (implicit return, but wrong type!)
                        ExprStmt(StringLiteral("hello"))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 1
        assert "return" in errors[0].message.lower() or "mismatch" in errors[0].message.lower()
    
    def test_implicit_return_option(self) -> None:
        """Implicit return with Option type should work."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="maybe",
                    params=[],
                    return_type=T("Option[Int]"),
                    body=[
                        ExprStmt(Call(Identifier("Some"), [IntLiteral(42)]))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_implicit_return_with_match_option(self) -> None:
        """match expression as implicit return should work."""
        # fn f(x: Option[Int]) -> Int {
        #     match x { Some(v) => v, None => 0 }
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("x", T("Option[Int]"))],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(MatchExpr(
                            subject=Identifier("x"),
                            arms=[
                                MatchArm(SomePattern("v"), Identifier("v")),
                                MatchArm(NonePattern(), IntLiteral(0)),
                            ]
                        ))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_implicit_return_with_match_result(self) -> None:
        """match on Result as implicit return should work."""
        # fn f(x: Result[Int, String]) -> Int {
        #     match x { Ok(v) => v, Err(e) => 0 }
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("x", T("Result[Int, String]"))],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(MatchExpr(
                            subject=Identifier("x"),
                            arms=[
                                MatchArm(OkPattern("v"), Identifier("v")),
                                MatchArm(ErrPattern("e"), IntLiteral(0)),
                            ]
                        ))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_implicit_return_with_if_else(self) -> None:
        """if/else expression as implicit return should work."""
        # fn f(x: Bool) -> Int {
        #     if x { 1 } else { 0 }
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("x", T("Bool"))],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(IfStmt(
                            condition=Identifier("x"),
                            then_body=[ExprStmt(IntLiteral(1))],
                            else_body=[ExprStmt(IntLiteral(0))],
                        ))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_if_without_else_not_exhaustive(self) -> None:
        """if without else as return should error (not all paths return)."""
        # fn bad(x: Bool) -> Int {
        #     if x { 1 }
        # } // ERROR: not all paths return
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="bad",
                    params=[Parameter("x", T("Bool"))],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(IfStmt(
                            condition=Identifier("x"),
                            then_body=[ExprStmt(IntLiteral(1))],
                            else_body=None,  # No else!
                        ))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) >= 1
        # Should mention that not all paths return or missing else
        assert any("path" in e.message.lower() or "else" in e.message.lower() or "return" in e.message.lower() for e in errors)
    
    def test_empty_body_function_with_return_type_error(self) -> None:
        """Function with return type but empty body should error."""
        # fn bad() -> Int { }  // ERROR: no return
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="bad",
                    params=[],
                    return_type=T("Int"),
                    body=[]  # Empty body!
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) >= 1
    
    def test_let_as_last_statement_not_return(self) -> None:
        """Let as last statement is not an expression return."""
        # fn bad() -> Int {
        #     let x = 42
        # } // ERROR: let is not an expression
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="bad",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        LetStmt(name="x", value=IntLiteral(42), type_annotation=None)
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) >= 1


# =============================================================================
# TRY OPERATOR (?) TESTS
# =============================================================================

class TestTryOperator:
    """Test the ? operator for Result error propagation."""
    
    def test_try_on_result_returns_ok_type(self) -> None:
        """expr? on Result[Int, String] should return Int."""
        checker = TypeChecker()
        # Set up a function that returns Result
        checker.current_function_return_type = ResultType(INT, STRING)
        
        # Ok(42)?
        expr = TryExpr(Call(Identifier("Ok"), [IntLiteral(42)]))
        typ = checker._check_expr(expr)
        
        assert typ == INT
        assert len(checker.errors) == 0
    
    def test_try_on_non_result_is_error(self) -> None:
        """expr? on non-Result type should produce error."""
        checker = TypeChecker()
        checker.current_function_return_type = ResultType(INT, STRING)
        
        # 42? - Int is not a Result
        expr = TryExpr(IntLiteral(42))
        checker._check_expr(expr)
        
        assert len(checker.errors) == 1
        assert "Result" in checker.errors[0].message
    
    def test_try_outside_result_function_is_error(self) -> None:
        """? used outside a Result-returning function should error."""
        checker = TypeChecker()
        # Function returns Int, not Result
        checker.current_function_return_type = INT
        
        expr = TryExpr(Call(Identifier("Ok"), [IntLiteral(42)]))
        checker._check_expr(expr)
        
        assert len(checker.errors) == 1
        assert "Result" in checker.errors[0].message
    
    def test_try_in_function_returning_result(self) -> None:
        """? should work in function returning Result."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="process",
                    params=[],
                    return_type=T("Result[Int, String]"),
                    body=[
                        LetStmt("x", TryExpr(Call(Identifier("Ok"), [IntLiteral(10)]))),
                        ExprStmt(Call(Identifier("Ok"), [BinaryOp(Identifier("x"), "*", IntLiteral(2))]))
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        assert len(errors) == 0
    
    def test_try_error_type_compatibility(self) -> None:
        """? requires compatible error types."""
        checker = TypeChecker()
        # Function returns Result[Int, Int]
        checker.current_function_return_type = ResultType(INT, INT)
        
        # Err("string")? - String error not compatible with Int error
        expr = TryExpr(Call(Identifier("Err"), [StringLiteral("oops")]))
        checker._check_expr(expr)
        
        assert len(checker.errors) == 1
        assert "Incompatible" in checker.errors[0].message or "error" in checker.errors[0].message.lower()
    
    def test_chained_try_operators(self) -> None:
        """Chained ? operators should work correctly."""
        checker = TypeChecker()
        checker.current_function_return_type = ResultType(INT, STRING)
        
        # (Ok(42)?)  - first ? returns Int
        inner_try = TryExpr(Call(Identifier("Ok"), [IntLiteral(42)]))
        typ = checker._check_expr(inner_try)
        assert typ == INT
        assert len(checker.errors) == 0


# =============================================================================
# PARAMETERIZED TYPE ARITY TESTS
# =============================================================================

class TestTypeAnnotationArity:
    """Test type annotation arity validation."""
    
    def test_option_requires_one_param(self) -> None:
        """Option without type parameter should error."""
        checker = TypeChecker()
        # Option without param
        type_ann = TypeAnnotation("Option", [])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 1
        assert "expects 1 type parameter" in checker.errors[0].message
    
    def test_option_too_many_params(self) -> None:
        """Option[Int, String] should error."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Option", [TypeAnnotation("Int"), TypeAnnotation("String")])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 1
        assert "expects 1 type parameter" in checker.errors[0].message
        assert "2 were provided" in checker.errors[0].message
    
    def test_result_requires_two_params(self) -> None:
        """Result[Int] (only one param) should error."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Result", [TypeAnnotation("Int")])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 1
        assert "expects 2 type parameters" in checker.errors[0].message
        assert "1 was provided" in checker.errors[0].message
    
    def test_result_no_params_error(self) -> None:
        """Result without params should error."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Result", [])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 1
        assert "expects 2 type parameters" in checker.errors[0].message
    
    def test_result_too_many_params(self) -> None:
        """Result[Int, String, Bool] should error."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Result", [
            TypeAnnotation("Int"),
            TypeAnnotation("String"),
            TypeAnnotation("Bool")
        ])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 1
        assert "expects 2 type parameters" in checker.errors[0].message
    
    def test_primitive_with_params_error(self) -> None:
        """Int[String] should error (primitives don't take params)."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Int", [TypeAnnotation("String")])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 1
        assert "expects 0 type parameter" in checker.errors[0].message
    
    def test_unknown_type_error(self) -> None:
        """Unknown type should produce error."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("MyCustomType", [])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 1
        assert "unknown type" in checker.errors[0].message.lower()
        assert "MyCustomType" in checker.errors[0].message
    
    def test_correct_option_int(self) -> None:
        """Option[Int] should work correctly."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Option", [TypeAnnotation("Int")])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 0
        assert isinstance(result, OptionType)
        assert result.inner == INT
    
    def test_correct_result_int_string(self) -> None:
        """Result[Int, String] should work correctly."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Result", [TypeAnnotation("Int"), TypeAnnotation("String")])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 0
        assert isinstance(result, ResultType)
        assert result.ok_type == INT
        assert result.err_type == STRING
    
    def test_nested_type_validation(self) -> None:
        """Result[Option[Int], String] should work correctly."""
        checker = TypeChecker()
        type_ann = TypeAnnotation("Result", [
            TypeAnnotation("Option", [TypeAnnotation("Int")]),
            TypeAnnotation("String")
        ])
        result = checker._parse_type(type_ann)
        
        assert len(checker.errors) == 0
        assert isinstance(result, ResultType)
        assert isinstance(result.ok_type, OptionType)
        assert result.ok_type.inner == INT


# =============================================================================
# MATCH EXPRESSION TESTS
# =============================================================================

class TestMatchExpression:
    """Test type checking of match expressions."""
    
    def test_match_option_returns_inner_type(self) -> None:
        """match Option[Int] with Some(x)/None returns Int."""
        checker = TypeChecker()
        checker.env.define_var("opt", OptionType(INT))
        
        match_expr = MatchExpr(
            subject=Identifier("opt"),
            arms=[
                MatchArm(SomePattern("v"), Identifier("v")),
                MatchArm(NonePattern(), IntLiteral(0)),
            ]
        )
        
        result = checker._check_expr(match_expr)
        
        assert len(checker.errors) == 0
        assert result == INT
    
    def test_match_result_returns_ok_type(self) -> None:
        """match Result[Int, String] with Ok(v)/Err(e) returns Int."""
        checker = TypeChecker()
        checker.env.define_var("res", ResultType(INT, STRING))
        
        match_expr = MatchExpr(
            subject=Identifier("res"),
            arms=[
                MatchArm(OkPattern("v"), Identifier("v")),
                MatchArm(ErrPattern("e"), IntLiteral(0)),
            ]
        )
        
        result = checker._check_expr(match_expr)
        
        assert len(checker.errors) == 0
        assert result == INT
    
    def test_match_some_binding_has_inner_type(self) -> None:
        """Some(x) binding should have the Option's inner type."""
        checker = TypeChecker()
        checker.env.define_var("opt", OptionType(STRING))
        
        # match opt { Some(s) => s, None => "" }
        match_expr = MatchExpr(
            subject=Identifier("opt"),
            arms=[
                MatchArm(SomePattern("s"), Identifier("s")),
                MatchArm(NonePattern(), StringLiteral("")),
            ]
        )
        
        result = checker._check_expr(match_expr)
        
        assert len(checker.errors) == 0
        assert result == STRING
    
    def test_match_ok_binding_has_ok_type(self) -> None:
        """Ok(v) binding should have Result's Ok type."""
        checker = TypeChecker()
        checker.env.define_var("res", ResultType(FLOAT, STRING))
        
        match_expr = MatchExpr(
            subject=Identifier("res"),
            arms=[
                MatchArm(OkPattern("v"), Identifier("v")),
                MatchArm(ErrPattern("e"), FloatLiteral(0.0)),
            ]
        )
        
        result = checker._check_expr(match_expr)
        
        assert len(checker.errors) == 0
        assert result == FLOAT
    
    def test_match_err_binding_has_err_type(self) -> None:
        """Err(e) binding should have Result's Err type."""
        checker = TypeChecker()
        checker.env.define_var("res", ResultType(INT, STRING))
        
        # match res { Ok(v) => "", Err(e) => e }
        match_expr = MatchExpr(
            subject=Identifier("res"),
            arms=[
                MatchArm(OkPattern("v"), StringLiteral("")),
                MatchArm(ErrPattern("e"), Identifier("e")),
            ]
        )
        
        result = checker._check_expr(match_expr)
        
        assert len(checker.errors) == 0
        assert result == STRING
    
    def test_match_exhaustivity_option_missing_none(self) -> None:
        """Missing None arm should error."""
        checker = TypeChecker()
        checker.env.define_var("opt", OptionType(INT))
        
        match_expr = MatchExpr(
            subject=Identifier("opt"),
            arms=[
                MatchArm(SomePattern("v"), Identifier("v")),
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) == 1
        assert "exhaustive" in checker.errors[0].message.lower() or "None" in checker.errors[0].message
    
    def test_match_exhaustivity_option_missing_some(self) -> None:
        """Missing Some arm should error."""
        checker = TypeChecker()
        checker.env.define_var("opt", OptionType(INT))
        
        match_expr = MatchExpr(
            subject=Identifier("opt"),
            arms=[
                MatchArm(NonePattern(), IntLiteral(0)),
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) == 1
        assert "exhaustive" in checker.errors[0].message.lower() or "Some" in checker.errors[0].message
    
    def test_match_exhaustivity_result_missing_err(self) -> None:
        """Missing Err arm should error."""
        checker = TypeChecker()
        checker.env.define_var("res", ResultType(INT, STRING))
        
        match_expr = MatchExpr(
            subject=Identifier("res"),
            arms=[
                MatchArm(OkPattern("v"), Identifier("v")),
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) == 1
        assert "exhaustive" in checker.errors[0].message.lower() or "Err" in checker.errors[0].message
    
    def test_match_exhaustivity_result_missing_ok(self) -> None:
        """Missing Ok arm should error."""
        checker = TypeChecker()
        checker.env.define_var("res", ResultType(INT, STRING))
        
        match_expr = MatchExpr(
            subject=Identifier("res"),
            arms=[
                MatchArm(ErrPattern("e"), IntLiteral(0)),
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) == 1
        assert "exhaustive" in checker.errors[0].message.lower() or "Ok" in checker.errors[0].message
    
    def test_match_branch_type_mismatch(self) -> None:
        """Branches with different types should error."""
        checker = TypeChecker()
        checker.env.define_var("opt", OptionType(INT))
        
        match_expr = MatchExpr(
            subject=Identifier("opt"),
            arms=[
                MatchArm(SomePattern("v"), Identifier("v")),  # Int
                MatchArm(NonePattern(), StringLiteral("none")),  # String
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) == 1
        assert "type" in checker.errors[0].message.lower()
    
    def test_match_on_non_option_non_result(self) -> None:
        """match on Int should error (only Option/Result supported)."""
        checker = TypeChecker()
        checker.env.define_var("x", INT)
        
        match_expr = MatchExpr(
            subject=Identifier("x"),
            arms=[
                MatchArm(SomePattern("v"), Identifier("v")),
                MatchArm(NonePattern(), IntLiteral(0)),
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) >= 1
        assert "Option" in checker.errors[0].message or "Result" in checker.errors[0].message
    
    def test_match_option_with_result_patterns_error(self) -> None:
        """Using Ok/Err patterns on Option should error."""
        checker = TypeChecker()
        checker.env.define_var("opt", OptionType(INT))
        
        match_expr = MatchExpr(
            subject=Identifier("opt"),
            arms=[
                MatchArm(OkPattern("v"), Identifier("v")),
                MatchArm(ErrPattern("e"), IntLiteral(0)),
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) >= 1
    
    def test_match_result_with_option_patterns_error(self) -> None:
        """Using Some/None patterns on Result should error."""
        checker = TypeChecker()
        checker.env.define_var("res", ResultType(INT, STRING))
        
        match_expr = MatchExpr(
            subject=Identifier("res"),
            arms=[
                MatchArm(SomePattern("v"), Identifier("v")),
                MatchArm(NonePattern(), IntLiteral(0)),
            ]
        )
        
        checker._check_expr(match_expr)
        
        assert len(checker.errors) >= 1
