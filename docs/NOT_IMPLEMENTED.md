# OwlLang: What is NOT Implemented

> This document explicitly lists features that **do not exist** in OwlLang v0.2.4.x.
> Absence is a deliberate choice. This is a complete language within its scope.

---

## Excluded by Design

These features are intentionally omitted from OwlLang's design philosophy:

| Feature                  | Reason                                |
| ------------------------ | ------------------------------------- |
| **Null values**          | Use `Option[T]` for optional values   |
| **Exceptions**           | Use `Result[T, E]` for error handling |
| **Implicit coercion**    | All type conversions must be explicit |
| **Inheritance**          | Composition over inheritance          |
| **Mutable globals**      | All top-level bindings are immutable  |
| **Operator overloading** | Operators have fixed semantics        |
| **Macros**               | No compile-time metaprogramming       |
| **Reflection**           | No runtime type introspection         |

---

## Not Yet Implemented (Planned)

These features are planned for future versions:

### v0.2.5 — Structs

```owl
// NOT YET IMPLEMENTED
struct Point {
    x: Int,
    y: Int
}

let p = Point { x: 10, y: 20 }
```

### v0.3.x — Methods & Enums

```owl
// NOT YET IMPLEMENTED
impl Point {
    fn distance(self, other: Point) -> Float {
        // ...
    }
}

enum Color {
    Red,
    Green,
    Blue,
    RGB(Int, Int, Int)
}
```

### v0.3.x — Closures

```owl
// NOT YET IMPLEMENTED
let double = |x: Int| -> Int { x * 2 }
let result = map(numbers, |n| n + 1)
```

### v0.4.x — Generics

```owl
// NOT YET IMPLEMENTED
fn identity[T](x: T) -> T {
    x
}
```

### v0.4.x — Traits

```owl
// NOT YET IMPLEMENTED
trait Printable {
    fn to_string(self) -> String
}

impl Printable for Point {
    fn to_string(self) -> String {
        "(" + self.x + ", " + self.y + ")"
    }
}
```

### v0.4.x — Modules

```owl
// NOT YET IMPLEMENTED
mod math {
    pub fn add(a: Int, b: Int) -> Int { a + b }
}

use math::add
```

---

## What v0.2.4.x Does Have

For clarity, here is what **is** implemented:

### Types
- `Int`, `Float`, `String`, `Bool`, `Void`
- `Option[T]` with `Some(x)` and `None`
- `Result[T, E]` with `Ok(x)` and `Err(e)`
- `List[T]` with literals `[1, 2, 3]`
- `Any` for Python interop

### Control Flow
- `if/else` (statement and expression)
- `while`, `for-in`, `loop`
- `break`, `continue`, `return`
- `match` for `Option` and `Result`

### Functions
- `fn name(params) -> Type { body }`
- Implicit returns (last expression)
- Try operator `?` for `Result` propagation

### Variables
- `let x = value` (immutable)
- `let mut x = value` (mutable)
- Type annotations optional where inferable

### Built-in Functions
- `print(value)` — output to stdout
- `len(list)` — list length
- `get(list, index)` — element access
- `push(list, item)` — append (returns new list)
- `is_empty(list)` — check if empty
- `range(n)` / `range(start, end)` — generate list

### Python Interop
- `from python import module`
- `from python import { name } from module`
- Python values have type `Any`

---

## Behavioral Boundaries

These behaviors are explicitly **undefined** or **not guaranteed**:

| Behavior                    | Status                                     |
| --------------------------- | ------------------------------------------ |
| Index out of bounds         | Runtime error (not caught at compile time) |
| Division by zero            | Runtime error (not caught at compile time) |
| Integer overflow            | Python semantics (arbitrary precision)     |
| Evaluation order of args    | Left-to-right (not guaranteed to stay)     |
| Generated Python code style | May change between versions                |
| Python import resolution    | Delegated to Python runtime                |

---

## The Owl's Promise 🦉

> *"What is here is complete. What is not here is coming or deliberately absent."*

If you're looking for a feature not listed in "What v0.2.4.x Does Have", check:
1. [ROADMAP.md](ROADMAP.md) — Is it planned?
2. This document — Is it excluded by design?

If neither, feel free to propose it.

---

*This document is part of OwlLang v0.2.4.5-alpha.*
