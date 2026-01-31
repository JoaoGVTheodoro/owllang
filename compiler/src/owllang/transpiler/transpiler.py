"""
OwlLang Transpiler

Converts OwlLang AST to Python source code.
"""

from __future__ import annotations

from ..ast import (
    # Expressions
    Expr, IntLiteral, FloatLiteral, StringLiteral, BoolLiteral,
    Identifier, BinaryOp, UnaryOp, Call, FieldAccess, TryExpr,
    # Statements
    Stmt, LetStmt, ExprStmt, ReturnStmt, IfStmt,
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
        elif isinstance(stmt, ExprStmt):
            return self._expr_has_result(stmt.expr)
        elif isinstance(stmt, ReturnStmt):
            return stmt.value is not None and self._expr_has_result(stmt.value)
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
        """Transpile function declaration."""
        # Function signature
        params = ", ".join(p.name for p in fn.params)
        lines: list[str] = [f"def {fn.name}({params}):"]
        
        # Function body
        self.indent_level += 1
        
        if not fn.body:
            lines.append(self._indent("pass"))
        else:
            for stmt in fn.body:
                lines.append(self._transpile_stmt(stmt))
        
        self.indent_level -= 1
        
        return "\n".join(lines)
    
    # =========================================================================
    # Statement Transpilation
    # =========================================================================
    
    def _transpile_stmt(self, stmt: Stmt) -> str:
        """Transpile a statement."""
        if isinstance(stmt, LetStmt):
            return self._transpile_let(stmt)
        elif isinstance(stmt, ExprStmt):
            return self._transpile_expr_stmt(stmt)
        elif isinstance(stmt, ReturnStmt):
            return self._transpile_return(stmt)
        elif isinstance(stmt, IfStmt):
            return self._transpile_if(stmt)
        else:
            raise ValueError(f"Unknown statement type: {type(stmt)}")
    
    def _transpile_let(self, stmt: LetStmt) -> str:
        """Transpile: let x = value → x = value
        
        Special handling for try expressions (?) to enable early return.
        """
        # Check if value contains TryExpr and handle specially
        if isinstance(stmt.value, TryExpr):
            return self._transpile_let_with_try(stmt.name, stmt.value)
        
        value = self._transpile_expr(stmt.value)
        return self._indent(f"{stmt.name} = {value}")
    
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
        
        else:
            raise ValueError(f"Unknown expression type: {type(expr)}")
    
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
