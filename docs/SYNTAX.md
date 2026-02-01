# OwlLang Syntax Reference

> Complete syntax for OwlLang v0.2.x

This document describes **only implemented features**.
See [LANGUAGE.md](LANGUAGE.md) for the mental model.

---

## Comments

```owl
// Single-line comment

/*
  Multi-line
  comment
*/
```

---

## Variables

### Immutable (default)

```owl
let name = "Alice"
let age: Int = 30
let pi = 3.14159
```

### Mutable

```owl
let mut counter = 0
counter = counter + 1
```

Immutable variables cannot be reassigned:

```owl
let x = 10
x = 20  // Error E0323: assignment to immutable variable
```

---

## Types

### Primitives

| Type     | Description    | Literals                   |
| -------- | -------------- | -------------------------- |
| `Int`    | Integer        | `42`, `-7`, `0`            |
| `Float`  | Floating point | `3.14`, `-0.5`             |
| `String` | Text           | `"hello"`, `"line\nbreak"` |
| `Bool`   | Boolean        | `true`, `false`            |
| `Void`   | No value       | (functions only)           |

### Type Annotations

```owl
let x: Int = 42
let name: String = "Alice"
let items: List[Int] = [1, 2, 3]
let maybe: Option[String] = Some("value")
```

Type annotations are optional when the type can be inferred.

---

## Operators

### Arithmetic

| Operator | Meaning        |
| -------- | -------------- |
| `+`      | Addition       |
| `-`      | Subtraction    |
| `*`      | Multiplication |
| `/`      | Division       |
| `%`      | Modulo         |

### Comparison

| Operator | Meaning          |
| -------- | ---------------- |
| `==`     | Equal            |
| `!=`     | Not equal        |
| `<`      | Less than        |
| `>`      | Greater than     |
| `<=`     | Less or equal    |
| `>=`     | Greater or equal |

### Logical

| Operator | Meaning |
| -------- | ------- |
| `!`      | Not     |

Note: `&&` and `||` are not implemented. Use nested `if` for compound conditions.

---

## Functions

### Declaration

```owl
fn greet(name: String) {
    print("Hello, " + name)
}

fn add(a: Int, b: Int) -> Int {
    a + b  // Implicit return
}

fn divide(a: Int, b: Int) -> Int {
    return a / b  // Explicit return
}
```

### Rules

- Parameters require type annotations
- Return type defaults to `Void` if omitted
- Last expression is the return value (implicit return)

### Calling

```owl
greet("World")
let sum = add(1, 2)
```

---

## Control Flow

### If Statement

```owl
if condition {
    // ...
}

if condition {
    // ...
} else {
    // ...
}
```

### If Expression

When both branches are present, `if/else` returns a value:

```owl
let status = if age >= 18 { "adult" } else { "minor" }
```

### While Loop

```owl
let mut i = 0
while i < 10 {
    print(i)
    i = i + 1
}
```

### For-In Loop

```owl
let items = [1, 2, 3]
for item in items {
    print(item)
}
```

### Loop (Infinite)

```owl
loop {
    // runs forever until break or return
    if done {
        break
    }
}
```

### Break and Continue

```owl
for x in items {
    if x == 0 {
        continue  // Skip to next iteration
    }
    if x < 0 {
        break     // Exit loop
    }
    print(x)
}
```

---

## Lists

### Creation

```owl
let empty: List[Int] = []
let numbers = [1, 2, 3]
let strings = ["a", "b", "c"]
```

### Operations

| Function         | Description       | Example                      |
| ---------------- | ----------------- | ---------------------------- |
| `len(list)`      | Length            | `len([1,2,3])` → `3`         |
| `get(list, i)`   | Get element       | `get([1,2,3], 0)` → `1`      |
| `push(list, x)`  | Append (new list) | `push([1,2], 3)` → `[1,2,3]` |
| `is_empty(list)` | Check if empty    | `is_empty([])` → `true`      |

Lists are **immutable**. `push` returns a new list.

### Range

```owl
let nums = range(0, 5)  // [0, 1, 2, 3, 4]

for i in range(0, 10) {
    print(i)
}
```

---

## Option Type

### Constructors

```owl
let some: Option[Int] = Some(42)
let none: Option[Int] = None
```

### Pattern Matching

```owl
match maybe_value {
    Some(x) => print(x),
    None => print("No value")
}
```

---

## Result Type

### Constructors

```owl
let success: Result[Int, String] = Ok(42)
let failure: Result[Int, String] = Err("failed")
```

### Pattern Matching

```owl
match result {
    Ok(value) => print(value),
    Err(error) => print("Error: " + error)
}
```

### Try Operator

The `?` operator propagates errors:

```owl
fn process() -> Result[Int, String] {
    let a = step_one()?  // Returns Err early if step_one fails
    let b = step_two(a)?
    Ok(a + b)
}
```

`?` can only be used in functions that return `Result`.

---

## Match Expression

Match is an expression (returns a value):

```owl
let name = match status {
    Some(s) => s,
    None => "unknown"
}
```

### Rules

- All patterns must be covered (exhaustive)
- Pattern bindings are immutable

### Patterns

| Pattern   | Matches           |
| --------- | ----------------- |
| `Some(x)` | Option with value |
| `None`    | Empty Option      |
| `Ok(x)`   | Successful Result |
| `Err(e)`  | Error Result      |

---

## Python Interop

### Module Import

```owl
from python import math
from python import json as j

let x = math.sqrt(16)
```

### From Import

```owl
from python import { loads, dumps } from json
from python import { get } from requests

let data = loads('{"key": "value"}')
```

### Type Boundary

All Python values have type `Any`. Type safety stops at the Python boundary.

---

## Built-in Functions

| Function         | Signature               | Description     |
| ---------------- | ----------------------- | --------------- |
| `print(x)`       | `Any -> Void`           | Print to stdout |
| `len(list)`      | `List[T] -> Int`        | List length     |
| `get(list, i)`   | `List[T], Int -> T`     | Get element     |
| `push(list, x)`  | `List[T], T -> List[T]` | Append element  |
| `is_empty(list)` | `List[T] -> Bool`       | Check if empty  |
| `range(a, b)`    | `Int, Int -> List[Int]` | Create range    |

---

*This document describes OwlLang v0.2.x syntax.*
