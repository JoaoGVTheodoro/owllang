"""
OwlLang Diagnostic Codes

Centralized error and warning codes for the entire compiler.
Follows the pattern: E/Wxxxx where:
- E = Error (compilation blocked)
- W = Warning (compilation continues)
- xx = Category
- xx = Specific code

Categories:
- 01xx: Lexer
- 02xx: Parser  
- 03xx: Type/Scope
- 04xx: Import
- 05xx: Control Flow
"""

from enum import Enum


class ErrorCode(Enum):
    """Error codes that block compilation."""
    
    # Lexer errors (E01xx)
    UNEXPECTED_CHAR = "E0101"
    UNTERMINATED_STRING = "E0102"
    INVALID_NUMBER = "E0103"
    UNTERMINATED_COMMENT = "E0104"
    
    # Parser errors (E02xx)
    UNEXPECTED_TOKEN = "E0201"
    MISSING_TOKEN = "E0202"
    INVALID_SYNTAX = "E0203"
    MISSING_BRACE = "E0204"
    MISSING_PAREN = "E0205"
    MALFORMED_MATCH = "E0206"
    
    # Type errors (E03xx)
    TYPE_MISMATCH = "E0301"
    UNDEFINED_VARIABLE = "E0302"
    UNDEFINED_FUNCTION = "E0303"
    INVALID_OPERATION = "E0304"
    INCOMPATIBLE_TYPES = "E0305"
    RETURN_TYPE_MISMATCH = "E0306"
    BRANCH_TYPE_MISMATCH = "E0307"
    WRONG_ARG_COUNT = "E0308"
    CONDITION_NOT_BOOL = "E0309"
    CANNOT_NEGATE = "E0310"
    TRY_NOT_RESULT = "E0311"
    TRY_OUTSIDE_RESULT_FN = "E0312"
    TRY_ERROR_TYPE_MISMATCH = "E0313"
    WRONG_TYPE_ARITY = "E0314"
    UNKNOWN_TYPE = "E0315"
    
    # Scope errors (E03xx continued)
    VARIABLE_REDEFINITION = "E0320"
    USE_BEFORE_DEFINITION = "E0321"
    ILLEGAL_SHADOWING = "E0322"
    ASSIGNMENT_TO_IMMUTABLE = "E0323"
    CONST_WITHOUT_VALUE = "E0324"
    
    # Import errors (E04xx)
    IMPORT_NOT_FOUND = "E0401"
    INVALID_IMPORT = "E0402"
    
    # Control flow errors (E05xx)
    MISSING_RETURN = "E0501"
    UNREACHABLE_CODE = "E0502"
    NON_EXHAUSTIVE_MATCH = "E0503"
    INVALID_PATTERN = "E0504"
    BREAK_OUTSIDE_LOOP = "E0505"
    CONTINUE_OUTSIDE_LOOP = "E0506"
    FOR_IN_NOT_LIST = "E0507"


class WarningCode(Enum):
    """Warning codes that don't block compilation.
    
    Implementation Status:
        ✅ Implemented - warning is actively checked
        📋 Reserved - code reserved for future implementation
    """
    
    # Variable warnings (W01xx)
    UNUSED_VARIABLE = "W0101"           # ✅ Implemented
    UNUSED_PARAMETER = "W0102"          # ✅ Implemented
    VARIABLE_NEVER_MUTATED = "W0103"    # 📋 Reserved: let mut but never mutated
    
    # Dead code warnings (W02xx)
    UNREACHABLE_CODE = "W0201"          # ✅ Implemented
    UNUSED_FUNCTION = "W0202"           # 📋 Reserved: function never called
    REDUNDANT_RETURN = "W0203"          # 📋 Reserved: return at end of Void fn
    LOOP_WITHOUT_EXIT = "W0204"         # ✅ Implemented
    
    # Style warnings (W03xx)
    REDUNDANT_MATCH = "W0301"           # 📋 Reserved: match with single case
    # W0302 removed: was TRIVIAL_IF, superseded by CONSTANT_CONDITION (W0306)
    UNNECESSARY_ELSE = "W0303"          # 📋 Reserved: else after return
    RESULT_IGNORED = "W0304"            # ✅ Implemented
    OPTION_IGNORED = "W0305"            # ✅ Implemented
    CONSTANT_CONDITION = "W0306"        # ✅ Implemented: if true/false
    
    # Shadowing warnings (W04xx)
    VARIABLE_SHADOWS = "W0401"          # 📋 Reserved: shadows outer variable


# Human-readable descriptions
ERROR_DESCRIPTIONS: dict[ErrorCode, str] = {
    ErrorCode.UNEXPECTED_CHAR: "Unexpected character in source",
    ErrorCode.UNTERMINATED_STRING: "String literal not closed",
    ErrorCode.INVALID_NUMBER: "Invalid numeric literal",
    ErrorCode.UNEXPECTED_TOKEN: "Unexpected token",
    ErrorCode.MISSING_TOKEN: "Expected token not found",
    ErrorCode.INVALID_SYNTAX: "Invalid syntax",
    ErrorCode.TYPE_MISMATCH: "Type mismatch",
    ErrorCode.UNDEFINED_VARIABLE: "Variable not defined",
    ErrorCode.UNDEFINED_FUNCTION: "Function not defined",
    ErrorCode.ASSIGNMENT_TO_IMMUTABLE: "Cannot assign to immutable variable",
    ErrorCode.MISSING_RETURN: "Function must return a value on all paths",
}

WARNING_DESCRIPTIONS: dict[WarningCode, str] = {
    WarningCode.UNUSED_VARIABLE: "Variable declared but never used",
    WarningCode.UNUSED_PARAMETER: "Parameter declared but never used",
    WarningCode.VARIABLE_NEVER_MUTATED: "Variable declared as mutable but never mutated",
    WarningCode.UNREACHABLE_CODE: "Code after this point will never execute",
    WarningCode.LOOP_WITHOUT_EXIT: "Infinite loop without break or return",
    WarningCode.REDUNDANT_MATCH: "Match expression with single case is redundant",
    WarningCode.RESULT_IGNORED: "Result value ignored; consider using match or ?",
    WarningCode.OPTION_IGNORED: "Option value ignored; consider using match",
    WarningCode.CONSTANT_CONDITION: "Condition is always true or always false",
    WarningCode.VARIABLE_SHADOWS: "Variable shadows a variable in outer scope",
}
