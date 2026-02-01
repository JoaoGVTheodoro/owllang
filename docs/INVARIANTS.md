# OwlLang Language Invariants

This document defines the **fundamental invariants** of OwlLang — the core rules that must never be violated. These invariants form the conceptual foundation of the language.

> **For stability guarantees and versioning policy, see [STABILITY.md](STABILITY.md).**

---

## 1. Expression vs Statement

### Invariant 1.1: Everything That Produces a Value Is an Expression

| Construct                        | Classification | Notes                      |
| -------------------------------- | -------------- | -------------------------- |
| Literals (`42`, `"hi"`, `true`)  | Expression     | Always                     |
| Identifiers (`x`)                | Expression     | Always                     |
| Binary/Unary ops (`a + b`, `-x`) | Expression     | Always                     |
| Function calls (`f(x)`)          | Expression     | Always                     |
| `match`                          | Expression     | Always produces a value    |
| `if/else`                        | Expression     | When both branches present |
| `if` (no else)                   | Statement      | Cannot be used as value    |

### Invariant 1.2: Expressions Can Be Used as Statements

Any expression can appear in statement position via `ExprStmt`. The value is discarded unless:
- It's the last statement in a function with non-Void return type (implicit return)
- The expression is `Result` or `Option` (generates warning)

### Invariant 1.3: Loops Are Always Statements

| Construct | Classification |
| --------- | -------------- |
| `while`   | Statement      |
| `for-in`  | Statement      |
| `loop`    | Statement      |

Loops never produce values. They execute for side effects only.

---

## 2. Type System

### Invariant 2.1: Static Typing

All types are determined at compile time. There is no runtime type checking.

### Invariant 2.2: Type Inference with Annotations

- Type annotations are optional when types can be inferred
- Type annotations are required for function parameters
- Type annotations are optional for return types (defaults to Void)

### Invariant 2.3: Core Types Are Fixed

| Type     | Description                 |
| -------- | --------------------------- |
| `Int`    | 64-bit signed integer       |
| `Float`  | 64-bit floating point       |
| `String` | UTF-8 string                |
| `Bool`   | `true` or `false`           |
| `Void`   | No value (unit type)        |
| `Any`    | Python interop escape hatch |

### Invariant 2.4: Algebraic Types

| Type           | Variants                       |
| -------------- | ------------------------------ |
| `Option[T]`    | `Some(T)`, `None`              |
| `Result[T, E]` | `Ok(T)`, `Err(E)`              |
| `List[T]`      | Homogeneous ordered collection |

### Invariant 2.5: Type Compatibility

- `Any` is compatible with all types (Python interop)
- `Option[Any]` matches any `Option[T]`
- `Result[Any, Any]` matches any `Result[T, E]`
- `List[Any]` matches any `List[T]` (empty list)

---

## 3. Mutability

### Invariant 3.1: Immutable by Default

All bindings are immutable unless explicitly marked with `mut`:

```owl
let x = 10      // immutable
let mut y = 20  // mutable
```

### Invariant 3.2: Mutability Is Local

Mutability does not propagate:
- `let mut xs = [1, 2, 3]` — the binding is mutable, not the list
- Lists are always immutable; `push` returns a new list

### Invariant 3.3: Assignment Requires Mutability

Assignment (`x = value`) is only valid for `let mut` bindings.
Assigning to immutable binding produces error E0323.

---

## 4. Control Flow

### Invariant 4.1: Loop Constructs

| Construct         | Purpose                | Exit                 |
| ----------------- | ---------------------- | -------------------- |
| `while cond { }`  | Conditional repetition | Condition false      |
| `for x in xs { }` | Collection iteration   | Collection exhausted |
| `loop { }`        | Infinite loop          | `break` or `return`  |

### Invariant 4.2: Break and Continue

- `break` exits the innermost loop
- `continue` skips to the next iteration
- Both are errors outside loops (E0505, E0506)

### Invariant 4.3: Return

- `return expr` exits the function with value
- `return` (no value) is only valid in Void functions
- Implicit return: last expression is the return value

---

## 5. Pattern Matching

### Invariant 5.1: Match Is Exhaustive

All `match` expressions must cover all possible cases:
- `Option[T]` requires `Some(_)` and `None`
- `Result[T, E]` requires `Ok(_)` and `Err(_)`

Non-exhaustive match produces error E0503.

### Invariant 5.2: Pattern Bindings Are Immutable

Variables bound in patterns (`Some(x)`, `Ok(value)`) are always immutable.

### Invariant 5.3: Try Operator

The `?` operator on `Result`:
- Unwraps `Ok(x)` to `x`
- Returns `Err(e)` from the function immediately
- Only valid in functions returning `Result` (E0312)

---

## 6. Functions

### Invariant 6.1: Function Signature

```owl
fn name(param: Type, ...) -> ReturnType {
    body
}
```

- Parameters require type annotations
- Return type defaults to Void if omitted
- Body is a sequence of statements

### Invariant 6.2: Implicit vs Explicit Return

- **Explicit**: `return expr` anywhere in function
- **Implicit**: Last expression in function body
- Functions must return on all paths (E0501)

### Invariant 6.3: Main Function

- `fn main()` is the entry point
- Main has no parameters and returns Void
- Main is optional (script mode)

---

## 7. Scope

### Invariant 7.1: Lexical Scoping

Variables are visible from declaration to end of enclosing block.

### Invariant 7.2: Shadowing Is Allowed

Inner scopes can shadow outer variables:

```owl
let x = 10
if true {
    let x = 20  // shadows outer x
}
```

### Invariant 7.3: Loop Variables

- `for x in xs` — `x` is scoped to loop body, immutable
- Loop variables shadow outer variables of same name

---

## 8. Diagnostics

### Invariant 8.1: Error Codes Are Stable

Once assigned, error codes never change meaning:
- `Exxxx` — Errors (compilation blocked)
- `Wxxxx` — Warnings (compilation continues)

### Invariant 8.2: Categories Are Fixed

| Range | Category     |
| ----- | ------------ |
| E01xx | Lexer        |
| E02xx | Parser       |
| E03xx | Type/Scope   |
| E04xx | Import       |
| E05xx | Control Flow |
| W01xx | Unused       |
| W02xx | Dead Code    |
| W03xx | Style        |
| W04xx | Shadowing    |

### Invariant 8.3: Warning Suppression

Prefixing a name with `_` suppresses unused warnings:
- `let _unused = value` — no W0101
- `fn f(_param: Int)` — no W0102

---

## 9. Python Interop

### Invariant 9.1: Import Syntax

```owl
from python import module
from python import module as alias
from python import { name1, name2 } from module
```

### Invariant 9.2: Any Type Escape

All Python values have type `Any`. No type checking on Python interop.

### Invariant 9.3: Transpilation Target

OwlLang transpiles to Python. The generated code is not part of the API.

---

## Version History

| Version        | Changes                     |
| -------------- | --------------------------- |
| v0.2.4.2-alpha | Validated, no changes       |
| v0.2.4.1-alpha | Initial invariants document |
