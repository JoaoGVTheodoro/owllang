# OwlLang Compiler Invariants

This document defines fundamental properties that the OwlLang compiler must maintain at all times. These invariants are enforced by tests in [`tests/test_invariants.py`](../tests/test_invariants.py).

> **See also**: [STABILITY.md](../../docs/STABILITY.md) for public API stability guarantees.

## 1. Diagnostic Code Format

### Error Codes

**Invariant**: All error codes must follow the format `Exxxx` where:
- First character is `E` (uppercase)
- Followed by exactly 4 digits
- Total length is 5 characters

**Example**: `E0301`, `E0502`

**Categories**:
- `E01xx`: Lexer errors
- `E02xx`: Parser errors
- `E03xx`: Type and scope errors
- `E04xx`: Import errors
- `E05xx`: Control flow errors

### Warning Codes

**Invariant**: All warning codes must follow the format `Wxxxx` where:
- First character is `W` (uppercase)
- Followed by exactly 4 digits
- Total length is 5 characters

**Example**: `W0101`, `W0201`

**Categories**:
- `W01xx`: Variable warnings (unused, never mutated)
- `W02xx`: Dead code warnings
- `W03xx`: Style warnings
- `W04xx`: Shadowing warnings

### Code Uniqueness

**Invariant**: All diagnostic codes must be unique.
- No two errors can share the same code
- No two warnings can share the same code
- Error codes and warning codes must not overlap

## 2. No Duplicate Diagnostics

**Invariant**: Each issue in the source code must generate exactly one diagnostic.

- If there's a type mismatch, exactly one error is generated
- If a variable is unused, exactly one warning is generated
- Running the checker twice on the same code produces identical diagnostics

**Why**: Duplicate diagnostics confuse users and indicate flawed logic in the checker.

## 3. Determinism

### Warning Determinism

**Invariant**: Given the same input AST, the type checker must always produce:
- The same warnings
- In the same order
- With the same codes and messages

**Why**: Non-deterministic behavior makes the compiler unpredictable and hard to test.

### Error Determinism

**Invariant**: Errors must also be deterministic.

**Note**: While multiple errors can exist for one issue (e.g., "type mismatch" and "implicit return type mismatch"), each distinct error condition should produce consistent results.

## 4. Error and Warning Separation

**Invariant**: Errors and warnings are distinct categories:

- **Errors** (E-codes):
  - Block compilation
  - Indicate semantic incorrectness
  - Must be fixed for valid program

- **Warnings** (W-codes):
  - Do not block compilation
  - Indicate potential issues or style problems
  - Can be suppressed with `--no-warnings`
  - Can be promoted to errors with `--deny-warnings`

**Coexistence**: A program can have both errors and warnings simultaneously. They are independent.

## 5. Checker State Isolation

**Invariant**: Each call to `TypeChecker.check()` must be independent:

- Errors from previous runs must not leak
- Warnings from previous runs must not leak
- Environment state must reset between runs

**Why**: The checker may be called multiple times during testing or in an IDE. State leakage causes false positives.

**Implementation**: The `check()` method resets:
```python
self.errors = []
self.diagnostics = []
self.warnings = []
```

## 6. Span Tracking

**Invariant (v0.2.4.6+)**: All diagnostics must have valid source spans.

**Implementation**: 
- The parser propagates spans to all AST nodes (expressions, statements, declarations)
- The checker extracts spans from AST nodes when creating diagnostics
- DUMMY_SPAN is only used as a fallback for legacy code paths

**Why**: Accurate spans are essential for:
- IDE integration
- User-friendly error messages
- Source highlighting
- Jump-to-error functionality

**Coverage**: Spans are now tracked for:
- All literals (Int, Float, String, Bool)
- Identifiers
- Binary and unary operations
- Function calls and field access
- All statements (let, assign, if, while, for, loop, return, break, continue)
- Function declarations

## 7. Type System Escape Hatches

### The `Any` Type

**Invariant**: `Any` is an **escape hatch**, not a "top type".

**Definition**: `Any` represents values that bypass static type checking. It is used exclusively for:
1. Python interop (imported modules and functions)
2. Match arm bindings (until pattern-local type inference is implemented)
3. Varargs functions like `print`

**Behavior**:
- `Any` is compatible with all types (`types_compatible(ANY, X)` is always true)
- `Any` propagates through operations (`Any + Int` returns `Any`)
- `Any` in conditions is allowed (bypasses Bool check)
- Field access on `Any` returns `Any`

**Boundaries** (formalized in v0.2.4.7):
- **ALLOWED**: Using `Any` from Python imports
- **ALLOWED**: Passing `Any` to functions expecting specific types
- **BLOCKED (E0316)**: Explicit `Any` annotations are compilation errors
  - `let x: Any = 1` → Error
  - `fn f() -> Any {}` → Error
  - `fn f(x: Any) {}` → Error
  - `Option[Any]`, `Result[Any, E]`, `List[Any]` → Error

**Why "Escape Hatch" not "Top Type"**:
- Unlike a true top type (e.g., `Object` in Java), `Any` silently suppresses type errors
- It does not participate in normal subtyping relationships
- It exists for FFI, not for polymorphism
- Idiomatic OwlLang code NEVER mentions `Any` explicitly

**Implementation Details**:
- `Any` is NOT in `PRIMITIVE_TYPES` registry (users can't annotate with it)
- `_parse_type()` explicitly rejects `Any` with error E0316
- The `TypeError.from_diagnostic()` preserves notes explaining this is an internal type

**Future Consideration**: May add warnings when `Any` propagates unexpectedly.

### The `Unknown` Type

**Invariant**: `Unknown` represents type inference failure.

- When an expression's type cannot be determined, it gets `Unknown`
- Operations on `Unknown` don't generate errors (to avoid cascading diagnostics)
- `Unknown` is never user-visible; it's an internal sentinel

## 8. Warning Suppression Rules

**Invariant**: Variables/parameters starting with `_` suppress unused warnings.

```owl
fn example(_unused: Int) {  // No warning
    let _x = 1              // No warning
}
```

**Why**: This is a common convention in many languages (Python, Rust) and provides an escape hatch for intentionally unused bindings.

## 9. Code Categories are Stable

**Invariant**: Once a diagnostic code is assigned to a specific error/warning, it should not change meaning.

**Why**: Users and tools may rely on specific codes. Changing codes is a breaking change.

**Process**: When adding new diagnostics:
1. Choose an unused code in the appropriate category
2. Document it in `codes.py`
3. Add factory function in `error.py` or `warning.py`

## 10. Warnings Must Not Affect Semantics

**Invariant**: The presence or absence of warnings must not change program behavior.

- Warnings analyze code but don't modify it
- Suppressing warnings with `--no-warnings` doesn't change compilation output
- The only exception is `--deny-warnings`, which changes the exit code but not the generated code

**Why**: Warnings are for developer experience. They should never affect runtime behavior.

## 11. Factory Functions are the Source of Truth

**Invariant**: Diagnostics should always be created via factory functions, not directly.

**Example**:
```python
# ✅ Correct
error = type_mismatch_error("Int", "String", span)

# ❌ Wrong
error = DiagnosticError(
    code="E0301",
    message="type mismatch",
    span=span
)
```

**Why**: Factory functions ensure:
- Consistent message format
- Appropriate hints and notes
- Correct code assignment

---

## Testing Invariants

All invariants are verified by tests in `tests/test_invariants.py`:

```bash
pytest tests/test_invariants.py -v
```

Tests cover:
- Code format validation
- Uniqueness checks
- Determinism verification
- State isolation
- Error/warning separation

---

## Maintenance Guidelines

When adding new diagnostics:

1. ✅ Choose an appropriate code from the category
2. ✅ Add enum entry to `ErrorCode` or `WarningCode`
3. ✅ Create factory function in `error.py` or `warning.py`
4. ✅ Export from `__init__.py`
5. ✅ Add tests in `test_diagnostics.py`
6. ✅ Run `pytest tests/test_invariants.py` to verify invariants hold

When removing diagnostics:

1. ✅ Check if the code is used anywhere
2. ✅ Remove factory function
3. ✅ Keep enum entry with deprecation note (for stability)
4. ✅ Update tests

---

## Future Work

Planned improvements that don't violate invariants:

- ✅ ~~Replace all dummy spans with real spans~~ (v0.2.4.6)
- Add structured notes with spans (similar to Rust)
- Implement remaining warning types (shadowing, style)
- Add diagnostic severity levels (error, warning, info, hint)
- Add warnings when `Any` propagates unexpectedly through operations
