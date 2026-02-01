# OwlLang Roadmap

This document outlines the planned development of OwlLang.

---

## Philosophy

| Series    | Theme                                            |
| --------- | ------------------------------------------------ |
| **0.1.x** | Correct language — solid types, diagnostics, CLI |
| **0.2.x** | Useful language — loops, lists, real programs    |
| **0.3.x** | Expressive language — methods, enums, closures   |
| **0.4.x** | Powerful language — generics, traits, modules    |

---

## Series 0.2.x — Practical Programming

> **Goal:** Enable writing real algorithms — sorting, searching, data processing.

### v0.2.0-alpha — While Loop + Mutability ✅ COMPLETE

**Adds:** `while` loop and `let mut` for local mutability.

```owl
fn countdown(n: Int) -> Void {
    let mut i = n
    while i > 0 {
        print(i)
        i = i - 1
    }
    print("Liftoff!")
}
```

**What becomes possible:**
- Counters and countdowns
- Iterative algorithms
- Input loops

**Scope:**
- Lexer: `while`, `mut` keywords ✅
- Parser: `WhileStmt`, mutability in `LetStmt` ✅
- TypeChecker: condition must be `Bool`, track mutability ✅
- Transpiler: `while condition:` ✅
- New error: E0323 "cannot assign to immutable variable" ✅
- 17 new tests, 482 total passing

---

### v0.2.1-alpha — Break and Continue

**Adds:** `break` and `continue` statements.

```owl
fn find_first_negative(numbers: List[Int]) -> Option[Int] {
    let mut i = 0
    while i < len(numbers) {
        let n = get(numbers, i)
        if n < 0 {
            return Some(n)
        }
        i = i + 1
    }
    None
}
```

**What becomes possible:**
- Early exit from loops
- Skip iterations
- Search with short-circuit

**Scope:**
- Lexer: `break`, `continue` keywords
- Parser: `BreakStmt`, `ContinueStmt`
- TypeChecker: must be inside loop
- New errors: E0602 "break outside of loop", E0603 "continue outside of loop"

---

### v0.2.2-alpha — Lists

**Adds:** `List[T]` type with basic operations.

```owl
fn sum_all(numbers: List[Int]) -> Int {
    let mut total = 0
    let mut i = 0
    while i < len(numbers) {
        total = total + get(numbers, i)
        i = i + 1
    }
    total
}

fn main() {
    let nums = [1, 2, 3, 4, 5]
    print(sum_all(nums))  // 15
}
```

**Built-in operations:**
| Function   | Signature               | Description                           |
| ---------- | ----------------------- | ------------------------------------- |
| `len`      | `List[T] -> Int`        | Length of list                        |
| `get`      | `List[T], Int -> T`     | Get element (panics if out of bounds) |
| `push`     | `List[T], T -> List[T]` | Append element (returns new list)     |
| `is_empty` | `List[T] -> Bool`       | Check if empty                        |

**What becomes possible:**
- Sum, average, min/max
- Linear search
- Manual filtering
- Data processing

**Scope:**
- Lexer: `[`, `]` for list literals
- Parser: `ListLiteral` node
- TypeChecker: infer element type, verify homogeneity
- Built-in functions in runtime

---

### v0.2.3-alpha — For Loop

**Adds:** `for item in collection` loop.

```owl
fn sum_all(numbers: List[Int]) -> Int {
    let mut total = 0
    for n in numbers {
        total = total + n
    }
    total
}

fn find_negative(numbers: List[Int]) -> Option[Int] {
    for n in numbers {
        if n < 0 {
            return Some(n)
        }
    }
    None
}
```

**What becomes possible:**
- Idiomatic iteration
- Cleaner code, fewer index errors
- Familiar patterns for Python/JS developers

**Scope:**
- Parser: `ForStmt` with pattern and iterable
- TypeChecker: iterable must be `List[T]`, bind item as `T`
- Transpiler: `for item in collection:`
- `break`/`continue` work inside `for`

---

### v0.2.4-alpha — Infinite Loop and Ranges

**Adds:** `loop` (infinite) and `range(start, end)`.

```owl
fn read_until_quit() -> List[String] {
    let mut inputs: List[String] = []
    loop {
        let input = read_line()
        if input == "quit" {
            break
        }
        inputs = push(inputs, input)
    }
    inputs
}

fn factorial(n: Int) -> Int {
    let mut result = 1
    for i in range(1, n + 1) {
        result = result * i
    }
    result
}
```

**What becomes possible:**
- Event/input loops
- Simple servers
- Numeric algorithms (factorial, fibonacci)
- Game loops

**Scope:**
- Parser: `LoopStmt` (no condition)
- Built-in: `range(start, end) -> List[Int]`
- Warning: W0401 "loop without break or return"

---

### v0.2.5-alpha — Structs

**Adds:** User-defined composite types.

```owl
struct Point {
    x: Float,
    y: Float
}

fn distance(p1: Point, p2: Point) -> Float {
    let dx = p2.x - p1.x
    let dy = p2.y - p1.y
    sqrt(dx * dx + dy * dy)
}

fn main() {
    let points = [
        Point { x: 0.0, y: 0.0 },
        Point { x: 3.0, y: 4.0 }
    ]
    for p in points {
        print(p.x)
    }
}
```

**What becomes possible:**
- Entity representation (User, Product, Config)
- Domain modeling
- Structured return values
- Data grouping

**Scope:**
- Parser: `StructDecl`, `StructLiteral`
- TypeChecker: type registry, field verification
- Transpiler: Python `@dataclass`
- No methods yet (free functions only)

---

### v0.2.6-alpha — Polish and Stabilization

**Focus:** Consistency, edge cases, documentation.

- Refined error messages for new features
- Integration tests for complete programs
- Updated examples
- STABILITY.md updated for 0.2.x
- Performance pass on large lists

---

## Summary Table

| Release | Feature              | New Capability              |
| ------- | -------------------- | --------------------------- |
| 0.2.0   | `while` + `let mut`  | Basic iterative loops       |
| 0.2.1   | `break` / `continue` | Early exit, skip iterations |
| 0.2.2   | `List[T]`            | Collection processing       |
| 0.2.3   | `for in`             | Idiomatic iteration         |
| 0.2.4   | `loop` + `range`     | Event loops, sequences      |
| 0.2.5   | `struct`             | Data modeling               |
| 0.2.6   | Polish               | Production confidence       |

---

## Validation Program

At the end of 0.2.x, this program must compile and run:

```owl
struct Stats {
    min: Int,
    max: Int,
    sum: Int
}

fn bubble_sort(items: List[Int]) -> List[Int] {
    let mut arr = items
    let n = len(arr)
    let mut i = 0
    while i < n {
        let mut j = 0
        while j < n - i - 1 {
            let a = get(arr, j)
            let b = get(arr, j + 1)
            if a > b {
                arr = swap(arr, j, j + 1)
            }
            j = j + 1
        }
        i = i + 1
    }
    arr
}

fn compute_stats(numbers: List[Int]) -> Stats {
    let mut min_val = get(numbers, 0)
    let mut max_val = get(numbers, 0)
    let mut sum = 0
    
    for n in numbers {
        if n < min_val { min_val = n }
        if n > max_val { max_val = n }
        sum = sum + n
    }
    
    Stats { min: min_val, max: max_val, sum: sum }
}

fn main() {
    let data = [5, 2, 8, 1, 9, 3]
    let sorted = bubble_sort(data)
    let stats = compute_stats(sorted)
    
    print("Min: " + stats.min)
    print("Max: " + stats.max)
    print("Sum: " + stats.sum)
}
```

---

## What's NOT in 0.2.x

| Feature                     | Reason                      | Planned |
| --------------------------- | --------------------------- | ------- |
| Methods (`impl`)            | Requires stable structs     | 0.3.0   |
| Custom enums                | Needs generics to be useful | 0.3.x   |
| Generics                    | Requires mature type system | 0.3.x   |
| Traits                      | Requires generics           | 0.4.x   |
| Closures/lambdas            | Capture complexity          | 0.3.x   |
| Pattern matching on structs | Requires stable structs     | 0.3.x   |
| Field mutability            | Complex design              | 0.3.x   |

---

## Future Series (Tentative)

### 0.3.x — Expressiveness
- Methods on structs (`impl`)
- Custom enums with variants
- Closures and lambdas
- Pattern matching on structs
- Map/filter/reduce

### 0.4.x — Abstraction
- Generics for structs and functions
- Traits (interfaces)
- Trait bounds
- Standard traits: `Display`, `Eq`, `Hash`

### 0.5.x — Organization
- Modules and namespaces
- Visibility (pub/private)
- Multi-file projects
- Package structure

### 1.0.x — Production
- LSP / IDE support
- Documentation generator
- Package manager integration
- Backward compatibility guarantees

---

## Design Principles

1. **Immutable by default** — `let mut` is explicit opt-in
2. **No inheritance** — Composition and traits only
3. **Exhaustive matching** — All cases must be handled
4. **Python interop** — Clean transpilation, dataclasses, etc.
5. **Incremental releases** — Each release is independently usable

---

*Last updated: v0.1.6-alpha (January 2026)*
