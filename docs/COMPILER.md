# OwlLang Compiler Architecture

This document describes the internal architecture of the OwlLang compiler.

> **For language semantics, see [INVARIANTS.md](INVARIANTS.md).**  
> **For syntax reference, see [SYNTAX.md](SYNTAX.md).**

---

## Overview

The OwlLang compiler follows a traditional pipeline:

```
Source Code → Lexer → Parser → TypeChecker → Transpiler → Python Code
```

Each stage has a single responsibility:

| Stage           | Responsibility    | Input           | Output          |
| --------------- | ----------------- | --------------- | --------------- |
| **Lexer**       | Tokenization      | Source string   | Token stream    |
| **Parser**      | Syntax analysis   | Token stream    | AST             |
| **TypeChecker** | Semantic analysis | AST             | Errors/Warnings |
| **Transpiler**  | Code generation   | AST (validated) | Python code     |

---

## Module Structure

```
compiler/src/owllang/
├── __init__.py          # Public API
├── __main__.py          # Entry point
├── cli.py               # Command-line interface
├── ast/
│   ├── __init__.py
│   └── nodes.py         # AST node definitions
├── lexer/
│   ├── __init__.py
│   └── lexer.py         # Tokenizer
├── parser/
│   ├── __init__.py
│   └── parser.py        # Recursive descent parser
├── typechecker/
│   ├── __init__.py
│   ├── checker.py       # Type checking logic
│   ├── types.py         # Type system definitions
│   └── builtins.py      # Built-in function registry
├── transpiler/
│   ├── __init__.py
│   └── transpiler.py    # Python code generator
└── diagnostics/
    ├── __init__.py
    ├── codes.py         # Error/warning code definitions
    ├── error.py         # Error factory functions
    ├── warning.py       # Warning factory functions
    ├── span.py          # Source location tracking
    └── printer.py       # Diagnostic formatting
```

---

## Design Principles

### 1. Single Responsibility

Each module has one job:

- **Lexer**: Convert characters to tokens
- **Parser**: Convert tokens to AST
- **TypeChecker**: Validate semantics, collect diagnostics
- **Transpiler**: Generate Python (assumes valid AST)

### 2. AST as Data, Not Behavior

The AST represents the structure of the program, not its semantics:

- AST nodes are plain dataclasses
- No methods that perform type checking or code generation
- Spans are attached for error reporting

### 3. Centralized Type System

All type definitions live in `typechecker/types.py`:

```python
# Primitive types
PRIMITIVE_TYPES = {"Int": INT, "Float": FLOAT, ...}

# Parameterized types
PARAMETERIZED_TYPES = {
    "Option": (1, lambda params: OptionType(params[0])),
    "Result": (2, lambda params: ResultType(params[0], params[1])),
    "List": (1, lambda params: ListType(params[0])),
}
```

Adding a new type (e.g., `StructType`) requires:
1. Define the type class
2. Register in `PARAMETERIZED_TYPES` (if parameterized)
3. Update type checker handlers

### 4. Centralized Built-ins

All built-in functions are defined in `typechecker/builtins.py`:

```python
BUILTIN_FUNCTIONS = {
    "print": BuiltinFunction(
        name="print",
        param_types=(ANY,),
        return_type=VOID,
        transpile_template="print({0})",
        doc="Print a value to stdout.",
    ),
    "len": ...,
    "get": ...,
    "push": ...,
    "is_empty": ...,
    "range": ...,
}
```

Each built-in defines:
- Type signature (for type checker)
- Transpilation template (for transpiler)
- Documentation

### 5. Transpiler as "Dumb Backend"

The transpiler:
- ✅ Assumes AST has passed type checking
- ✅ Uses templates from `BUILTIN_FUNCTIONS`
- ❌ Does not re-validate types
- ❌ Does not check semantic rules

If the type checker passed, the transpiler trusts the AST.

### 6. Diagnostic Factory Functions

All error and warning messages are created by factory functions in `diagnostics/`:

```python
# Good: Use factory function
self._add_diagnostic(type_mismatch_error(expected, found, span))

# Bad: Create message inline
self._error(f"Expected {expected}, got {found}", line, col)
```

Benefits:
- Consistent wording
- Single source of truth for messages
- Easy to update all occurrences

---

## Type System Architecture

### Type Hierarchy

```
OwlType (base)
├── INT, FLOAT, STRING, BOOL, VOID  (primitives)
├── ANY, UNKNOWN                      (special)
├── OptionType[T]                     (algebraic)
├── ResultType[T, E]                  (algebraic)
└── ListType[T]                       (collection)
```

### Type Registries

```python
# Lookup primitive type by name
lookup_primitive_type("Int")  # → INT
lookup_primitive_type("str")  # → STRING (alias)

# Lookup parameterized type
lookup_parameterized_type("Option")  # → (1, constructor)
lookup_parameterized_type("Result")  # → (2, constructor)
```

### Type Constructors

```python
TYPE_CONSTRUCTORS = {
    "Some": TypeConstructor(name="Some", param_count=1, creates_type="Option"),
    "None": TypeConstructor(name="None", param_count=0, creates_type="Option"),
    "Ok": TypeConstructor(name="Ok", param_count=1, creates_type="Result"),
    "Err": TypeConstructor(name="Err", param_count=1, creates_type="Result"),
}
```

---

## Extending the Compiler

### Adding a New Primitive Type

1. Add to `types.py`:
   ```python
   CHAR = OwlType("Char")
   PRIMITIVE_TYPES["Char"] = CHAR
   ```

2. No changes needed elsewhere (type checker uses registry)

### Adding a New Parameterized Type

1. Define type class in `types.py`:
   ```python
   @dataclass(frozen=True)
   class MapType(OwlType):
       key_type: OwlType
       value_type: OwlType
   ```

2. Register in `PARAMETERIZED_TYPES`:
   ```python
   PARAMETERIZED_TYPES["Map"] = (2, lambda p: MapType(p[0], p[1]))
   ```

### Adding a New Built-in Function

1. Add to `builtins.py`:
   ```python
   _register(BuiltinFunction(
       name="concat",
       param_types=(STRING, STRING),
       return_type=STRING,
       transpile_template="{0} + {1}",
       doc="Concatenate two strings.",
   ))
   ```

2. No changes needed in type checker or transpiler (they use registry)

---

## Version History

| Version        | Changes                                                       |
| -------------- | ------------------------------------------------------------- |
| v0.2.4.3-alpha | Added type registries, builtins module, simplified transpiler |
| v0.2.4.1-alpha | Initial documentation                                         |
