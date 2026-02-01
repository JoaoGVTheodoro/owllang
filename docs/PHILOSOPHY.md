# OwlLang Design Philosophy

> The principles that guide OwlLang's design.

---

## Core Beliefs

### 1. Safe by Default

Errors should be caught at compile time, not runtime.

- Types are known before the program runs
- Variables cannot change unless explicitly marked
- Missing values (`Option`) and errors (`Result`) must be handled

### 2. Explicit Over Implicit

The reader should understand the code without hidden context.

```owl
let mut counter = 0   // Clearly mutable
let total = 100       // Clearly immutable

let result = risky_operation()
match result {
    Ok(value) => use(value),
    Err(e) => handle(e)
}
// Error handling is visible
```

### 3. Small and Predictable

A smaller language is easier to learn, easier to reason about, and has fewer edge cases.

OwlLang has:
- 5 primitive types
- 2 algebraic types (Option, Result)
- 1 collection type (List)
- 3 loop constructs
- 1 pattern matching construct

That's it.

### 4. Python Is a Friend

The Python ecosystem is a treasure. OwlLang compiles to readable Python so you can:
- Debug the output directly
- Use any Python library
- Integrate with existing tools

```owl
from python import json
from python import { get } from requests

let response = get("https://api.example.com")
let data = json.loads(response.text)
```

### 5. Immutable First

Mutability is a feature, not a default.

```owl
let x = 10        // Cannot change
let mut y = 20    // Can change

y = 25            // OK
x = 15            // Error
```

This makes code easier to understand: you know a value won't change unless you see `mut`.

### 6. Errors Are Values

There are no exceptions in OwlLang. Operations that can fail return `Result`:

```owl
fn divide(a: Int, b: Int) -> Result[Int, String] {
    if b == 0 {
        Err("division by zero")
    } else {
        Ok(a / b)
    }
}
```

You must handle the error or propagate it with `?`.

### 7. Absence Is Explicit

There is no `null`. A value that might not exist is `Option`:

```owl
fn find(id: Int) -> Option[User] {
    // Returns Some(user) or None
}
```

You must handle both cases.

---

## What OwlLang Is Not

- **Not a Python replacement**: It's a safer way to write Python-compatible code
- **Not performance-focused**: It's about correctness, not speed
- **Not feature-rich**: Simplicity is a feature
- **Not production-ready**: It's still alpha

---

## The Owl's Wisdom 🦉

> *"A wise owl knows what it doesn't need."*

OwlLang deliberately excludes:
- Inheritance
- Exceptions
- Null values
- Implicit type coercion
- Runtime metaprogramming

These features add complexity without adding safety.

---

*See [LANGUAGE.md](LANGUAGE.md) for the complete mental model.*
