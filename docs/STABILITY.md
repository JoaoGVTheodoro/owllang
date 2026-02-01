# OwlLang Stability Contract

This document defines the stability guarantees for OwlLang and outlines what will remain stable, what may change, and what is experimental.

> **For language invariants and core rules, see [INVARIANTS.md](INVARIANTS.md).**

## Purpose

As OwlLang evolves through the 0.2.x series, this contract formalizes the boundaries of stability to help users and tool authors understand what they can depend on.

---

## Stability Tiers

### 🟢 Stable (Guaranteed until v0.3)

These features are frozen and will not change without a major version bump:

#### Language Semantics
- **Core types**: `Int`, `Float`, `String`, `Bool`, `Void`, `Any`
- **Algebraic types**: `Option[T]`, `Result[T, E]`
- **Collection types**: `List[T]`
- **Pattern matching**: `match` with `Some`, `None`, `Ok`, `Err` patterns
- **Error propagation**: `?` operator for `Result` types
- **Implicit returns**: Last expression is the return value
- **If expressions**: `if/else` returns a value when used as expression
- **Functions**: `fn name(params) -> Type { body }`
- **Mutability**: `let` (immutable) and `let mut` (mutable)
- **Loops**: `while`, `for-in`, `loop`
- **Control flow**: `break`, `continue`, `return`
- **Built-ins**: `print`, `len`, `get`, `push`, `is_empty`, `range`

#### Python Interop
- `from python import module`
- `from python import module as alias`
- `from python import { name1, name2 } from module`

#### CLI Interface
- `owl compile <file>` - Compile to Python
- `owl run <file>` - Compile and execute
- `owl check <file|dir>` - Type check without output
- `owl check --json` - Structured JSON output

#### Exit Codes
- `0` - Success
- `1` - Compilation error
- `2` - Warnings treated as errors (with `-W` or `--deny-warnings`)

#### Diagnostic Codes
- Format: `Exxxx` for errors, `Wxxxx` for warnings
- Existing codes will not change meaning
- Code categories are fixed (E01xx=Lexer, E02xx=Parser, etc.)

#### JSON Output Schema
```json
{
  "version": "string",
  "files": [{
    "file": "string",
    "success": "boolean",
    "errors": [{ "severity", "code", "message", "file", "line", "column", "hints", "notes" }],
    "warnings": [...]
  }],
  "summary": {
    "total_files": "number",
    "files_with_errors": "number",
    "total_errors": "number",
    "total_warnings": "number"
  }
}
```

---

### 🟡 Experimental (May change in v0.2)

These features work but their API/behavior may change:

#### CLI Flags
- `--profile` - Timing breakdown (format may change)
- Debug commands: `tokens`, `ast` (output format unstable)

#### Error Messages
- The exact wording of error messages may be refined
- Hints and notes may be added or improved
- **v0.2.4.6+**: Span accuracy is now implemented for all diagnostics

#### Warning Behavior
- New warnings may be added
- Warning thresholds may be adjusted
- Warning suppression mechanisms may be extended

---

### 🔴 Unstable (Internal)

These are implementation details and may change at any time:

- Internal AST node structure
- TypeChecker internal methods
- Transpiler output format (Python code style)
- Test utilities and helpers
- Debug output formats

---

## Versioning Policy

### What requires a MAJOR bump (0.x → 1.x)
- Removing stable language features
- Changing semantics of stable constructs
- Breaking CLI interface changes
- Removing or changing meaning of diagnostic codes

### What requires a MINOR bump (0.1.x → 0.2.x)
- Adding new language features
- Adding new CLI commands or flags
- Adding new diagnostic codes
- Deprecating (not removing) features

### What requires a PATCH bump (0.1.x → 0.1.y)
- Bug fixes
- Documentation improvements
- Test additions
- Error message improvements (wording only)
- Performance improvements

---

## Deprecation Policy

When deprecating a feature:

1. **Announce** - Document in CHANGELOG with deprecation notice
2. **Warn** - Add compiler warning for deprecated usage
3. **Wait** - Keep working for at least one minor version
4. **Remove** - Only remove in next major version

---

## Compatibility Promises

### Source Compatibility
Valid OwlLang 0.1.x code will remain valid in 0.1.y where y > x.

### Output Compatibility
The generated Python code may change (style, optimization), but:
- Runtime behavior will be preserved
- Public API of generated code is not guaranteed

### CLI Compatibility
- Stable commands and flags will work the same
- Exit codes are fixed
- JSON schema is fixed (fields may be added, not removed)

---

## Testing Contract

The following test suites enforce stability:

| Suite                          | Purpose                     |
| ------------------------------ | --------------------------- |
| `test_invariants.py`           | Compiler invariants         |
| `test_cli_ux.py`               | CLI behavior and exit codes |
| `test_semantic_consistency.py` | Language semantics          |
| `test_diagnostics.py`          | Error/warning format        |

All tests must pass before any release.

---

## Reporting Stability Issues

If you believe a stability guarantee has been violated:

1. Check this document to confirm the feature is marked stable
2. Open an issue with label `stability-violation`
3. Include: version, expected behavior, actual behavior
4. We will treat this as a high-priority bug

---

## Changelog

| Version        | Stability Changes                                |
| -------------- | ------------------------------------------------ |
| v0.2.4.7-alpha | Any type formalized, E0316 enforces boundaries   |
| v0.2.4.6-alpha | Span precision, Any type boundaries documented   |
| v0.2.4.5-alpha | Semantic lock tests, invariants, NOT_IMPLEMENTED |
| v0.2.4.4-alpha | Documentation reset, LANGUAGE.md                 |
| v0.2.4.3-alpha | Internal architecture, type registries           |
| v0.2.4.2-alpha | Documentation fixes, code audit                  |
| v0.2.4.1-alpha | Added INVARIANTS.md, updated v0.2.x              |
| v0.1.6-alpha   | Initial stability contract                       |
| v0.1.5-alpha   | CLI exit codes finalized                         |
| v0.1.4-alpha   | Semantic consistency pass                        |
| v0.1.0-alpha   | Initial language design                          |

---

*This document is part of the OwlLang v0.2.4.7-alpha release.*
