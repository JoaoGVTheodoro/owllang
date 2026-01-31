"""
OwlLang Type Checker

Performs static type checking on the AST before transpilation.
Detects type errors like invalid operations, type mismatches, and undefined variables.

Phase 1: Int, Float, String, Bool, Void, Any
Phase 2: Option[T], Result[T, E], if-expr, implicit return
DX Phase 1: Rich diagnostics with spans
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..ast import (
    # Expressions
    Expr, IntLiteral, FloatLiteral, StringLiteral, BoolLiteral,
    Identifier, BinaryOp, UnaryOp, Call, FieldAccess, TryExpr,
    # Type Annotations
    TypeAnnotation,
    # Statements
    Stmt, LetStmt, ExprStmt, ReturnStmt, IfStmt,
    # Declarations
    Parameter, FnDecl, PythonImport, PythonFromImport, Program
)

from .types import (
    OwlType, INT, FLOAT, STRING, BOOL, VOID, UNKNOWN, ANY,
    OptionType, ResultType,
    parse_type, types_compatible,
)

from ..diagnostics import (
    DiagnosticError, Span, DUMMY_SPAN,
    type_mismatch_error, undefined_variable_error, undefined_function_error,
    return_type_mismatch_error, invalid_operation_error, incompatible_comparison_error,
    branch_type_mismatch_error, condition_not_bool_error, wrong_arg_count_error,
    cannot_negate_error, wrong_type_arity_error, unknown_type_error,
    try_not_result_error, try_outside_result_fn_error, try_error_type_mismatch_error,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Type Errors (Legacy - kept for backward compatibility)
# =============================================================================

@dataclass
class TypeError:
    """Represents a type error found during checking."""
    message: str
    line: int
    column: int
    
    def __str__(self) -> str:
        return f"[{self.line}:{self.column}] {self.message}"
    
    @classmethod
    def from_diagnostic(cls, diag: DiagnosticError) -> TypeError:
        """Create a TypeError from a DiagnosticError."""
        return cls(
            message=diag.message,
            line=diag.span.start.line,
            column=diag.span.start.column
        )


# =============================================================================
# Type Environment
# =============================================================================

class TypeEnv:
    """
    Type environment that tracks variable and function types.
    Supports nested scopes.
    """
    
    def __init__(self, parent: TypeEnv | None = None) -> None:
        self.parent = parent
        self.variables: dict[str, OwlType] = {}
        self.functions: dict[str, tuple[list[OwlType], OwlType]] = {}
    
    def define_var(self, name: str, typ: OwlType) -> None:
        """Define a variable in current scope."""
        self.variables[name] = typ
    
    def lookup_var(self, name: str) -> OwlType | None:
        """Look up a variable, searching parent scopes."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.lookup_var(name)
        return None
    
    def define_fn(self, name: str, param_types: list[OwlType], return_type: OwlType) -> None:
        """Define a function in current scope."""
        self.functions[name] = (param_types, return_type)
    
    def lookup_fn(self, name: str) -> tuple[list[OwlType], OwlType] | None:
        """Look up a function, searching parent scopes."""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.lookup_fn(name)
        return None
    
    def child_scope(self) -> TypeEnv:
        """Create a child scope."""
        return TypeEnv(parent=self)


# =============================================================================
# Type Checker
# =============================================================================

class TypeChecker:
    """
    Type checker for OwlLang.
    
    Validates types in the AST and collects errors.
    Does not modify the AST.
    """
    
    def __init__(self, filename: str = "<unknown>") -> None:
        self.errors: list[TypeError] = []
        self.diagnostics: list[DiagnosticError] = []
        self.env = TypeEnv()
        self.current_function_return_type: OwlType | None = None
        self.filename = filename
        
        # Built-in functions
        self._register_builtins()
    
    def _register_builtins(self) -> None:
        """Register built-in functions."""
        # print accepts any type
        self.env.define_fn("print", [ANY], VOID)
    
    def check(self, program: Program) -> list[TypeError]:
        """
        Check the entire program for type errors.
        Returns list of errors found.
        """
        self.errors = []
        self.diagnostics = []
        
        # First pass: collect function signatures
        for fn in program.functions:
            self._register_function(fn)
        
        # Register imported modules as ANY type
        for imp in program.imports:
            if isinstance(imp, PythonImport):
                name = imp.alias if imp.alias else imp.module
                self.env.define_var(name, ANY)
            elif isinstance(imp, PythonFromImport):
                for name, alias in imp.names:
                    var_name = alias if alias else name
                    self.env.define_var(var_name, ANY)
        
        # Second pass: check function bodies
        for fn in program.functions:
            self._check_function(fn)
        
        # Check top-level statements
        for stmt in program.statements:
            self._check_stmt(stmt)
        
        return self.errors
    
    def _register_function(self, fn: FnDecl) -> None:
        """Register a function's signature in the environment."""
        # For now, all params are ANY since we don't have type annotations yet
        param_types = [ANY] * len(fn.params)
        
        # Return type defaults to VOID
        return_type = VOID
        if fn.return_type:
            return_type = self._parse_type(fn.return_type)
        
        self.env.define_fn(fn.name, param_types, return_type)
    
    def _parse_type(self, type_ann: TypeAnnotation) -> OwlType:
        """
        Convert a TypeAnnotation AST node into an OwlType.
        
        Validates arity for parameterized types:
        - Option requires exactly 1 type parameter
        - Result requires exactly 2 type parameters
        """
        name = type_ann.name
        params = type_ann.params
        
        # Primitive types (no parameters allowed)
        primitives = {
            "Int": INT, "int": INT,
            "Float": FLOAT, "float": FLOAT,
            "String": STRING, "str": STRING,
            "Bool": BOOL, "bool": BOOL,
            "Void": VOID, "void": VOID,
            "Any": ANY,
        }
        
        if name in primitives:
            if params:
                span = type_ann.span if type_ann.span else DUMMY_SPAN
                self._add_diagnostic(wrong_type_arity_error(name, 0, len(params), span))
                return UNKNOWN
            return primitives[name]
        
        # Option[T] - requires exactly 1 parameter
        if name == "Option":
            if len(params) != 1:
                span = type_ann.span if type_ann.span else DUMMY_SPAN
                self._add_diagnostic(wrong_type_arity_error("Option", 1, len(params), span))
                return UNKNOWN
            inner_type = self._parse_type(params[0])
            return OptionType(inner_type)
        
        # Result[T, E] - requires exactly 2 parameters
        if name == "Result":
            if len(params) != 2:
                span = type_ann.span if type_ann.span else DUMMY_SPAN
                self._add_diagnostic(wrong_type_arity_error("Result", 2, len(params), span))
                return UNKNOWN
            ok_type = self._parse_type(params[0])
            err_type = self._parse_type(params[1])
            return ResultType(ok_type, err_type)
        
        # Unknown type
        span = type_ann.span if type_ann.span else DUMMY_SPAN
        self._add_diagnostic(unknown_type_error(name, span))
        return UNKNOWN
    
    def _check_function(self, fn: FnDecl) -> None:
        """Check a function declaration."""
        # Create new scope for function body
        fn_env = self.env.child_scope()
        old_env = self.env
        self.env = fn_env
        
        # Add parameters to scope
        for param in fn.params:
            param_type = ANY
            if param.type_annotation:
                param_type = self._parse_type(param.type_annotation)
            self.env.define_var(param.name, param_type)
        
        # Set expected return type
        fn_info = old_env.lookup_fn(fn.name)
        if fn_info:
            self.current_function_return_type = fn_info[1]
        
        # Check body statements
        last_stmt_type: OwlType = VOID
        for i, stmt in enumerate(fn.body):
            if isinstance(stmt, ExprStmt):
                # Track the type of the last expression (for implicit return)
                last_stmt_type = self._check_expr(stmt.expr)
            else:
                self._check_stmt(stmt)
                last_stmt_type = VOID
        
        # Check implicit return (last expression as return value)
        if (self.current_function_return_type and 
            self.current_function_return_type != VOID and
            fn.body and 
            isinstance(fn.body[-1], ExprStmt)):
            # Last statement is an expression - check if it matches return type
            if not types_compatible(self.current_function_return_type, last_stmt_type):
                self._error(
                    f"Implicit return type mismatch: expected {self.current_function_return_type}, got {last_stmt_type}",
                    1, 1
                )
        
        # Restore scope
        self.env = old_env
        self.current_function_return_type = None
    
    def _check_stmt(self, stmt: Stmt) -> None:
        """Check a statement for type errors."""
        if isinstance(stmt, LetStmt):
            self._check_let(stmt)
        elif isinstance(stmt, ExprStmt):
            self._check_expr(stmt.expr)
        elif isinstance(stmt, ReturnStmt):
            self._check_return(stmt)
        elif isinstance(stmt, IfStmt):
            self._check_if(stmt)
    
    def _check_let(self, stmt: LetStmt) -> None:
        """Check let statement."""
        value_type = self._check_expr(stmt.value)
        
        # If there's a type annotation, verify it matches
        if stmt.type_annotation:
            expected_type = self._parse_type(stmt.type_annotation)
            if not types_compatible(expected_type, value_type):
                self._error(
                    f"Type mismatch: expected {expected_type}, got {value_type}",
                    1, 1  # TODO: track actual line/column in AST
                )
            # Use the annotated type for the variable
            self.env.define_var(stmt.name, expected_type)
        else:
            # Define variable with inferred type
            self.env.define_var(stmt.name, value_type)
    
    def _check_return(self, stmt: ReturnStmt) -> None:
        """Check return statement."""
        if stmt.value:
            return_type = self._check_expr(stmt.value)
            
            if self.current_function_return_type and self.current_function_return_type != VOID:
                if not types_compatible(self.current_function_return_type, return_type):
                    self._error(
                        f"Return type mismatch: expected {self.current_function_return_type}, got {return_type}",
                        1, 1
                    )
    
    def _check_if(self, stmt: IfStmt) -> None:
        """Check if statement."""
        cond_type = self._check_expr(stmt.condition)
        
        # Condition should be Bool (or compatible)
        if cond_type not in (BOOL, ANY, UNKNOWN):
            self._error(
                f"Condition must be Bool, got {cond_type}",
                1, 1
            )
        
        # Check then branch
        for s in stmt.then_body:
            self._check_stmt(s)
        
        # Check else branch
        if stmt.else_body:
            for s in stmt.else_body:
                self._check_stmt(s)
    
    def _check_if_expr(self, stmt: IfStmt) -> OwlType:
        """
        Check if/else as an expression and return its type.
        Both branches must have compatible types.
        If no else, returns Void.
        """
        cond_type = self._check_expr(stmt.condition)
        
        # Condition should be Bool
        if cond_type not in (BOOL, ANY, UNKNOWN):
            self._error(
                f"Condition must be Bool, got {cond_type}",
                1, 1
            )
        
        # Get type of last expression in then branch
        then_type = VOID
        if stmt.then_body:
            last_then = stmt.then_body[-1]
            if isinstance(last_then, ExprStmt):
                then_type = self._check_expr(last_then.expr)
            else:
                self._check_stmt(last_then)
                then_type = VOID
            # Check other statements in then branch
            for s in stmt.then_body[:-1]:
                self._check_stmt(s)
        
        # If no else branch, type is Void
        if not stmt.else_body:
            return VOID
        
        # Get type of last expression in else branch
        else_type = VOID
        if stmt.else_body:
            last_else = stmt.else_body[-1]
            if isinstance(last_else, ExprStmt):
                else_type = self._check_expr(last_else.expr)
            else:
                self._check_stmt(last_else)
                else_type = VOID
            # Check other statements in else branch
            for s in stmt.else_body[:-1]:
                self._check_stmt(s)
        
        # Both branches must have compatible types
        if not types_compatible(then_type, else_type):
            self._error(
                f"Incompatible branch types: then has {then_type}, else has {else_type}",
                1, 1
            )
        
        # Return the more specific type
        if then_type == ANY:
            return else_type
        return then_type
    
    def _check_expr(self, expr: Expr) -> OwlType:
        """Check an expression and return its type."""
        if isinstance(expr, IntLiteral):
            return INT
        
        elif isinstance(expr, FloatLiteral):
            return FLOAT
        
        elif isinstance(expr, StringLiteral):
            return STRING
        
        elif isinstance(expr, BoolLiteral):
            return BOOL
        
        elif isinstance(expr, Identifier):
            # Special case: None is Option[Any]
            if expr.name == "None":
                return OptionType(ANY)
            
            typ = self.env.lookup_var(expr.name)
            if typ is None:
                self._error(f"Undefined variable: {expr.name}", 1, 1)
                return UNKNOWN
            return typ
        
        elif isinstance(expr, BinaryOp):
            return self._check_binary_op(expr)
        
        elif isinstance(expr, UnaryOp):
            return self._check_unary_op(expr)
        
        elif isinstance(expr, Call):
            return self._check_call(expr)
        
        elif isinstance(expr, FieldAccess):
            # For now, field access on ANY returns ANY
            self._check_expr(expr.object)
            return ANY
        
        elif isinstance(expr, TryExpr):
            return self._check_try_expr(expr)
        
        return UNKNOWN
    
    def _check_binary_op(self, expr: BinaryOp) -> OwlType:
        """Check binary operation and return result type."""
        left_type = self._check_expr(expr.left)
        right_type = self._check_expr(expr.right)
        op = expr.operator
        
        # Handle ANY type (from Python imports)
        if left_type == ANY or right_type == ANY:
            return ANY
        
        # Arithmetic operators: + - * / %
        if op in ('+', '-', '*', '/', '%'):
            # String concatenation
            if op == '+' and left_type == STRING and right_type == STRING:
                return STRING
            
            # Numeric operations
            if left_type in (INT, FLOAT) and right_type in (INT, FLOAT):
                # Float if either operand is Float
                if left_type == FLOAT or right_type == FLOAT:
                    return FLOAT
                return INT
            
            # Type error
            self._error(
                f"Cannot apply '{op}' to {left_type} and {right_type}",
                1, 1
            )
            return UNKNOWN
        
        # Comparison operators: == != < > <= >=
        if op in ('==', '!=', '<', '>', '<=', '>='):
            # Equality works on same types
            if op in ('==', '!='):
                if left_type == right_type:
                    return BOOL
                self._error(
                    f"Cannot compare {left_type} with {right_type}",
                    1, 1
                )
                return BOOL
            
            # Ordering only for numeric types
            if left_type in (INT, FLOAT) and right_type in (INT, FLOAT):
                return BOOL
            
            self._error(
                f"Cannot compare {left_type} with {right_type} using '{op}'",
                1, 1
            )
            return BOOL
        
        return UNKNOWN
    
    def _check_unary_op(self, expr: UnaryOp) -> OwlType:
        """Check unary operation."""
        operand_type = self._check_expr(expr.operand)
        op = expr.operator
        
        if op == '-':
            if operand_type in (INT, FLOAT, ANY):
                return operand_type
            self._error(
                f"Cannot negate {operand_type}",
                1, 1
            )
        
        return operand_type
    
    def _check_call(self, expr: Call) -> OwlType:
        """Check function call."""
        # Get callee type
        if isinstance(expr.callee, Identifier):
            callee_name = expr.callee.name
            
            # Special constructors: Some, Ok, Err
            if callee_name == "Some":
                return self._check_some_call(expr)
            elif callee_name == "Ok":
                return self._check_ok_call(expr)
            elif callee_name == "Err":
                return self._check_err_call(expr)
            
            fn_info = self.env.lookup_fn(callee_name)
            if fn_info:
                param_types, return_type = fn_info
                
                # Check argument count (skip for varargs like print)
                if param_types != [ANY] and len(expr.arguments) != len(param_types):
                    self._error(
                        f"Function {callee_name} expects {len(param_types)} arguments, got {len(expr.arguments)}",
                        1, 1
                    )
                
                # Check argument types
                for arg in expr.arguments:
                    self._check_expr(arg)
                
                return return_type
            
            # Unknown function - might be a Python import
            var_type = self.env.lookup_var(callee_name)
            if var_type == ANY:
                # Calling a Python import
                for arg in expr.arguments:
                    self._check_expr(arg)
                return ANY
            
            self._error(f"Undefined function: {callee_name}", 1, 1)
            return UNKNOWN
        
        elif isinstance(expr.callee, FieldAccess):
            # Method call on object (e.g., math.sqrt)
            self._check_expr(expr.callee)
            for arg in expr.arguments:
                self._check_expr(arg)
            return ANY
        
        # Check arguments anyway
        for arg in expr.arguments:
            self._check_expr(arg)
        
        return UNKNOWN
    
    def _check_some_call(self, expr: Call) -> OwlType:
        """Check Some(x) constructor - returns Option[type(x)]."""
        if len(expr.arguments) != 1:
            self._error(
                f"Some expects exactly 1 argument, got {len(expr.arguments)}",
                1, 1
            )
            return OptionType(ANY)
        
        inner_type = self._check_expr(expr.arguments[0])
        return OptionType(inner_type)
    
    def _check_ok_call(self, expr: Call) -> OwlType:
        """Check Ok(x) constructor - returns Result[type(x), Any]."""
        if len(expr.arguments) != 1:
            self._error(
                f"Ok expects exactly 1 argument, got {len(expr.arguments)}",
                1, 1
            )
            return ResultType(ANY, ANY)
        
        ok_type = self._check_expr(expr.arguments[0])
        return ResultType(ok_type, ANY)
    
    def _check_err_call(self, expr: Call) -> OwlType:
        """Check Err(e) constructor - returns Result[Any, type(e)]."""
        if len(expr.arguments) != 1:
            self._error(
                f"Err expects exactly 1 argument, got {len(expr.arguments)}",
                1, 1
            )
            return ResultType(ANY, ANY)
        
        err_type = self._check_expr(expr.arguments[0])
        return ResultType(ANY, err_type)
    
    def _check_try_expr(self, expr: TryExpr) -> OwlType:
        """
        Check try expression (expr?).
        
        Rules:
        1. The operand must be of type Result[T, E]
        2. The current function must return Result[_, E']
        3. E must be compatible with E'
        4. Returns T (the Ok type)
        """
        operand_type = self._check_expr(expr.operand)
        span = self._get_span(expr)
        
        # Rule 1: operand must be Result[T, E]
        if not isinstance(operand_type, ResultType):
            self._add_diagnostic(try_not_result_error(str(operand_type), span))
            return UNKNOWN
        
        # Rule 2: must be inside a function that returns Result
        if self.current_function_return_type is None:
            self._add_diagnostic(try_outside_result_fn_error(span))
            return operand_type.ok_type
        
        if not isinstance(self.current_function_return_type, ResultType):
            self._add_diagnostic(try_outside_result_fn_error(span))
            return operand_type.ok_type
        
        # Rule 3: error types must be compatible
        fn_err_type = self.current_function_return_type.err_type
        operand_err_type = operand_type.err_type
        
        # ANY is compatible with anything
        if fn_err_type != ANY and operand_err_type != ANY:
            if fn_err_type != operand_err_type:
                self._add_diagnostic(try_error_type_mismatch_error(
                    str(operand_err_type),
                    str(fn_err_type),
                    span
                ))
        
        # Rule 4: return the Ok type
        return operand_type.ok_type
    
    def _get_span(self, node: Expr | Stmt | None) -> Span:
        """Get span from a node, returning DUMMY_SPAN if not available."""
        if node is None:
            return DUMMY_SPAN
        span = getattr(node, 'span', None)
        if span is not None:
            return span
        return Span.single(1, 1, 1, self.filename)
    
    def _error(self, message: str, line: int, column: int) -> None:
        """Record a type error (legacy method for backward compatibility)."""
        self.errors.append(TypeError(message, line, column))
    
    def _add_diagnostic(self, diag: DiagnosticError) -> None:
        """Record a structured diagnostic error."""
        self.diagnostics.append(diag)
        # Also add to legacy errors for backward compatibility
        self.errors.append(TypeError.from_diagnostic(diag))
