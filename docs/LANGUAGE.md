# OwlLang

> A statically-typed language that transpiles to Python.

This document defines **what OwlLang is** and **how to think about it**.

---

## What is OwlLang?

OwlLang is a programming language designed for **clarity and safety**:

- **Statically typed**: All types are known at compile time
- **Immutable by default**: Variables cannot change unless explicitly marked
- **Explicit error handling**: No exceptions; errors are values
- **Python-compatible**: Transpiles to clean, readable Python

OwlLang is **not** a replacement for Python. It's a **safer way to write programs** that run on Python.

---

## Who is OwlLang for?

OwlLang is for programmers who want:

- Type safety without a heavy runtime
- Explicit handling of "might fail" and "might not exist"
- Readable Python output they can inspect and debug
- A small, predictable language

OwlLang is **not** for:

- Performance-critical code (use Rust, C, etc.)
- Existing Python codebases (the interop is one-way)
- Production systems (it's still alpha)

---

## The Core Rules

These rules define OwlLang. They will not change.

### 1. Everything is Immutable by Default

```owl
let x = 10       // Cannot be changed
let mut y = 20   // Can be changed
y = 30           // OK
x = 40           // Error: assignment to immutable variable
```

Mutability is **opt-in**, not opt-out.

### 2. All Types are Known at Compile Time

```owl
let name = "Alice"      // Inferred as String
let age: Int = 30       // Explicit annotation
let items = [1, 2, 3]   // Inferred as List[Int]
```

There is no `any` type for user code. The `Any` type exists internally for Python interop only — idiomatic OwlLang code never mentions `Any` explicitly. Attempting to annotate with `Any` produces error E0316. Type errors are caught before the program runs.

### 3. Functions Require Parameter Types

```owl
fn greet(name: String) {
    print("Hello, " + name)
}

fn add(a: Int, b: Int) -> Int {
    a + b
}
```

Return type defaults to `Void` if omitted.

### 4. `if/else` with Both Branches is an Expression

```owl
// As expression (returns a value)
let status = if age >= 18 { "adult" } else { "minor" }

// As statement (no else, no value)
if debug {
    print("debug mode")
}
```

### 5. Absence is Explicit: `Option[T]`

```owl
fn find(id: Int) -> Option[User] {
    if exists(id) {
        Some(get_user(id))
    } else {
        None
    }
}

match find(42) {
    Some(user) => print(user.name),
    None => print("Not found")
}
```

There is no `null`. A value either exists (`Some`) or doesn't (`None`).

### 6. Errors are Values: `Result[T, E]`

```owl
fn divide(a: Int, b: Int) -> Result[Int, String] {
    if b == 0 {
        Err("division by zero")
    } else {
        Ok(a / b)
    }
}

match divide(10, 0) {
    Ok(n) => print(n),
    Err(e) => print("Error: " + e)
}
```

There are no exceptions. Errors must be handled or propagated.

### 7. The `?` Operator Propagates Errors

```owl
fn compute() -> Result[Int, String] {
    let a = step_one()?   // Returns early if Err
    let b = step_two(a)?
    Ok(a + b)
}
```

`?` can only be used in functions that return `Result`.

### 8. Loops are Statements, Not Expressions

```owl
while condition {
    // ...
}

for item in items {
    // ...
}

loop {
    // infinite loop, exit with break
}
```

Loops do not return values. They execute for side effects.

### 9. Pattern Matching Must Be Exhaustive

```owl
match opt {
    Some(x) => handle(x),
    None => handle_none()
}
// Both cases required
```

The compiler rejects non-exhaustive matches.

### 10. Python Interop is Untyped

```owl
from python import json
from python import { get } from requests

let response = get("https://api.example.com")
// response has type Any
```

Python values have type `Any`. Type safety stops at the boundary.

---

## What the Compiler Guarantees

When OwlLang compiles successfully:

| Guarantee               | Meaning                                  |
| ----------------------- | ---------------------------------------- |
| **Type safety**         | No type mismatches at runtime            |
| **Exhaustive matching** | All pattern cases are covered            |
| **Immutability**        | Immutable variables are never reassigned |
| **Error awareness**     | `Result` and `Option` values are handled |
| **Scope validity**      | Variables are defined before use         |

---

## What the Compiler Does NOT Guarantee

| Not Guaranteed            | Why                                         |
| ------------------------- | ------------------------------------------- |
| **Runtime errors**        | Division by zero, index out of bounds, etc. |
| **Python interop safety** | Python values are `Any`                     |
| **Performance**           | No optimization pass                        |
| **Resource management**   | No ownership/borrowing system               |

OwlLang catches **type errors**, not **logic errors**.

---

## Error vs Warning

| Diagnostic  | Effect               | Action Required |
| ----------- | -------------------- | --------------- |
| **Error**   | Compilation fails    | Must fix        |
| **Warning** | Compilation succeeds | Should review   |

### Common Errors
- `E0301`: Type mismatch
- `E0302`: Undefined variable
- `E0323`: Assignment to immutable variable
- `E0503`: Non-exhaustive match

### Common Warnings
- `W0101`: Unused variable
- `W0201`: Unreachable code
- `W0304`: Result value ignored

Prefix a variable with `_` to silence unused warnings: `let _unused = value`

---

## The Types

### Primitives
| Type     | Description    | Example         |
| -------- | -------------- | --------------- |
| `Int`    | Integer        | `42`            |
| `Float`  | Floating point | `3.14`          |
| `String` | Text           | `"hello"`       |
| `Bool`   | Boolean        | `true`, `false` |
| `Void`   | No value       | (no literal)    |

### Algebraic Types
| Type           | Description      | Constructors      |
| -------------- | ---------------- | ----------------- |
| `Option[T]`    | Optional value   | `Some(x)`, `None` |
| `Result[T, E]` | Success or error | `Ok(x)`, `Err(e)` |

### Collections
| Type      | Description        | Example     |
| --------- | ------------------ | ----------- |
| `List[T]` | Ordered collection | `[1, 2, 3]` |

---

## Summary

OwlLang is simple by design:

- **5 primitive types**: Int, Float, String, Bool, Void
- **2 algebraic types**: Option, Result
- **1 collection type**: List
- **3 loop constructs**: while, for-in, loop
- **1 matching construct**: match

If you understand these concepts, you understand OwlLang.

---

*This document describes OwlLang v0.2.x. See [STABILITY.md](STABILITY.md) for what is stable.*
