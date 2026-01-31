"""
Semantic consistency tests for OwlLang v0.1.4-alpha.

These tests verify that:
1. Expression vs statement semantics are predictable
2. Return semantics are consistent
3. Scope and shadowing rules are well-defined
4. Diagnostic messages follow consistent patterns
"""

import pytest
from owllang.ast import (
    Program, FnDecl, Parameter, LetStmt, ExprStmt, ReturnStmt, IfStmt,
    MatchExpr, MatchArm, SomePattern, NonePattern, OkPattern, ErrPattern,
    IntLiteral, StringLiteral, BoolLiteral, Identifier, BinaryOp, Call,
    TypeAnnotation as T
)
from owllang.typechecker import TypeChecker
from owllang.typechecker.types import OptionType, ResultType, INT, STRING
from owllang.diagnostics import WarningCode, Warning


# =============================================================================
# Test Helpers
# =============================================================================

def check_program(program: Program) -> TypeChecker:
    """Run type checker and return it for inspection."""
    checker = TypeChecker()
    checker.check(program)
    return checker


def get_warnings_by_code(checker: TypeChecker, code: WarningCode) -> list[Warning]:
    """Filter warnings by code."""
    return [w for w in checker.get_warnings() if w.code == code]


def make_fn(name: str, params: list[Parameter], body: list, return_type=None) -> FnDecl:
    """Helper to create function declarations."""
    return FnDecl(name=name, params=params, return_type=return_type, body=body)


def make_program(functions: list[FnDecl], statements: list = None) -> Program:
    """Helper to create programs."""
    return Program(imports=[], functions=functions, statements=statements or [])


# =============================================================================
# 1. Expression vs Statement Normalization Tests
# =============================================================================

class TestExpressionStatementSemantics:
    """Test that expression/statement semantics are predictable."""
    
    def test_result_ignored_in_statement_warns(self) -> None:
        """Ignoring Result value in statement position should warn."""
        # fn get_result() -> Result[Int, String] { Ok(42) }
        # fn test() { get_result() }  // Warning: Result ignored
        program = make_program([
            make_fn("get_result", [], [
                ExprStmt(Call(Identifier("Ok"), [IntLiteral(42)]))
            ], T("Result", [T("Int"), T("String")])),
            make_fn("test", [], [
                ExprStmt(Call(Identifier("get_result"), []))
            ])
        ])
        checker = check_program(program)
        warnings = get_warnings_by_code(checker, WarningCode.RESULT_IGNORED)
        assert len(warnings) == 1
    
    def test_option_ignored_in_statement_warns(self) -> None:
        """Ignoring Option value in statement position should warn."""
        program = make_program([
            make_fn("get_option", [], [
                ExprStmt(Call(Identifier("Some"), [IntLiteral(42)]))
            ], T("Option", [T("Int")])),
            make_fn("test", [], [
                ExprStmt(Call(Identifier("get_option"), []))
            ])
        ])
        checker = check_program(program)
        warnings = get_warnings_by_code(checker, WarningCode.OPTION_IGNORED)
        assert len(warnings) == 1
    
    def test_int_value_in_statement_no_warning(self) -> None:
        """Plain values (Int, String, etc.) in statement don't warn."""
        program = make_program([
            make_fn("f", [], [
                ExprStmt(IntLiteral(42)),  # Just an int - no warning
            ])
        ])
        checker = check_program(program)
        # Should not warn for plain values
        result_warnings = get_warnings_by_code(checker, WarningCode.RESULT_IGNORED)
        option_warnings = get_warnings_by_code(checker, WarningCode.OPTION_IGNORED)
        assert len(result_warnings) == 0
        assert len(option_warnings) == 0
    
    def test_implicit_return_not_warned(self) -> None:
        """Last expression used as implicit return should NOT warn."""
        program = make_program([
            make_fn("get_result", [], [
                ExprStmt(Call(Identifier("Ok"), [IntLiteral(42)]))
            ], T("Result", [T("Int"), T("String")])),
            # This function returns Result and uses get_result() as implicit return
            make_fn("wrapper", [], [
                ExprStmt(Call(Identifier("get_result"), []))
            ], T("Result", [T("Int"), T("String")]))
        ])
        checker = check_program(program)
        # Should NOT warn since it's used as implicit return
        warnings = get_warnings_by_code(checker, WarningCode.RESULT_IGNORED)
        assert len(warnings) == 0
    
    def test_constant_condition_warns(self) -> None:
        """if true / if false should warn about constant condition."""
        program = make_program([
            make_fn("f", [], [
                IfStmt(BoolLiteral(True), [ExprStmt(IntLiteral(1))], None)
            ])
        ])
        checker = check_program(program)
        warnings = get_warnings_by_code(checker, WarningCode.CONSTANT_CONDITION)
        assert len(warnings) == 1


# =============================================================================
# 2. Return Semantics Tests
# =============================================================================

class TestReturnSemantics:
    """Test that return semantics are consistent."""
    
    def test_unreachable_code_after_return_warns(self) -> None:
        """Code after return should generate warning."""
        program = make_program([
            make_fn("f", [], [
                ReturnStmt(IntLiteral(1)),
                ExprStmt(IntLiteral(2)),  # Unreachable
            ], T("Int"))
        ])
        checker = check_program(program)
        warnings = get_warnings_by_code(checker, WarningCode.UNREACHABLE_CODE)
        assert len(warnings) == 1
    
    def test_multiple_unreachable_statements_all_warn(self) -> None:
        """Each unreachable statement should warn individually."""
        program = make_program([
            make_fn("f", [], [
                ReturnStmt(IntLiteral(1)),
                ExprStmt(IntLiteral(2)),  # Unreachable
                ExprStmt(IntLiteral(3)),  # Also unreachable
                LetStmt("x", IntLiteral(4)),  # Also unreachable
            ], T("Int"))
        ])
        checker = check_program(program)
        warnings = get_warnings_by_code(checker, WarningCode.UNREACHABLE_CODE)
        assert len(warnings) == 3
    
    def test_early_return_in_if_branch(self) -> None:
        """Early return in if branch should not cause errors."""
        program = make_program([
            make_fn("f", [Parameter("x", T("Int"))], [
                IfStmt(
                    BinaryOp(Identifier("x"), "<", IntLiteral(0)),
                    [ReturnStmt(IntLiteral(0))],
                    None
                ),
                ExprStmt(Identifier("x"))  # Implicit return
            ], T("Int"))
        ])
        checker = check_program(program)
        assert len(checker.errors) == 0
    
    def test_exhaustive_return_in_if_else(self) -> None:
        """Return in both branches should be valid."""
        program = make_program([
            make_fn("f", [Parameter("x", T("Bool"))], [
                IfStmt(
                    Identifier("x"),
                    [ReturnStmt(IntLiteral(1))],
                    [ReturnStmt(IntLiteral(2))]
                ),
            ], T("Int"))
        ])
        checker = check_program(program)
        assert len(checker.errors) == 0


# =============================================================================
# 3. Scope and Shadowing Tests
# =============================================================================

class TestScopeAndShadowing:
    """Test that scope and shadowing rules are consistent."""
    
    def test_parameter_used_no_warning(self) -> None:
        """Used parameter should not warn."""
        program = make_program([
            make_fn("f", [Parameter("x", T("Int"))], [
                ExprStmt(Identifier("x"))
            ], T("Int"))
        ])
        checker = check_program(program)
        unused_warnings = get_warnings_by_code(checker, WarningCode.UNUSED_PARAMETER)
        assert len(unused_warnings) == 0
    
    def test_parameter_unused_warns(self) -> None:
        """Unused parameter should warn."""
        program = make_program([
            make_fn("f", [Parameter("x", T("Int"))], [
                ExprStmt(IntLiteral(42))
            ], T("Int"))
        ])
        checker = check_program(program)
        unused_warnings = get_warnings_by_code(checker, WarningCode.UNUSED_PARAMETER)
        assert len(unused_warnings) == 1
        assert "x" in unused_warnings[0].message
    
    def test_underscore_prefix_suppresses_warning(self) -> None:
        """Variables prefixed with _ should not warn about unused."""
        program = make_program([
            make_fn("f", [Parameter("_x", T("Int"))], [
                ExprStmt(IntLiteral(42))
            ], T("Int"))
        ])
        checker = check_program(program)
        unused_warnings = get_warnings_by_code(checker, WarningCode.UNUSED_PARAMETER)
        assert len(unused_warnings) == 0
    
    def test_variable_unused_warns(self) -> None:
        """Unused variable should warn."""
        program = make_program([
            make_fn("f", [], [
                LetStmt("x", IntLiteral(42)),
                ExprStmt(IntLiteral(0))
            ])
        ])
        checker = check_program(program)
        unused_warnings = get_warnings_by_code(checker, WarningCode.UNUSED_VARIABLE)
        assert len(unused_warnings) == 1
        assert "x" in unused_warnings[0].message
    
    def test_variable_used_in_nested_scope(self) -> None:
        """Variable used in if body should be marked as used."""
        program = make_program([
            make_fn("f", [], [
                LetStmt("x", IntLiteral(42)),
                IfStmt(
                    BoolLiteral(True),
                    [ExprStmt(Identifier("x"))],
                    None
                )
            ])
        ])
        checker = check_program(program)
        unused_warnings = get_warnings_by_code(checker, WarningCode.UNUSED_VARIABLE)
        assert len(unused_warnings) == 0


# =============================================================================
# 4. Diagnostic Message Consistency Tests
# =============================================================================

class TestDiagnosticConsistency:
    """Test that diagnostic messages are consistent."""
    
    def test_warning_messages_use_backticks_for_names(self) -> None:
        """Variable/parameter names in warnings should use backticks."""
        program = make_program([
            make_fn("f", [Parameter("myVar", T("Int"))], [
                ExprStmt(IntLiteral(42))
            ])
        ])
        checker = check_program(program)
        unused = get_warnings_by_code(checker, WarningCode.UNUSED_PARAMETER)
        assert len(unused) == 1
        # Should use backticks around the variable name
        assert "`myVar`" in unused[0].message
    
    def test_all_warnings_have_hints(self) -> None:
        """All warning types should include helpful hints."""
        # Unused variable
        program1 = make_program([
            make_fn("f", [], [
                LetStmt("x", IntLiteral(42))
            ])
        ])
        checker1 = check_program(program1)
        for w in checker1.get_warnings():
            assert len(w.hints) > 0, f"Warning {w.code} has no hints"
    
    def test_similar_warnings_consistent_format(self) -> None:
        """Similar warnings (unused var/param) should have consistent format."""
        program = make_program([
            make_fn("f", [Parameter("param", T("Int"))], [
                LetStmt("var", IntLiteral(42))
            ])
        ])
        checker = check_program(program)
        
        unused_param = get_warnings_by_code(checker, WarningCode.UNUSED_PARAMETER)
        unused_var = get_warnings_by_code(checker, WarningCode.UNUSED_VARIABLE)
        
        assert len(unused_param) == 1
        assert len(unused_var) == 1
        
        # Both should mention "unused" and use backticks
        assert "unused" in unused_param[0].message.lower()
        assert "unused" in unused_var[0].message.lower()
        assert "`param`" in unused_param[0].message
        assert "`var`" in unused_var[0].message
        
        # Both hints should suggest underscore prefix
        assert "_" in unused_param[0].hints[0]
        assert "_" in unused_var[0].hints[0]


# =============================================================================
# 5. Edge Cases and Regression Tests
# =============================================================================

class TestEdgeCases:
    """Test edge cases for semantic consistency."""
    
    def test_empty_function_void_ok(self) -> None:
        """Empty function with void return is valid."""
        program = make_program([
            make_fn("f", [], [])
        ])
        checker = check_program(program)
        assert len(checker.errors) == 0
    
    def test_if_as_implicit_return(self) -> None:
        """If/else as implicit return should work."""
        program = make_program([
            make_fn("f", [Parameter("x", T("Bool"))], [
                IfStmt(
                    Identifier("x"),
                    [ExprStmt(IntLiteral(1))],
                    [ExprStmt(IntLiteral(2))]
                )
            ], T("Int"))
        ])
        checker = check_program(program)
        assert len(checker.errors) == 0
    
    def test_nested_if_type_consistency(self) -> None:
        """Nested if/else should have consistent types in all branches."""
        program = make_program([
            make_fn("f", [Parameter("x", T("Bool")), Parameter("y", T("Bool"))], [
                IfStmt(
                    Identifier("x"),
                    [IfStmt(
                        Identifier("y"),
                        [ExprStmt(IntLiteral(1))],
                        [ExprStmt(IntLiteral(2))]
                    )],
                    [ExprStmt(IntLiteral(3))]
                )
            ], T("Int"))
        ])
        checker = check_program(program)
        assert len(checker.errors) == 0
