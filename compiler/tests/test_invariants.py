"""
Invariant tests for OwlLang compiler.

These tests verify fundamental properties that must always hold:
1. All diagnostics have valid codes
2. No duplicate diagnostics at the same location
3. Warnings are deterministic
4. Error/warning separation is consistent
"""

import pytest
from owllang.ast import (
    Program, FnDecl, Parameter, LetStmt, ExprStmt, ReturnStmt,
    IntLiteral, StringLiteral, Identifier, BinaryOp, TypeAnnotation as T
)
from owllang.typechecker import TypeChecker
from owllang.diagnostics import ErrorCode, WarningCode


class TestDiagnosticCodeInvariants:
    """All diagnostics must have valid codes."""
    
    def test_error_codes_are_valid_format(self) -> None:
        """Error codes must match Exxxx format."""
        for code in ErrorCode:
            assert code.value.startswith("E"), f"Error code {code} must start with 'E'"
            assert len(code.value) == 5, f"Error code {code} must be 5 chars (Exxxx)"
            assert code.value[1:].isdigit(), f"Error code {code} must have 4 digits"
    
    def test_warning_codes_are_valid_format(self) -> None:
        """Warning codes must match Wxxxx format."""
        for code in WarningCode:
            assert code.value.startswith("W"), f"Warning code {code} must start with 'W'"
            assert len(code.value) == 5, f"Warning code {code} must be 5 chars (Wxxxx)"
            assert code.value[1:].isdigit(), f"Warning code {code} must have 4 digits"
    
    def test_error_codes_are_unique(self) -> None:
        """All error codes must be unique."""
        values = [code.value for code in ErrorCode]
        assert len(values) == len(set(values)), "Duplicate error codes found"
    
    def test_warning_codes_are_unique(self) -> None:
        """All warning codes must be unique."""
        values = [code.value for code in WarningCode]
        assert len(values) == len(set(values)), "Duplicate warning codes found"
    
    def test_no_overlap_between_error_and_warning_codes(self) -> None:
        """Error and warning codes must not overlap."""
        error_values = {code.value for code in ErrorCode}
        warning_values = {code.value for code in WarningCode}
        overlap = error_values & warning_values
        assert len(overlap) == 0, f"Overlapping codes: {overlap}"


class TestNoDuplicateDiagnostics:
    """No duplicate diagnostics should be generated."""
    
    def test_single_error_per_issue(self) -> None:
        """Each type error should generate exactly one error."""
        # Type mismatch should generate one error
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
        
        # Count errors by message to find duplicates
        error_messages = [str(e) for e in errors]
        for msg in set(error_messages):
            count = error_messages.count(msg)
            assert count == 1, f"Duplicate error: '{msg}' appeared {count} times"
    
    def test_single_warning_per_issue(self) -> None:
        """Each warning condition should generate exactly one warning."""
        # Unused variable should generate one warning
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
        
        # Count warnings by message
        warning_messages = [str(w) for w in warnings]
        for msg in set(warning_messages):
            count = warning_messages.count(msg)
            assert count == 1, f"Duplicate warning: '{msg}' appeared {count} times"


class TestWarningDeterminism:
    """Warnings must be deterministic."""
    
    def test_same_input_same_warnings(self) -> None:
        """Running the checker twice should produce identical warnings."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("a", T("Int")), Parameter("b", T("Int"))],
                    return_type=None,
                    body=[
                        LetStmt("x", IntLiteral(1)),
                        LetStmt("y", IntLiteral(2)),
                    ]
                )
            ],
            statements=[]
        )
        
        # Run checker multiple times
        results = []
        for _ in range(3):
            checker = TypeChecker()
            checker.check(program)
            warnings = checker.get_warnings()
            results.append([str(w) for w in warnings])
        
        # All results should be identical
        assert results[0] == results[1] == results[2], "Warnings are not deterministic"
    
    def test_warning_order_is_consistent(self) -> None:
        """Warning order should be consistent across runs."""
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[
                        ReturnStmt(IntLiteral(1)),
                        LetStmt("dead1", IntLiteral(2)),
                        LetStmt("dead2", IntLiteral(3)),
                    ]
                )
            ],
            statements=[]
        )
        
        # Run checker multiple times
        orders = []
        for _ in range(3):
            checker = TypeChecker()
            checker.check(program)
            warnings = checker.get_warnings()
            orders.append([w.code.value for w in warnings])
        
        assert orders[0] == orders[1] == orders[2], "Warning order is not consistent"


class TestErrorWarningSeparation:
    """Errors and warnings must be properly separated."""
    
    def test_errors_block_but_warnings_do_not(self) -> None:
        """Errors should cause non-zero exit, warnings should not."""
        # Program with only warnings
        warning_program = Program(
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
        errors = checker.check(warning_program)
        warnings = checker.get_warnings()
        
        assert len(errors) == 0, "Should have no errors"
        assert len(warnings) > 0, "Should have warnings"
    
    def test_errors_and_warnings_are_independent(self) -> None:
        """Both errors and warnings can coexist."""
        # Program with both error and warning
        program = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[Parameter("unused", T("Int"))],
                    return_type=T("Int"),
                    body=[
                        ExprStmt(StringLiteral("wrong type")),
                    ]
                )
            ],
            statements=[]
        )
        checker = TypeChecker()
        errors = checker.check(program)
        warnings = checker.get_warnings()
        
        # Should have both
        assert len(errors) > 0, "Should have errors"
        assert len(warnings) > 0, "Should have warnings"


class TestCheckerStateInvariants:
    """TypeChecker state invariants."""
    
    def test_checker_resets_between_runs(self) -> None:
        """Checker should reset state between runs."""
        checker = TypeChecker()
        
        # First run with error
        program1 = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=T("Int"),
                    body=[ExprStmt(StringLiteral("wrong"))],
                )
            ],
            statements=[]
        )
        errors1 = checker.check(program1)
        assert len(errors1) > 0
        
        # Second run with no errors
        program2 = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="g",
                    params=[],
                    return_type=T("Int"),
                    body=[ExprStmt(IntLiteral(42))],
                )
            ],
            statements=[]
        )
        errors2 = checker.check(program2)
        
        # Second run should not carry over errors from first run
        assert len(errors2) == 0, "Errors from previous run leaked"
    
    def test_warnings_reset_between_runs(self) -> None:
        """Warnings should reset between runs."""
        checker = TypeChecker()
        
        # First run with warnings
        program1 = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="f",
                    params=[],
                    return_type=None,
                    body=[LetStmt("unused", IntLiteral(1))],
                )
            ],
            statements=[]
        )
        checker.check(program1)
        warnings1 = checker.get_warnings()
        assert len(warnings1) > 0
        
        # Second run with no warnings
        program2 = Program(
            imports=[],
            functions=[
                FnDecl(
                    name="g",
                    params=[],
                    return_type=None,
                    body=[],
                )
            ],
            statements=[]
        )
        checker.check(program2)
        warnings2 = checker.get_warnings()
        
        # Second run should not carry over warnings
        assert len(warnings2) == 0, "Warnings from previous run leaked"
