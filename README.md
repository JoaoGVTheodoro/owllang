# OwlLang 🦉

> A modern, statically-typed language that transpiles to Python

[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/owl-lang/owl)
[![Version](https://img.shields.io/badge/version-0.1.0--alpha-blue.svg)](https://github.com/owl-lang/owl)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-364%20passing-brightgreen.svg)](https://github.com/owl-lang/owl)

**OwlLang** is an experimental programming language with a strong type system, first-class error handling via `Option` and `Result` types, and seamless Python interoperability. It transpiles to clean, readable Python code.

## ⚠️ Status: Alpha / Experimental

This is **v0.1.0-alpha** — the core language is semantically complete, but:
- Breaking changes may occur
- No backward compatibility guarantees
- Not recommended for production use

**However**, the language is consistent and testable. We encourage experimentation!

---

## 🚀 Quick Start

### Hello World

```owl
// hello.ow
fn main() {
    print("Hello, OwlLang!")
}
```

```bash
owl run hello.ow
# Output: Hello, OwlLang!
```

### Installation

```bash
# Clone the repository
git clone https://github.com/owl-lang/owl.git
cd owl/compiler

# Install in development mode
pip install -e ".[dev]"

# Verify installation
owl --version
# OwlLang 0.1.0-alpha
```

---

## ✨ Features

### Type-Safe Option & Result

Handle nullable values and errors at compile time:

```owl
fn divide(a: Int, b: Int) -> Option[Int] {
    if b == 0 {
        None
    } else {
        Some(a / b)
    }
}

fn read_file(path: String) -> Result[String, String] {
    if exists(path) {
        Ok(contents)
    } else {
        Err("File not found")
    }
}
```

### Pattern Matching with `match`

Exhaustive pattern matching on Option and Result:

```owl
fn handle_result(value: Option[Int]) -> String {
    match value {
        Some(n) => "Got: " + n,
        None => "Nothing"
    }
}

fn process(result: Result[Int, String]) -> Int {
    match result {
        Ok(value) => value,
        Err(msg) => {
            print("Error: " + msg)
            0
        }
    }
}
```

### Error Propagation with `?`

Propagate errors cleanly with the try operator:

```owl
fn compute() -> Result[Int, String] {
    let a = step1()?  // Returns early if Err
    let b = step2(a)?
    Ok(a + b)
}
```

### Implicit Returns

The last expression in a function is the return value:

```owl
fn add(a: Int, b: Int) -> Int {
    a + b  // No 'return' needed
}

fn classify(n: Int) -> String {
    if n > 0 {
        "positive"
    } else if n < 0 {
        "negative"
    } else {
        "zero"
    }
}
```

### Python Interop

Use any Python library:

```owl
from python import math
from python import json

fn calculate() {
    let result = math.sqrt(16.0)
    print(result)  // 4.0
}
```

### Rich Diagnostics

Clear, actionable error messages:

```
error[E0301]: incompatible types in assignment
 --> main.ow:5:10
  |
5 |     let x: Int = "hello"
  |            ^^^ expected Int, found String
  |
  = help: change the type annotation or convert the value
```

Helpful warnings:

```
warning[W0101]: unused variable `x`
 --> main.ow:3:9
  |
3 |     let x = 42
  |         ^ unused variable
  |
  = hint: if this is intentional, prefix with underscore: `_x`
```

---

## 🛠️ CLI Usage

```bash
# Compile to Python
owl compile program.ow           # Creates program.py
owl compile program.ow -o out.py # Custom output file

# Run directly
owl run program.ow

# Type check only
owl check program.ow             # Shows errors and warnings
owl check program.ow -W          # Treat warnings as errors
owl check program.ow --no-warnings  # Suppress warnings

# Debug
owl tokens program.ow            # Show lexer tokens
owl ast program.ow               # Show AST
```

---

## 📁 Examples

The [examples/](examples/) directory contains working examples:

| File                        | Description          |
| --------------------------- | -------------------- |
| `00_hello_world.ow`         | Basic hello world    |
| `01_variables_and_types.ow` | Type annotations     |
| `02_functions.ow`           | Function definitions |
| `03_if_expression.ow`       | If as expression     |
| `04_option_basic.ow`        | Option type usage    |
| `05_result_basic.ow`        | Result type usage    |
| `07_python_import.ow`       | Python interop       |
| `08_try_operator.ow`        | Error propagation    |

Run any example:

```bash
owl run examples/00_hello_world.ow
```

---

## 🚫 What OwlLang is NOT (yet)

To set expectations clearly:

- **No full generics** — Only `Option[T]` and `Result[T, E]` are parameterized
- **No custom types** — Structs, classes, enums not yet implemented
- **No runtime** — Transpiles to Python, depends on Python runtime
- **No performance guarantees** — Focus is on correctness, not speed
- **No backward compatibility** — API may change before 1.0
- **No package manager** — Use pip for dependencies
- **No LSP/IDE support** — Editor tooling planned for future

---

## 🧪 Running Tests

```bash
cd compiler
pip install -e ".[dev]"
pytest -v
# 364 tests passing
```

---

## 📚 Documentation

- [Philosophy](docs/PHILOSOPHY.md) — Why OwlLang exists
- [Syntax Guide](docs/SYNTAX.md) — Language reference
- [Architecture](docs/ARCHITECTURE.md) — Compiler internals

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

<p align="center">
  <b>🦉 OwlLang v0.1.0-alpha</b><br>
  <i>"Wisdom comes from seeing clearly in the dark"</i>
</p>
