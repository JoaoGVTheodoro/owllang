"""
OwlLang Transpiler

Converts OwlLang AST to Python source code.
"""

from __future__ import annotations

from ..ast import (
    # Expressions
    Expr, IntLiteral, FloatLiteral, StringLiteral, BoolLiteral,
    Identifier, BinaryOp, UnaryOp, Call, FieldAccess, TryExpr,
    # Pattern Matching
    MatchExpr, MatchArm, Pattern, SomePattern, NonePattern, OkPattern, ErrPattern,
    # Statements
    Stmt, LetStmt, AssignStmt, ExprStmt, ReturnStmt, WhileStmt, BreakStmt, ContinueStmt, IfStmt,
    # Declarations
    FnDecl, PythonImport, PythonFromImport, Program
)


class Transpiler:
    """
    Transpiles OwlLang AST to Python source code.
    
    Usage:
        transpiler = Transpiler()
        python_code = transpiler.transpile(ast)
    """
    
    def __init__(self) -> None:
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces
        self._try_counter = 0  # Counter for unique try expression variables
    
    def transpile(self, program: Program) -> str:
        """Transpile entire program to Python."""
        lines: list[str] = []
        
        # Check if we need the Result runtime (if any function uses Ok, Err, or ?)
        needs_result_runtime = self._program_uses_result(program)
        if needs_result_runtime:
            lines.extend(self._generate_result_runtime())
            lines.append("")
        
        # Generate imports
        for imp in program.imports:
            lines.append(self._transpile_import(imp))
        
        if program.imports:
            lines.append("")  # Blank line after imports
        
        # Generate functions
        for fn in program.functions:
            lines.append(self._transpile_fn(fn))
            lines.append("")  # Blank line between functions
        
        # Generate top-level statements (script mode)
        for stmt in program.statements:
            lines.append(self._transpile_stmt(stmt))
        
        # Add main guard if there's a main function
        has_main = any(fn.name == "main" for fn in program.functions)
        if has_main:
            lines.append("")
            lines.append('if __name__ == "__main__":')
            lines.append(f"{self.indent_str}main()")
        
        return "\n".join(lines)
    
    def _program_uses_result(self, program: Program) -> bool:
        """Check if the program uses Result types (TryExpr, Ok, or Err)."""
        for fn in program.functions:
            for stmt in fn.body:
                if self._stmt_has_result(stmt):
                    return True
        for stmt in program.statements:
            if self._stmt_has_result(stmt):
                return True
        return False
    
    def _stmt_has_result(self, stmt: Stmt) -> bool:
        """Check if a statement contains Result usage."""
        if isinstance(stmt, LetStmt):
            return self._expr_has_result(stmt.value)
        elif isinstance(stmt, AssignStmt):
            return self._expr_has_result(stmt.value)
        elif isinstance(stmt, ExprStmt):
            return self._expr_has_result(stmt.expr)
        elif isinstance(stmt, ReturnStmt):
            return stmt.value is not None and self._expr_has_result(stmt.value)
        elif isinstance(stmt, WhileStmt):
            if self._expr_has_result(stmt.condition):
                return True
            for s in stmt.body:
                if self._stmt_has_result(s):
                    return True
        elif isinstance(stmt, IfStmt):
            if self._expr_has_result(stmt.condition):
                return True
            for s in stmt.then_body:
                if self._stmt_has_result(s):
                    return True
            if stmt.else_body:
                for s in stmt.else_body:
                    if self._stmt_has_result(s):
                        return True
        return False
    
    def _expr_has_result(self, expr: Expr) -> bool:
        """Check if an expression contains Result usage (TryExpr, Ok, Err)."""
        if isinstance(expr, TryExpr):
            return True
        elif isinstance(expr, Call):
            # Check for Ok(...) or Err(...) calls
            if isinstance(expr.callee, Identifier) and expr.callee.name in ("Ok", "Err"):
                return True
            if self._expr_has_result(expr.callee):
                return True
            for arg in expr.arguments:
                if self._expr_has_result(arg):
                    return True
        elif isinstance(expr, BinaryOp):
            return self._expr_has_result(expr.left) or self._expr_has_result(expr.right)
        elif isinstance(expr, UnaryOp):
            return self._expr_has_result(expr.operand)
        elif isinstance(expr, FieldAccess):
            return self._expr_has_result(expr.object)
        return False
    
    def _generate_result_runtime(self) -> list[str]:
        """Generate the Ok/Err runtime classes for Result type support."""
        return [
            "# Result type runtime",
            "class Ok:",
            "    def __init__(self, value):",
            "        self.value = value",
            "    def __repr__(self):",
            "        return f\"Ok({self.value!r})\"",
            "",
            "class Err:",
            "    def __init__(self, error):",
            "        self.error = error",
            "    def __repr__(self):",
            "        return f\"Err({self.error!r})\"",
        ]
    
    # =========================================================================
    # Import Transpilation
    # =========================================================================
    
    def _transpile_import(self, imp: PythonImport | PythonFromImport) -> str:
        """Transpile import statement."""
        if isinstance(imp, PythonImport):
            # from python import math [as m]
            if imp.alias:
                return f"import {imp.module} as {imp.alias}"
            return f"import {imp.module}"
        
        elif isinstance(imp, PythonFromImport):
            # from python.os.path import join, exists
            names: list[str] = []
            for name, alias in imp.names:
                if alias:
                    names.append(f"{name} as {alias}")
                else:
                    names.append(name)
            return f"from {imp.module} import {', '.join(names)}"
        
        return ""
    
    # =========================================================================
    # Function Transpilation
    # =========================================================================
    
    def _transpile_fn(self, fn: FnDecl) -> str:
        """Transpile function declaration.
        
        Handles implicit return: if the last statement is an expression,
        it is treated as the return value.
        """
        # Function signature
        params = ", ".join(p.name for p in fn.params)
        lines: list[str] = [f"def {fn.name}({params}):"]
        
        # Function body
        self.indent_level += 1
        
        if not fn.body:
            lines.append(self._indent("pass"))
        else:
            # Transpile all statements except the last
            for stmt in fn.body[:-1]:
                lines.append(self._transpile_stmt(stmt))
            
            # Handle last statement specially for implicit return
            last_stmt = fn.body[-1]
            if isinstance(last_stmt, ExprStmt):
                # Last expression becomes implicit return
                expr_code = self._transpile_expr(last_stmt.expr)
                lines.append(self._indent(f"return {expr_code}"))
            elif isinstance(last_stmt, ReturnStmt):
                # Explicit return, transpile normally
                lines.append(self._transpile_stmt(last_stmt))
            elif isinstance(last_stmt, IfStmt):
                # if/else as last statement - treat as expression return
                lines.append(self._transpile_if_as_return(last_stmt))
            else:
                # Other statements (let)
                lines.append(self._transpile_stmt(last_stmt))
        
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _transpile_if_as_return(self, stmt: IfStmt) -> str:
        """Transpile if/else as a returning expression.
        
        Generates:
            if condition:
                return <last expr in then>
            else:
                return <last expr in else>
        """
        lines: list[str] = []
        condition = self._transpile_expr(stmt.condition)
        lines.append(self._indent(f"if {condition}:"))
        
        # Then branch
        self.indent_level += 1
        if stmt.then_body:
            # All but last statement
            for s in stmt.then_body[:-1]:
                lines.append(self._transpile_stmt(s))
            # Last statement becomes return
            last_then = stmt.then_body[-1]
            if isinstance(last_then, ExprStmt):
                expr_code = self._transpile_expr(last_then.expr)
                lines.append(self._indent(f"return {expr_code}"))
            elif isinstance(last_then, IfStmt):
                lines.append(self._transpile_if_as_return(last_then))
            else:
                lines.append(self._transpile_stmt(last_then))
        else:
            lines.append(self._indent("pass"))
        self.indent_level -= 1
        
        # Else branch
        if stmt.else_body:
            lines.append(self._indent("else:"))
            self.indent_level += 1
            # All but last statement
            for s in stmt.else_body[:-1]:
                lines.append(self._transpile_stmt(s))
            # Last statement becomes return
            last_else = stmt.else_body[-1]
            if isinstance(last_else, ExprStmt):
                expr_code = self._transpile_expr(last_else.expr)
                lines.append(self._indent(f"return {expr_code}"))
            elif isinstance(last_else, IfStmt):
                lines.append(self._transpile_if_as_return(last_else))
            else:
                lines.append(self._transpile_stmt(last_else))
            self.indent_level -= 1
        
        return "\n".join(lines)
    
    # =========================================================================
    # Statement Transpilation
    # =========================================================================
    
    def _transpile_stmt(self, stmt: Stmt) -> str:
        """Transpile a statement."""
        if isinstance(stmt, LetStmt):
            return self._transpile_let(stmt)
        elif isinstance(stmt, AssignStmt):
            return self._transpile_assign(stmt)
        elif isinstance(stmt, ExprStmt):
            return self._transpile_expr_stmt(stmt)
        elif isinstance(stmt, ReturnStmt):
            return self._transpile_return(stmt)
        elif isinstance(stmt, WhileStmt):
            return self._transpile_while(stmt)
        elif isinstance(stmt, BreakStmt):
            return self._transpile_break(stmt)
        elif isinstance(stmt, ContinueStmt):
            return self._transpile_continue(stmt)
        elif isinstance(stmt, IfStmt):
            return self._transpile_if(stmt)
        else:
            raise ValueError(f"Unknown statement type: {type(stmt)}")
    
    def _transpile_let(self, stmt: LetStmt) -> str:
        """Transpile: let x = value → x = value
        
        Special handling for try expressions (?) to enable early return.
        Note: 'mut' doesn't affect Python output - mutability is enforced at compile time.
        """
        # Check if value contains TryExpr and handle specially
        if isinstance(stmt.value, TryExpr):
            return self._transpile_let_with_try(stmt.name, stmt.value)
        
        value = self._transpile_expr(stmt.value)
        return self._indent(f"{stmt.name} = {value}")
    
    def _transpile_assign(self, stmt: AssignStmt) -> str:
        """Transpile: x = value → x = value (assignment to mutable variable)."""
        value = self._transpile_expr(stmt.value)
        return self._indent(f"{stmt.name} = {value}")
    
    def _transpile_while(self, stmt: WhileStmt) -> str:
        """Transpile: while condition { body } → while condition: body"""
        lines: list[str] = []
        condition = self._transpile_expr(stmt.condition)
        lines.append(self._indent(f"while {condition}:"))
        
        self.indent_level += 1
        if stmt.body:
            for s in stmt.body:
                lines.append(self._transpile_stmt(s))
        else:
            lines.append(self._indent("pass"))
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _transpile_break(self, stmt: BreakStmt) -> str:
        """Transpile: break → break"""
        return self._indent("break")
    
    def _transpile_continue(self, stmt: ContinueStmt) -> str:
        """Transpile: continue → continue"""
        return self._indent("continue")
    
    def _transpile_let_with_try(self, var_name: str, try_expr: TryExpr) -> str:
        """
        Transpile: let x = expr? 
        
        Generates:
            __try_N = expr
            if isinstance(__try_N, Err):
                return __try_N
            x = __try_N.value
        """
        lines: list[str] = []
        tmp_var = f"__try_{self._try_counter}"
        self._try_counter += 1
        
        operand = self._transpile_expr(try_expr.operand)
        
        lines.append(self._indent(f"{tmp_var} = {operand}"))
        lines.append(self._indent(f"if isinstance({tmp_var}, Err):"))
        self.indent_level += 1
        lines.append(self._indent(f"return {tmp_var}"))
        self.indent_level -= 1
        lines.append(self._indent(f"{var_name} = {tmp_var}.value"))
        
        return "\n".join(lines)
    
    def _transpile_expr_stmt(self, stmt: ExprStmt) -> str:
        """Transpile expression statement."""
        # Handle try expression in statement position
        if isinstance(stmt.expr, TryExpr):
            return self._transpile_try_stmt(stmt.expr)
        return self._indent(self._transpile_expr(stmt.expr))
    
    def _transpile_try_stmt(self, try_expr: TryExpr) -> str:
        """
        Transpile a try expression in statement position (result discarded).
        
        Generates:
            __try_N = expr
            if isinstance(__try_N, Err):
                return __try_N
        """
        lines: list[str] = []
        tmp_var = f"__try_{self._try_counter}"
        self._try_counter += 1
        
        operand = self._transpile_expr(try_expr.operand)
        
        lines.append(self._indent(f"{tmp_var} = {operand}"))
        lines.append(self._indent(f"if isinstance({tmp_var}, Err):"))
        self.indent_level += 1
        lines.append(self._indent(f"return {tmp_var}"))
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    def _transpile_return(self, stmt: ReturnStmt) -> str:
        """Transpile return statement."""
        if stmt.value:
            # Handle try expression in return
            if isinstance(stmt.value, TryExpr):
                return self._transpile_return_with_try(stmt.value)
            value = self._transpile_expr(stmt.value)
            return self._indent(f"return {value}")
        return self._indent("return")
    
    def _transpile_return_with_try(self, try_expr: TryExpr) -> str:
        """
        Transpile: return expr?
        
        Generates:
            __try_N = expr
            if isinstance(__try_N, Err):
                return __try_N
            return __try_N.value
        """
        lines: list[str] = []
        tmp_var = f"__try_{self._try_counter}"
        self._try_counter += 1
        
        operand = self._transpile_expr(try_expr.operand)
        
        lines.append(self._indent(f"{tmp_var} = {operand}"))
        lines.append(self._indent(f"if isinstance({tmp_var}, Err):"))
        self.indent_level += 1
        lines.append(self._indent(f"return {tmp_var}"))
        self.indent_level -= 1
        lines.append(self._indent(f"return {tmp_var}.value"))
        
        return "\n".join(lines)
    
    def _transpile_if(self, stmt: IfStmt) -> str:
        """Transpile if statement."""
        lines: list[str] = []
        
        # If condition
        condition = self._transpile_expr(stmt.condition)
        lines.append(self._indent(f"if {condition}:"))
        
        # Then body
        self.indent_level += 1
        for s in stmt.then_body:
            lines.append(self._transpile_stmt(s))
        self.indent_level -= 1
        
        # Else body
        if stmt.else_body:
            lines.append(self._indent("else:"))
            self.indent_level += 1
            for s in stmt.else_body:
                lines.append(self._transpile_stmt(s))
            self.indent_level -= 1
        
        return "\n".join(lines)
    
    # =========================================================================
    # Expression Transpilation
    # =========================================================================
    
    def _transpile_expr(self, expr: Expr) -> str:
        """Transpile an expression."""
        if isinstance(expr, IntLiteral):
            return str(expr.value)
        
        elif isinstance(expr, FloatLiteral):
            return str(expr.value)
        
        elif isinstance(expr, StringLiteral):
            # Escape special characters and wrap in quotes
            escaped = expr.value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        
        elif isinstance(expr, BoolLiteral):
            return "True" if expr.value else "False"
        
        elif isinstance(expr, Identifier):
            return expr.name
        
        elif isinstance(expr, BinaryOp):
            left = self._transpile_expr(expr.left)
            right = self._transpile_expr(expr.right)
            return f"({left} {expr.operator} {right})"
        
        elif isinstance(expr, UnaryOp):
            operand = self._transpile_expr(expr.operand)
            return f"({expr.operator}{operand})"
        
        elif isinstance(expr, Call):
            callee = self._transpile_expr(expr.callee)
            args = ", ".join(self._transpile_expr(arg) for arg in expr.arguments)
            return f"{callee}({args})"
        
        elif isinstance(expr, FieldAccess):
            obj = self._transpile_expr(expr.object)
            return f"{obj}.{expr.field}"
        
        elif isinstance(expr, TryExpr):
            # For try expressions used within other expressions (e.g., foo()? + bar()),
            # we generate a simple value extraction. The early-return semantics
            # are handled at the statement level for let/return/expr statements.
            # 
            # For nested try expressions in complex expressions, this provides
            # the value extraction, but won't do early return. The type checker
            # ensures this is only used with Result types.
            operand = self._transpile_expr(expr.operand)
            return f"({operand}).value"
        
        elif isinstance(expr, MatchExpr):
            return self._transpile_match_expr(expr)
        
        else:
            raise ValueError(f"Unknown expression type: {type(expr)}")
    
    def _transpile_match_expr(self, expr: MatchExpr) -> str:
        """
        Transpile match expression to Python.
        
        Match expressions are transpiled to a conditional expression or
        a helper function call that evaluates the pattern matching.
        
        For simple cases, we use Python's inline conditional:
        ((lambda __match: v if isinstance(__match, Some) else 0)(subject))
        
        But for readability and correctness, we generate a helper pattern:
        (v if (__match := subject) is not None and hasattr(__match, 'value') else 0)
        
        Actually, we'll use a simpler approach with if/elif in a lambda or
        use walrus operator for inline evaluation.
        """
        subject = self._transpile_expr(expr.subject)
        match_var = f"__match_{self._try_counter}"
        self._try_counter += 1
        
        # Build a conditional expression chain
        # We process arms in order, generating:
        # (body1 if condition1 else (body2 if condition2 else ...))
        
        def build_conditional(arms: list[MatchArm]) -> str:
            if not arms:
                return "None"  # Fallback, shouldn't happen with exhaustive match
            
            arm = arms[0]
            remaining = arms[1:]
            
            condition = self._pattern_condition(arm.pattern, match_var)
            
            # For patterns with bindings, we need to extract the value
            body = self._transpile_arm_body(arm, match_var)
            
            if not remaining:
                # Last arm - no else needed (exhaustive match)
                return body
            else:
                rest = build_conditional(remaining)
                return f"({body} if {condition} else {rest})"
        
        # Generate: (lambda __match_N: conditional)(__subject)
        conditional = build_conditional(expr.arms)
        return f"((lambda {match_var}: {conditional})({subject}))"
    
    def _pattern_condition(self, pattern: Pattern, match_var: str) -> str:
        """Generate condition for a pattern."""
        if isinstance(pattern, SomePattern):
            # Some(x) matches if match_var is not None and has .value
            return f"{match_var} is not None and hasattr({match_var}, 'value')"
        elif isinstance(pattern, NonePattern):
            return f"{match_var} is None"
        elif isinstance(pattern, OkPattern):
            return f"isinstance({match_var}, Ok)"
        elif isinstance(pattern, ErrPattern):
            return f"isinstance({match_var}, Err)"
        else:
            return "True"  # Fallback
    
    def _transpile_arm_body(self, arm: MatchArm, match_var: str) -> str:
        """Transpile arm body, substituting pattern bindings."""
        import re
        pattern = arm.pattern
        body_expr = self._transpile_expr(arm.body)
        
        def replace_identifier(expr: str, old: str, new: str) -> str:
            """Replace identifier only when it's a complete word."""
            # Use word boundaries to only match complete identifiers
            return re.sub(rf'\b{re.escape(old)}\b', new, expr)
        
        # Replace the binding with the appropriate extraction
        if isinstance(pattern, SomePattern):
            # Some(v) => body where v is match_var.value
            binding = pattern.binding
            body_expr = replace_identifier(body_expr, binding, f"{match_var}.value")
        elif isinstance(pattern, OkPattern):
            # Ok(v) => body where v is match_var.value
            binding = pattern.binding
            body_expr = replace_identifier(body_expr, binding, f"{match_var}.value")
        elif isinstance(pattern, ErrPattern):
            # Err(e) => body where e is match_var.error
            binding = pattern.binding
            body_expr = replace_identifier(body_expr, binding, f"{match_var}.error")
        # NonePattern has no binding
        
        return body_expr
    
    # =========================================================================
    # Helpers
    # =========================================================================
    
    def _indent(self, line: str) -> str:
        """Add current indentation to a line."""
        return f"{self.indent_str * self.indent_level}{line}"


def transpile(program: Program) -> str:
    """Convenience function to transpile AST to Python."""
    transpiler = Transpiler()
    return transpiler.transpile(program)
