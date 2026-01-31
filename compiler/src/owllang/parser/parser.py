"""
OwlLang Parser

Converts tokens into an Abstract Syntax Tree (AST).
Uses recursive descent parsing.
"""

from __future__ import annotations

from ..ast import (
    Token, TokenType,
    # Expressions
    Expr, IntLiteral, FloatLiteral, StringLiteral, BoolLiteral,
    Identifier, BinaryOp, UnaryOp, Call, FieldAccess, TryExpr,
    # Pattern Matching
    Pattern, SomePattern, NonePattern, OkPattern, ErrPattern,
    MatchArm, MatchExpr,
    # Type Annotations
    TypeAnnotation,
    # Statements
    Stmt, LetStmt, ExprStmt, ReturnStmt, IfStmt,
    # Declarations
    Parameter, FnDecl, PythonImport, PythonFromImport, Program
)


class ParseError(Exception):
    """Error during parsing."""
    
    def __init__(self, message: str, token: Token) -> None:
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
    
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> Program:
        """Parse the entire program."""
        imports: list[PythonImport | PythonFromImport] = []
        functions: list[FnDecl] = []
        statements: list[Stmt] = []
        
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
    
    def _match(self, *token_types: TokenType) -> Token | None:
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
    
    def _parse_import(self) -> PythonImport | PythonFromImport:
        """Parse: from python import math [as m]"""
        self._expect(TokenType.FROM, "Expected 'from'")
        self._expect(TokenType.PYTHON, "Expected 'python'")
        
        # Check for dotted module path: from python.os.path import ...
        module_parts: list[str] = []
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
    
    def _parse_import_names(self) -> list[tuple[str, str | None]]:
        """Parse import names: join, exists as e"""
        names: list[tuple[str, str | None]] = []
        
        while True:
            name_token = self._expect(TokenType.IDENT, "Expected import name")
            alias: str | None = None
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
            return_type = self._parse_type_annotation()
        
        body = self._parse_block()
        
        return FnDecl(name_token.value, params, body, return_type)
    
    def _parse_type_annotation(self) -> TypeAnnotation:
        """
        Parse a type annotation: Int, String, Option[Int], Result[Int, String]
        
        Grammar:
            type_annotation := IDENT ('[' type_annotation (',' type_annotation)* ']')?
        """
        name_token = self._expect(TokenType.IDENT, "Expected type name")
        name = name_token.value
        params: list[TypeAnnotation] = []
        
        # Check for parameterized type: Type[...]
        if self._match(TokenType.LBRACKET):
            # Parse first type parameter
            params.append(self._parse_type_annotation())
            
            # Parse additional type parameters
            while self._match(TokenType.COMMA):
                params.append(self._parse_type_annotation())
            
            self._expect(TokenType.RBRACKET, "Expected ']' after type parameters")
        
        return TypeAnnotation(name, params)
    
    def _parse_params(self) -> list[Parameter]:
        """Parse function parameters: a, b, c"""
        params: list[Parameter] = []
        
        if self._check(TokenType.RPAREN):
            return params  # No parameters
        
        while True:
            name_token = self._expect(TokenType.IDENT, "Expected parameter name")
            
            # Optional type annotation: : Type
            type_annotation = None
            if self._match(TokenType.COLON):
                type_annotation = self._parse_type_annotation()
            
            params.append(Parameter(name_token.value, type_annotation))
            
            if not self._match(TokenType.COMMA):
                break
        
        return params
    
    def _parse_block(self) -> list[Stmt]:
        """Parse: { statements }"""
        self._expect(TokenType.LBRACE, "Expected '{'")
        
        statements: list[Stmt] = []
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
            type_annotation = self._parse_type_annotation()
        
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
        """Parse: primary ("(" arguments ")" | "." IDENT | "?")*"""
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
            elif question_tok := self._match(TokenType.QUESTION):
                # Try operator (?)
                expr = TryExpr(expr, span=question_tok.span())
            else:
                break
        
        return expr
    
    def _parse_arguments(self) -> list[Expr]:
        """Parse function call arguments."""
        args: list[Expr] = []
        
        if self._check(TokenType.RPAREN):
            return args  # No arguments
        
        while True:
            args.append(self._parse_expr())
            if not self._match(TokenType.COMMA):
                break
        
        return args
    
    def _parse_primary(self) -> Expr:
        """Parse primary expression (literals, identifiers, grouped, match)."""
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
        
        # Match expression
        if match_token := self._match(TokenType.MATCH):
            return self._parse_match_expr(match_token)
        
        # Identifier
        if token := self._match(TokenType.IDENT):
            return Identifier(token.value)
        
        # Grouped expression
        if self._match(TokenType.LPAREN):
            expr = self._parse_expr()
            self._expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        raise ParseError(f"Unexpected token: {self._peek().value!r}", self._peek())
    
    def _parse_match_expr(self, match_token: Token) -> MatchExpr:
        """
        Parse match expression.
        
        match expr {
            pattern => body,
            pattern => body,
        }
        """
        # Parse subject expression
        subject = self._parse_expr()
        
        # Expect opening brace
        self._expect(TokenType.LBRACE, "Expected '{' after match expression")
        
        # Parse arms
        arms: list[MatchArm] = []
        while not self._check(TokenType.RBRACE):
            arm = self._parse_match_arm()
            arms.append(arm)
            
            # Optional comma between arms
            self._match(TokenType.COMMA)
        
        # Expect closing brace
        self._expect(TokenType.RBRACE, "Expected '}' after match arms")
        
        return MatchExpr(
            subject=subject,
            arms=arms,
            span=match_token.span()
        )
    
    def _parse_match_arm(self) -> MatchArm:
        """
        Parse a single match arm.
        
        pattern => body
        """
        pattern = self._parse_pattern()
        
        self._expect(TokenType.FAT_ARROW, "Expected '=>' after pattern")
        
        body = self._parse_expr()
        
        return MatchArm(
            pattern=pattern,
            body=body,
            span=None  # Could add span tracking here
        )
    
    def _parse_pattern(self) -> Pattern:
        """
        Parse a pattern: Some(x), None, Ok(v), Err(e)
        """
        token = self._expect(TokenType.IDENT, "Expected pattern (Some, None, Ok, or Err)")
        pattern_name = token.value
        span = token.span()
        
        if pattern_name == "None":
            return NonePattern(span=span)
        
        if pattern_name in ("Some", "Ok", "Err"):
            self._expect(TokenType.LPAREN, f"Expected '(' after {pattern_name}")
            binding_token = self._expect(TokenType.IDENT, "Expected binding name")
            binding = binding_token.value
            self._expect(TokenType.RPAREN, f"Expected ')' after binding")
            
            if pattern_name == "Some":
                return SomePattern(binding=binding, span=span)
            elif pattern_name == "Ok":
                return OkPattern(binding=binding, span=span)
            else:  # Err
                return ErrPattern(binding=binding, span=span)
        
        raise ParseError(
            f"Unknown pattern '{pattern_name}'. Expected Some, None, Ok, or Err",
            token
        )


def parse(tokens: list[Token]) -> Program:
    """Convenience function to parse tokens into AST."""
    parser = Parser(tokens)
    return parser.parse()
