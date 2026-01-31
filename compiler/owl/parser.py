"""
OwlLang Parser

Converts tokens into an Abstract Syntax Tree (AST).
Uses recursive descent parsing.
"""

from typing import List, Optional, Union
from .ast_nodes import (
    Token, TokenType,
    # Expressions
    Expr, IntLiteral, FloatLiteral, StringLiteral, BoolLiteral,
    Identifier, BinaryOp, UnaryOp, Call, FieldAccess,
    # Statements
    Stmt, LetStmt, ExprStmt, ReturnStmt, IfStmt,
    # Declarations
    Parameter, FnDecl, PythonImport, PythonFromImport, Program
)


class ParseError(Exception):
    """Error during parsing."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at {token.line}:{token.column}: {message}")


class Parser:
    """
    Recursive descent parser for OwlLang.
    
    Grammar (simplified):
        program     → (import | fn_decl | statement)* EOF
        import      → "from" "python" "import" IDENT ("as" IDENT)? 
                    | "from" "python" "." module "import" names
        fn_decl     → "fn" IDENT "(" params? ")" block
        block       → "{" statement* "}"
        statement   → let_stmt | return_stmt | if_stmt | expr_stmt
        let_stmt    → "let" IDENT "=" expr
        return_stmt → "return" expr?
        if_stmt     → "if" expr block ("else" block)?
        expr_stmt   → expr
        
        expr        → comparison
        comparison  → addition (("==" | "!=" | "<" | ">" | "<=" | ">=") addition)*
        addition    → multiplication (("+" | "-") multiplication)*
        multiplication → unary (("*" | "/" | "%") unary)*
        unary       → ("-") unary | call
        call        → primary ("(" arguments? ")" | "." IDENT)*
        primary     → INT | FLOAT | STRING | BOOL | IDENT | "(" expr ")"
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> Program:
        """Parse the entire program."""
        imports: List[Union[PythonImport, PythonFromImport]] = []
        functions: List[FnDecl] = []
        statements: List[Stmt] = []
        
        while not self._is_at_end():
            if self._check(TokenType.FROM):
                imports.append(self._parse_import())
            elif self._check(TokenType.FN):
                functions.append(self._parse_fn_decl())
            else:
                statements.append(self._parse_statement())
        
        return Program(imports, functions, statements)
    
    # =========================================================================
    # Token Helpers
    # =========================================================================
    
    def _is_at_end(self) -> bool:
        """Check if we've consumed all tokens."""
        return self._peek().type == TokenType.EOF
    
    def _peek(self, offset: int = 0) -> Token:
        """Look at current token without consuming."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[pos]
    
    def _advance(self) -> Token:
        """Consume and return current token."""
        token = self.tokens[self.pos]
        if not self._is_at_end():
            self.pos += 1
        return token
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        return self._peek().type == token_type
    
    def _match(self, *token_types: TokenType) -> Optional[Token]:
        """If current token matches any type, consume and return it."""
        for token_type in token_types:
            if self._check(token_type):
                return self._advance()
        return None
    
    def _expect(self, token_type: TokenType, message: str) -> Token:
        """Expect a specific token type, or raise error."""
        if self._check(token_type):
            return self._advance()
        raise ParseError(message, self._peek())
    
    # =========================================================================
    # Import Parsing
    # =========================================================================
    
    def _parse_import(self) -> Union[PythonImport, PythonFromImport]:
        """Parse: from python import math [as m]"""
        self._expect(TokenType.FROM, "Expected 'from'")
        self._expect(TokenType.PYTHON, "Expected 'python'")
        
        # Check for dotted module path: from python.os.path import ...
        module_parts = []
        while self._match(TokenType.DOT):
            name_token = self._expect(TokenType.IDENT, "Expected module name")
            module_parts.append(name_token.value)
        
        self._expect(TokenType.IMPORT, "Expected 'import'")
        
        if module_parts:
            # from python.os.path import join, exists
            names = self._parse_import_names()
            return PythonFromImport('.'.join(module_parts), names)
        else:
            # from python import math [as m]
            module_token = self._expect(TokenType.IDENT, "Expected module name")
            alias = None
            if self._match(TokenType.AS):
                alias_token = self._expect(TokenType.IDENT, "Expected alias name")
                alias = alias_token.value
            return PythonImport(module_token.value, alias)
    
    def _parse_import_names(self) -> List[tuple]:
        """Parse import names: join, exists as e"""
        names = []
        
        while True:
            name_token = self._expect(TokenType.IDENT, "Expected import name")
            alias = None
            if self._match(TokenType.AS):
                alias_token = self._expect(TokenType.IDENT, "Expected alias")
                alias = alias_token.value
            names.append((name_token.value, alias))
            
            if not self._match(TokenType.COMMA):
                break
        
        return names
    
    # =========================================================================
    # Function Parsing
    # =========================================================================
    
    def _parse_fn_decl(self) -> FnDecl:
        """Parse: fn name(params) { body }"""
        self._expect(TokenType.FN, "Expected 'fn'")
        name_token = self._expect(TokenType.IDENT, "Expected function name")
        
        self._expect(TokenType.LPAREN, "Expected '(' after function name")
        params = self._parse_params()
        self._expect(TokenType.RPAREN, "Expected ')' after parameters")
        
        # Optional return type: -> Type
        return_type = None
        if self._match(TokenType.ARROW):
            type_token = self._expect(TokenType.IDENT, "Expected return type")
            return_type = type_token.value
        
        body = self._parse_block()
        
        return FnDecl(name_token.value, params, body, return_type)
    
    def _parse_params(self) -> List[Parameter]:
        """Parse function parameters: a, b, c"""
        params = []
        
        if self._check(TokenType.RPAREN):
            return params  # No parameters
        
        while True:
            name_token = self._expect(TokenType.IDENT, "Expected parameter name")
            
            # Optional type annotation: : Type
            type_annotation = None
            if self._match(TokenType.COLON):
                type_token = self._expect(TokenType.IDENT, "Expected type")
                type_annotation = type_token.value
            
            params.append(Parameter(name_token.value, type_annotation))
            
            if not self._match(TokenType.COMMA):
                break
        
        return params
    
    def _parse_block(self) -> List[Stmt]:
        """Parse: { statements }"""
        self._expect(TokenType.LBRACE, "Expected '{'")
        
        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._parse_statement())
        
        self._expect(TokenType.RBRACE, "Expected '}'")
        return statements
    
    # =========================================================================
    # Statement Parsing
    # =========================================================================
    
    def _parse_statement(self) -> Stmt:
        """Parse a single statement."""
        if self._check(TokenType.LET):
            return self._parse_let_stmt()
        elif self._check(TokenType.RETURN):
            return self._parse_return_stmt()
        elif self._check(TokenType.IF):
            return self._parse_if_stmt()
        else:
            return self._parse_expr_stmt()
    
    def _parse_let_stmt(self) -> LetStmt:
        """Parse: let x = value"""
        self._expect(TokenType.LET, "Expected 'let'")
        name_token = self._expect(TokenType.IDENT, "Expected variable name")
        
        # Optional type annotation
        type_annotation = None
        if self._match(TokenType.COLON):
            type_token = self._expect(TokenType.IDENT, "Expected type")
            type_annotation = type_token.value
        
        self._expect(TokenType.ASSIGN, "Expected '=' after variable name")
        value = self._parse_expr()
        
        return LetStmt(name_token.value, value, type_annotation)
    
    def _parse_return_stmt(self) -> ReturnStmt:
        """Parse: return [expr]"""
        self._expect(TokenType.RETURN, "Expected 'return'")
        
        # Check for empty return
        if self._check(TokenType.RBRACE):
            return ReturnStmt(None)
        
        value = self._parse_expr()
        return ReturnStmt(value)
    
    def _parse_if_stmt(self) -> IfStmt:
        """Parse: if condition { body } [else { body }]"""
        self._expect(TokenType.IF, "Expected 'if'")
        condition = self._parse_expr()
        then_body = self._parse_block()
        
        else_body = None
        if self._match(TokenType.ELSE):
            else_body = self._parse_block()
        
        return IfStmt(condition, then_body, else_body)
    
    def _parse_expr_stmt(self) -> ExprStmt:
        """Parse expression as statement."""
        expr = self._parse_expr()
        return ExprStmt(expr)
    
    # =========================================================================
    # Expression Parsing (Precedence Climbing)
    # =========================================================================
    
    def _parse_expr(self) -> Expr:
        """Parse expression (entry point)."""
        return self._parse_comparison()
    
    def _parse_comparison(self) -> Expr:
        """Parse: addition (("==" | "!=" | "<" | ">" | "<=" | ">=") addition)*"""
        expr = self._parse_addition()
        
        while True:
            op_token = self._match(
                TokenType.EQ, TokenType.NE,
                TokenType.LT, TokenType.GT,
                TokenType.LE, TokenType.GE
            )
            if not op_token:
                break
            right = self._parse_addition()
            expr = BinaryOp(expr, op_token.value, right)
        
        return expr
    
    def _parse_addition(self) -> Expr:
        """Parse: multiplication (("+" | "-") multiplication)*"""
        expr = self._parse_multiplication()
        
        while True:
            op_token = self._match(TokenType.PLUS, TokenType.MINUS)
            if not op_token:
                break
            right = self._parse_multiplication()
            expr = BinaryOp(expr, op_token.value, right)
        
        return expr
    
    def _parse_multiplication(self) -> Expr:
        """Parse: unary (("*" | "/" | "%") unary)*"""
        expr = self._parse_unary()
        
        while True:
            op_token = self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT)
            if not op_token:
                break
            right = self._parse_unary()
            expr = BinaryOp(expr, op_token.value, right)
        
        return expr
    
    def _parse_unary(self) -> Expr:
        """Parse: ("-") unary | call"""
        if op_token := self._match(TokenType.MINUS):
            operand = self._parse_unary()
            return UnaryOp(op_token.value, operand)
        
        return self._parse_call()
    
    def _parse_call(self) -> Expr:
        """Parse: primary ("(" arguments ")" | "." IDENT)*"""
        expr = self._parse_primary()
        
        while True:
            if self._match(TokenType.LPAREN):
                # Function call
                args = self._parse_arguments()
                self._expect(TokenType.RPAREN, "Expected ')' after arguments")
                expr = Call(expr, args)
            elif self._match(TokenType.DOT):
                # Field access
                field_token = self._expect(TokenType.IDENT, "Expected field name after '.'")
                expr = FieldAccess(expr, field_token.value)
            else:
                break
        
        return expr
    
    def _parse_arguments(self) -> List[Expr]:
        """Parse function call arguments."""
        args = []
        
        if self._check(TokenType.RPAREN):
            return args  # No arguments
        
        while True:
            args.append(self._parse_expr())
            if not self._match(TokenType.COMMA):
                break
        
        return args
    
    def _parse_primary(self) -> Expr:
        """Parse primary expression (literals, identifiers, grouped)."""
        # Integer
        if token := self._match(TokenType.INT):
            return IntLiteral(int(token.value))
        
        # Float
        if token := self._match(TokenType.FLOAT):
            return FloatLiteral(float(token.value))
        
        # String
        if token := self._match(TokenType.STRING):
            return StringLiteral(token.value)
        
        # Boolean
        if self._match(TokenType.TRUE):
            return BoolLiteral(True)
        if self._match(TokenType.FALSE):
            return BoolLiteral(False)
        
        # Identifier
        if token := self._match(TokenType.IDENT):
            return Identifier(token.value)
        
        # Grouped expression
        if self._match(TokenType.LPAREN):
            expr = self._parse_expr()
            self._expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        raise ParseError(f"Unexpected token: {self._peek().value!r}", self._peek())


def parse(tokens: List[Token]) -> Program:
    """Convenience function to parse tokens into AST."""
    parser = Parser(tokens)
    return parser.parse()


# =============================================================================
# Debug / Testing
# =============================================================================

def debug_ast(source: str):
    """Print AST for debugging."""
    from .lexer import tokenize
    
    print(f"Source:\n{source}\n")
    print("AST:")
    print("-" * 50)
    
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
        _print_ast(ast)
    except (ParseError, Exception) as e:
        print(f"ERROR: {e}")


def _print_ast(node, indent: int = 0):
    """Pretty-print AST node."""
    prefix = "  " * indent
    
    if isinstance(node, Program):
        print(f"{prefix}Program:")
        print(f"{prefix}  Imports:")
        for imp in node.imports:
            _print_ast(imp, indent + 2)
        print(f"{prefix}  Functions:")
        for fn in node.functions:
            _print_ast(fn, indent + 2)
        print(f"{prefix}  Statements:")
        for stmt in node.statements:
            _print_ast(stmt, indent + 2)
    
    elif isinstance(node, PythonImport):
        alias = f" as {node.alias}" if node.alias else ""
        print(f"{prefix}PythonImport: {node.module}{alias}")
    
    elif isinstance(node, FnDecl):
        params = ", ".join(p.name for p in node.params)
        print(f"{prefix}FnDecl: {node.name}({params})")
        for stmt in node.body:
            _print_ast(stmt, indent + 1)
    
    elif isinstance(node, LetStmt):
        print(f"{prefix}LetStmt: {node.name} =")
        _print_ast(node.value, indent + 1)
    
    elif isinstance(node, ExprStmt):
        print(f"{prefix}ExprStmt:")
        _print_ast(node.expr, indent + 1)
    
    elif isinstance(node, Call):
        print(f"{prefix}Call:")
        _print_ast(node.callee, indent + 1)
        print(f"{prefix}  Args:")
        for arg in node.arguments:
            _print_ast(arg, indent + 2)
    
    elif isinstance(node, BinaryOp):
        print(f"{prefix}BinaryOp: {node.operator}")
        _print_ast(node.left, indent + 1)
        _print_ast(node.right, indent + 1)
    
    elif isinstance(node, Identifier):
        print(f"{prefix}Ident: {node.name}")
    
    elif isinstance(node, IntLiteral):
        print(f"{prefix}Int: {node.value}")
    
    elif isinstance(node, FloatLiteral):
        print(f"{prefix}Float: {node.value}")
    
    elif isinstance(node, StringLiteral):
        print(f"{prefix}String: {node.value!r}")
    
    elif isinstance(node, BoolLiteral):
        print(f"{prefix}Bool: {node.value}")
    
    elif isinstance(node, FieldAccess):
        print(f"{prefix}FieldAccess: .{node.field}")
        _print_ast(node.object, indent + 1)
    
    else:
        print(f"{prefix}{type(node).__name__}: {node}")


if __name__ == "__main__":
    test_source = '''
from python import math

fn add(a, b) {
    return a + b
}

fn main() {
    let x = 10
    let y = 20
    let result = add(x, y)
    print(result)
    print(math.sqrt(16))
}
'''
    debug_ast(test_source)
