"""
Tests for the warning system in OwlLang.
"""

import pytest
from owllang.ast import (
    Program, FnDecl, Parameter, LetStmt, ExprStmt, ReturnStmt,
    IntLiteral, Identifier, BinaryOp, TypeAnnotation as T, Call, IfStmt
)
from owllang.typechecker import TypeChecker
from owllang.diagnostics import WarningCode


class TestUnusedVariables:
    """Tests for unused variable warnings."""
    
    def test_unused_local_variable(self) -> None:
        """Unused local variable should trigger warning."""
        # fn f() {
        #     let x = 1
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=None,
                    body=[
                        LetStmt("x", IntLiteral(1)),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 1
        assert warnings[0].code == WarningCode.UNUSED_VARIABLE
        assert "x" in warnings[0].message
    
    def test_used_local_variable(self) -> None:
        """Used local variable should not trigger warning."""
        # fn f() {
        #     let x = 1
        #     print(x)
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=None,
                    body=[
                        LetStmt("x", IntLiteral(1)),
                        ExprStmt(Call(Identifier("print"), [Identifier("x")])),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 0
    
    def test_underscore_prefix_suppresses_warning(self) -> None:
        """Variables prefixed with underscore should not trigger warning."""
        # fn f() {
        #     let _unused = 1
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=None,
                    body=[
                        LetStmt("_unused", IntLiteral(1)),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 0


class TestUnusedParameters:
    """Tests for unused parameter warnings."""
    
    def test_unused_parameter(self) -> None:
        """Unused parameter should trigger warning."""
        # fn f(x: Int) {
        #     print(1)
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("x", T("Int"))],
                    return_type=None,
                    body=[
                        ExprStmt(Call(Identifier("print"), [IntLiteral(1)])),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 1
        assert warnings[0].code == WarningCode.UNUSED_PARAMETER
        assert "x" in warnings[0].message
        assert "f" in warnings[0].message  # Function name in message
    
    def test_used_parameter(self) -> None:
        """Used parameter should not trigger warning."""
        # fn f(x: Int) {
        #     print(x)
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("x", T("Int"))],
                    return_type=None,
                    body=[
                        ExprStmt(Call(Identifier("print"), [Identifier("x")])),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 0
    
    def test_underscore_prefix_suppresses_parameter_warning(self) -> None:
        """Parameters prefixed with underscore should not trigger warning."""
        # fn f(_x: Int) {
        #     print(1)
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("_x", T("Int"))],
                    return_type=None,
                    body=[
                        ExprStmt(Call(Identifier("print"), [IntLiteral(1)])),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 0
    
    def test_multiple_unused_parameters(self) -> None:
        """Multiple unused parameters should trigger multiple warnings."""
        # fn f(a: Int, b: Int) {
        #     print(1)
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[
                        Parameter("a", T("Int")),
                        Parameter("b", T("Int")),
                    ],
                    return_type=None,
                    body=[
                        ExprStmt(Call(Identifier("print"), [IntLiteral(1)])),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 2
        assert all(w.code == WarningCode.UNUSED_PARAMETER for w in warnings)


class TestWarningIntegration:
    """Integration tests for warnings with errors."""
    
    def test_warnings_do_not_affect_errors(self) -> None:
        """Warnings should not prevent error detection."""
        # fn f(unused: Int) -> Int {
        #     "not an int"  // Type error + unused param warning
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("unused", T("Int"))],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(Identifier("wrong_type_literal")),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        warnings = checker.get_warnings()
        
        # Should have both errors and warnings
        assert len(errors) > 0 or len(checker.diagnostics) > 0
        assert len(warnings) == 1  # unused parameter
    
    def test_variable_used_in_expression(self) -> None:
        """Variable used in expression should be marked as used."""
        # fn f() -> Int {
        #     let x = 1
        #     let y = 2
        #     x + y
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        LetStmt("x", IntLiteral(1)),
                        LetStmt("y", IntLiteral(2)),
                        ExprStmt(BinaryOp(
                            Identifier("x"),
                            "+",
                            Identifier("y")
                        )),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 0
    
    def test_variable_used_in_if_condition(self) -> None:
        """Variable used in if condition should be marked as used."""
        # fn f(x: Bool) {
        #     if x { print(1) }
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("x", T("Bool"))],
                    return_type=None,
                    body=[
                        ExprStmt(IfStmt(
                            condition=Identifier("x"),
                            then_body=[
                                ExprStmt(Call(Identifier("print"), [IntLiteral(1)]))
                            ],
                            else_body=None,
                        )),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) == 0


class TestDeadCode:
    """Tests for dead/unreachable code warnings."""
    
    def test_code_after_return(self) -> None:
        """Code after return should trigger warning."""
        # fn f() -> Int {
        #     return 1
        #     let x = 2  // unreachable!
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        ReturnStmt(IntLiteral(1)),
                        LetStmt("x", IntLiteral(2)),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        assert len(warnings) >= 1
        assert any(w.code == WarningCode.UNREACHABLE_CODE for w in warnings)
    
    def test_multiple_statements_after_return(self) -> None:
        """Multiple statements after return should trigger multiple warnings."""
        # fn f() -> Int {
        #     return 1
        #     let x = 2  // unreachable!
        #     let y = 3  // unreachable!
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        ReturnStmt(IntLiteral(1)),
                        LetStmt("x", IntLiteral(2)),
                        LetStmt("y", IntLiteral(3)),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        unreachable_warnings = [w for w in warnings if w.code == WarningCode.UNREACHABLE_CODE]
        assert len(unreachable_warnings) == 2
    
    def test_code_before_return_is_ok(self) -> None:
        """Code before return should not trigger warning."""
        # fn f() -> Int {
        #     let x = 1
        #     return x
        # }
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        LetStmt("x", IntLiteral(1)),
                        ReturnStmt(Identifier("x")),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        unreachable_warnings = [w for w in warnings if w.code == WarningCode.UNREACHABLE_CODE]
        assert len(unreachable_warnings) == 0
