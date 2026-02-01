# OwlLang Technical Architecture

## Overview

OwlLang is designed as a **hybrid language** that:

1. **Transpiles** to Python for maximum ecosystem compatibility
2. **Compiles** to bytecode for optimized execution (future)
3. **Optionally compiles** to native code via LLVM (future)

```
                           OwlLang Architecture
                           
┌─────────────────────────────────────────────────────────────────────────┐
│                              OwlLang Source                              │
│                               (.owl files)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND                                      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────┐   │
│  │   Lexer     │ → │   Parser    │ → │        Type Checker         │   │
│  │  (Tokens)   │   │   (AST)     │   │  (Hindley-Milner Extended)  │   │
│  └─────────────┘   └─────────────┘   └─────────────────────────────┘   │
│                                                    │                     │
│                                                    ▼                     │
│                              ┌─────────────────────────────────────┐    │
│                              │          Typed AST (TAST)           │    │
│                              └─────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
┌───────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│   Python Transpiler   │ │   Owl Bytecode   │ │    LLVM Backend      │
│   (Phase 1 - MVP)     │ │   (Phase 2)      │ │    (Phase 3)         │
└───────────────────────┘ └──────────────────┘ └──────────────────────┘
           │                       │                      │
           ▼                       ▼                      ▼
┌───────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│  Python Source (.py)  │ │  Owl Bytecode    │ │  Native Binary       │
│         +             │ │     (.owc)       │ │  (ELF/Mach-O/PE)     │
│  CPython Runtime      │ │        +         │ │                      │
│                       │ │  OwlVM Runtime   │ │                      │
└───────────────────────┘ └──────────────────┘ └──────────────────────┘
```

---

## Component Details

### 1. Lexer

Converts source code into tokens.

```
Input:  fn add(a: Int, b: Int) -> Int { a + b }

Output: [
    Token(FN, "fn"),
    Token(IDENT, "add"),
    Token(LPAREN, "("),
    Token(IDENT, "a"),
    Token(COLON, ":"),
    Token(TYPE, "Int"),
    Token(COMMA, ","),
    Token(IDENT, "b"),
    Token(COLON, ":"),
    Token(TYPE, "Int"),
    Token(RPAREN, ")"),
    Token(ARROW, "->"),
    Token(TYPE, "Int"),
    Token(LBRACE, "{"),
    Token(IDENT, "a"),
    Token(PLUS, "+"),
    Token(IDENT, "b"),
    Token(RBRACE, "}")
]
```

### 2. Parser

Builds Abstract Syntax Tree (AST).

```
AST:
FunctionDecl {
    name: "add",
    params: [
        Param { name: "a", type: Int },
        Param { name: "b", type: Int }
    ],
    return_type: Int,
    body: BinaryExpr {
        op: Add,
        left: Ident("a"),
        right: Ident("b")
    }
}
```

### 3. Type Checker

- Uses **Hindley-Milner** type inference with extensions
- Supports **gradual typing** (like TypeScript)
- Validates all type constraints at compile time

```
// Input
let x = 42
let y = x + 1.5  // Error: Int + Float

// Type checker output:
Error at line 2: Cannot apply operator '+' to types 'Int' and 'Float'
  Hint: Convert one operand: x.to_float() + 1.5
```

### 4. Typed AST (TAST)

AST with full type annotations for code generation.

```
TypedFunctionDecl {
    name: "add",
    type: (Int, Int) -> Int,
    params: [
        TypedParam { name: "a", type: Int },
        TypedParam { name: "b", type: Int }
    ],
    body: TypedBinaryExpr {
        type: Int,
        op: Add,
        left: TypedIdent { name: "a", type: Int },
        right: TypedIdent { name: "b", type: Int }
    }
}
```

---

## Python Interoperability Layer

### Strategy: Transparent Transpilation

```
┌─────────────────────────────────────────────────────────────────┐
│                     OwlLang Module                               │
│  from python import numpy as np                                  │
│  let arr = np.array([1, 2, 3])                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                Python Interop Bridge                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Import      │  │ Type         │  │ Exception             │  │
│  │ Resolution  │  │ Marshaling   │  │ Handling              │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CPython Runtime                              │
│  import numpy as np                                              │
│  arr = np.array([1, 2, 3])                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Type Marshaling Table

| OwlLang Type   | Python Type   | Notes                            |
| -------------- | ------------- | -------------------------------- |
| `Int`          | `int`         | Arbitrary precision in Python    |
| `Float`        | `float`       | IEEE 754 double                  |
| `String`       | `str`         | UTF-8 encoded                    |
| `Bool`         | `bool`        | Direct mapping                   |
| `List[T]`      | `list`        | Converted element-by-element     |
| `Map[K, V]`    | `dict`        | Converted key-by-key             |
| `Option[T]`    | `T \| None`   | `Some(x)` → `x`, `None` → `None` |
| `Result[T, E]` | `T` or raises | `Err` becomes exception          |
| `Unit`         | `None`        | Function returns                 |

### Exception Bridge

```owl
// OwlLang code
try {
    let data = python_function()
} catch e: ValueError {
    handle_value_error(e)
} catch e: IOError {
    handle_io_error(e)
} catch e {
    handle_unknown(e)
}
```

Translates to:

```python
# Generated Python
try:
    data = python_function()
except ValueError as e:
    handle_value_error(e)
except IOError as e:
    handle_io_error(e)
except Exception as e:
    handle_unknown(e)
```

---

## Memory Model

### Immutability Implementation

```
┌──────────────────────────────────────────────────────┐
│                  Value Semantics                      │
│                                                       │
│  let x = [1, 2, 3]                                   │
│  let y = x         // y references same data          │
│  let z = y + [4]   // z is new list [1,2,3,4]        │
│                                                       │
│  Memory:                                              │
│  ┌─────────────────────────────────────────────┐     │
│  │ x, y ───→ [1, 2, 3] (immutable, shared)     │     │
│  │ z ──────→ [1, 2, 3, 4] (new allocation)     │     │
│  └─────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
```

### Copy-on-Write for Efficiency

```
┌──────────────────────────────────────────────────────┐
│              Copy-on-Write (COW)                      │
│                                                       │
│  let big_list = generate_million_items()             │
│  let copy = big_list  // No actual copy yet!         │
│                                                       │
│  // Only copies when mutation attempted:              │
│  var mutable = MutList(big_list)  // Copies here     │
│  mutable.append(new_item)                            │
└──────────────────────────────────────────────────────┘
```

---

## Concurrency Model

### No GIL Strategy

In transpiled Python mode, OwlLang uses:

1. **`multiprocessing`** for CPU-bound parallelism
2. **`asyncio`** for I/O-bound concurrency
3. **Message passing** (no shared mutable state)

```owl
// OwlLang concurrent code
let results = items
    |> parallel_map(process)
    |> await_all()
```

Generates:

```python
# Generated Python
import multiprocessing

with multiprocessing.Pool() as pool:
    results = pool.map(process, items)
```

### Future: OwlVM Without GIL

```
┌─────────────────────────────────────────────────────────────────┐
│                        OwlVM Runtime                             │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │  Thread 1  │  │  Thread 2  │  │  Thread 3  │   (No GIL!)    │
│  │            │  │            │  │            │                 │
│  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │                │
│  │ │ Stack  │ │  │ │ Stack  │ │  │ │ Stack  │ │                │
│  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │                │
│  └────────────┘  └────────────┘  └────────────┘                │
│         │               │               │                       │
│         └───────────────┼───────────────┘                       │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Shared Immutable Heap                    │  │
│  │  (All data immutable, no locks needed for reads)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Channel Message Queue                    │  │
│  │  (Typed, bounded, for inter-thread communication)        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
owl-project/
├── src/
│   ├── main.owl           # Entry point
│   ├── utils.owl          # Utility module
│   └── models/
│       ├── user.owl
│       └── order.owl
├── tests/
│   ├── test_utils.owl
│   └── test_models.owl
├── owl.toml               # Project configuration
└── .owl/
    └── cache/             # Compiled cache
        ├── main.py        # Transpiled Python
        └── main.owc       # Bytecode (future)
```

### owl.toml Configuration

```toml
[package]
name = "my-owl-project"
version = "0.1.0"
authors = ["Your Name <you@example.com>"]
owl-version = "0.1"

[dependencies]
owl-std = "0.1"

[python-dependencies]
numpy = ">=1.20"
pandas = ">=1.3"
requests = ">=2.25"

[build]
target = "python"  # python | bytecode | native
python-version = "3.10"
optimization = 2

[dev]
test-framework = "owl-test"
lint = true
format-on-save = true
```

---

## Compilation Pipeline

### Phase 1: Parse & Check

```
owl build src/main.owl

[1/4] Parsing... ✓
[2/4] Type checking... ✓
[3/4] Optimizing... ✓
[4/4] Generating Python... ✓

Output: .owl/cache/main.py
```

### Phase 2: Run

```
owl run src/main.owl

[Compiling] src/main.owl
[Running] python .owl/cache/main.py

Hello, World!
```

### Error Messages

```
owl build src/broken.owl

Error[E0001]: Type mismatch
  --> src/broken.owl:15:10
   |
15 |     let x: Int = "hello"
   |            ^^^   ^^^^^^^ expected Int, found String
   |
   = help: Try using Int.parse("hello") or change the type annotation

Error[E0002]: Unknown variable
  --> src/broken.owl:20:5
   |
20 |     print(undefined_var)
   |           ^^^^^^^^^^^^^ not found in this scope
   |
   = help: Did you mean 'defined_var'?

Failed with 2 errors
```

---

## Standard Library Modules

```
owl-std/
├── core/
│   ├── option.owl      # Option[T] type
│   ├── result.owl      # Result[T, E] type
│   ├── string.owl      # String utilities
│   └── collections.owl # List, Map, Set
├── io/
│   ├── file.owl        # File I/O
│   ├── path.owl        # Path manipulation
│   └── console.owl     # Terminal I/O
├── net/
│   ├── http.owl        # HTTP client
│   └── socket.owl      # Raw sockets
├── async/
│   ├── task.owl        # Async tasks
│   ├── channel.owl     # Channels
│   └── executor.owl    # Thread pool
├── json/
│   └── json.owl        # JSON parsing/generation
├── time/
│   ├── datetime.owl    # Date/time handling
│   └── duration.owl    # Time durations
└── math/
    ├── basic.owl       # Basic math
    └── random.owl      # Random numbers
```
