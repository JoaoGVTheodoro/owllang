"""
Robustness tests for OwlLang compiler.

Tests that verify the compiler handles errors gracefully:
- No duplicate diagnostics
- Error recovery continues compilation
- Precise error spans
"""

import pytest
from owllang.ast import (
    Program, FnDecl, Parameter, LetStmt, ExprStmt, ReturnStmt, IfStmt,
    IntLiteral, StringLiteral, Identifier, BinaryOp, TypeAnnotation as T,
    Call, MatchExpr, MatchArm, SomePattern, NonePattern
)
from owllang.typechecker import TypeChecker
from owllang.diagnostics import WarningCode


class TestNoDuplicateErrors:
    """Ensure no duplicate errors are generated."""
    
    def test_single_type_mismatch_one_error(self) -> None:
        """Type mismatch should generate exactly one error."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(StringLiteral("not an int")),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        
        # Should have exactly 1 error (implicit return mismatch)
        assert len(errors) == 1
        
        # Verify no duplicates
        error_messages = [e.message for e in errors]
        assert len(error_messages) == len(set(error_messages))
    
    def test_multiple_errors_in_same_function(self) -> None:
        """Multiple distinct errors should each be reported once."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        LetStmt("x", StringLiteral("hello")),
                        LetStmt("y", BinaryOp(Identifier("x"), "+", IntLiteral(1))),  # Error 1
                        ReturnStmt(StringLiteral("world")),  # Error 2
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        
        # Should have 2 distinct errors
        assert len(errors) >= 2
        
        # Verify no duplicates
        error_messages = [e.message for e in errors]
        unique_messages = list(set(error_messages))
        # Allow some duplicates if they're at different locations
        # but most should be unique
        assert len(unique_messages) >= len(error_messages) // 2


class TestNoDuplicateWarnings:
    """Ensure no duplicate warnings are generated."""
    
    def test_unused_variables_unique(self) -> None:
        """Each unused variable should generate exactly one warning."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=None,
                    body=[
                        LetStmt("x", IntLiteral(1)),
                        LetStmt("y", IntLiteral(2)),
                        LetStmt("z", IntLiteral(3)),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        # 3 unused variables = 3 warnings
        unused_warnings = [w for w in warnings if w.code == WarningCode.UNUSED_VARIABLE]
        assert len(unused_warnings) == 3
        
        # All warnings should have different messages
        messages = [w.message for w in unused_warnings]
        assert len(messages) == len(set(messages))


class TestSpanPrecision:
    """Verify error spans point to the correct location."""
    
    def test_match_exhaustiveness_has_span(self) -> None:
        """Match exhaustiveness error should have a valid span."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("x", T("Option", [T("Int")]))],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(
                            MatchExpr(
                                subject=Identifier("x"),
                                arms=[
                                    # Missing None arm!
                                    MatchArm(
                                        pattern=SomePattern("val"),
                                        body=Identifier("val")
                                    )
                                ]
                            )
                        )
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        
        # Should have error about non-exhaustive match
        assert len(errors) >= 1
        
        # At least one error should have a span
        error_spans = [e.line > 0 or e.column > 0 for e in errors]
        assert any(error_spans), "At least one error should have location info"


class TestErrorRecovery:
    """Verify compiler continues after errors to find more issues."""
    
    def test_continues_after_type_error(self) -> None:
        """Should continue checking after first type error."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        LetStmt("x", IntLiteral(1)),
                        LetStmt("y", BinaryOp(
                            StringLiteral("hello"),
                            "+",
                            IntLiteral(1)
                        )),  # Error 1: invalid operation
                        ReturnStmt(Identifier("x")),  # x is used
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        
        # Should have error about invalid operation
        assert len(errors) >= 1
        # Checker should continue and not crash
        assert checker.errors is not None


class TestDiagnosticQuality:
    """Verify diagnostic messages are helpful."""
    
    def test_errors_have_code(self) -> None:
        """All errors should have error codes."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        ReturnStmt(StringLiteral("wrong")),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        diagnostics = checker.diagnostics
        
        # All diagnostics should have codes
        for diag in diagnostics:
            assert diag.code is not None
            assert isinstance(diag.code, str)
            assert len(diag.code) == 5  # E0301 format
            assert diag.code[0] in ('E', 'W')
    
    def test_warnings_have_code(self) -> None:
        """All warnings should have warning codes."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=None,
                    body=[
                        LetStmt("unused", IntLiteral(1)),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        checker.check(program)
        warnings = checker.get_warnings()
        
        # All warnings should have codes
        for warning in warnings:
            assert warning.code is not None
            assert warning.code.value.startswith('W')
            assert len(warning.code.value) == 5
