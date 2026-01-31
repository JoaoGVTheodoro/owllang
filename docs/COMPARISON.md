# OwlLang vs Python: Comparison

## Quick Overview

| Aspect               | Python                     | OwlLang                            |
| -------------------- | -------------------------- | ---------------------------------- |
| **Typing**           | Optional (type hints)      | Gradual, first-class               |
| **Mutability**       | Mutable by default         | Immutable by default               |
| **Null handling**    | `None` (nullable anything) | `Option[T]` types                  |
| **Error handling**   | Exceptions                 | `Result[T, E]` + exceptions        |
| **Blocks**           | Indentation only           | Braces `{}` + optional indentation |
| **Concurrency**      | GIL-limited                | First-class async, channels        |
| **Pattern matching** | `match` (3.10+)            | Full ADT matching                  |
| **Ecosystem**        | Native                     | Full Python compatibility          |

---

## What OwlLang Does EQUAL to Python

### 1. Python Library Access

```owl
// OwlLang
from python import pandas as pd
let df = pd.DataFrame({"a": [1, 2, 3]})
```

```python
# Python
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3]})
```

**Result:** Identical behavior, same libraries, same output.

---

### 2. Basic Operations

```owl
// OwlLang
let x = 10
let y = 20
let sum = x + y
let message = "Hello, World!"
let items = [1, 2, 3, 4, 5]
```

```python
# Python
x = 10
y = 20
sum = x + y
message = "Hello, World!"
items = [1, 2, 3, 4, 5]
```

---

### 3. Functions

```owl
// OwlLang
fn greet(name: String) -> String {
    "Hello, {name}!"
}
```

```python
# Python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

---

### 4. Classes

```owl
// OwlLang
class Person {
    name: String
    age: Int
    
    fn new(name: String, age: Int) -> Person {
        Person { name, age }
    }
    
    fn greet(self) -> String {
        "Hi, I'm {self.name}"
    }
}
```

```python
# Python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def greet(self) -> str:
        return f"Hi, I'm {self.name}"
```

---

## What OwlLang Does BETTER than Python

### 1. Type Safety

```owl
// OwlLang - Compile-time type checking
fn add(a: Int, b: Int) -> Int {
    a + b
}

add(1, 2)        // ✅ OK
add(1, "two")    // ❌ Compile error!
```

```python
# Python - Runtime error
def add(a: int, b: int) -> int:
    return a + b

add(1, 2)        # ✅ OK
add(1, "two")    # ❌ Runtime TypeError
```

**Advantage:** OwlLang catches type errors before running.

---

### 2. Null Safety with Option Types

```owl
// OwlLang - Null is impossible
fn find_user(id: Int) -> Option[User] {
    if user_exists(id) {
        Some(get_user(id))
    } else {
        None
    }
}

// Must handle both cases
match find_user(42) {
    Some(user) => use(user),
    None => handle_missing()
}

// Safe access
let name = find_user(42).map(_.name).unwrap_or("Unknown")
```

```python
# Python - None can sneak in anywhere
def find_user(id: int) -> User | None:
    if user_exists(id):
        return get_user(id)
    return None

user = find_user(42)
# Can crash if you forget to check
print(user.name)  # AttributeError if None!
```

**Advantage:** OwlLang makes null checks mandatory.

---

### 3. Immutability by Default

```owl
// OwlLang
let x = 10
x = 20        // ❌ Compile error!

var y = 10    // Explicitly mutable
y = 20        // ✅ OK

let list = [1, 2, 3]
list.append(4)  // ❌ Error - immutable

let new_list = list + [4]  // ✅ Creates new list
```

```python
# Python - Everything is mutable
x = 10
x = 20  # ✅ OK (no protection)

list = [1, 2, 3]
list.append(4)  # ✅ Mutates in place (can cause bugs)
```

**Advantage:** OwlLang prevents accidental mutations.

---

### 4. Pattern Matching (More Powerful)

```owl
// OwlLang - Full pattern matching
enum Result[T, E] {
    Ok(value: T),
    Err(error: E)
}

fn describe(result: Result[Int, String]) -> String {
    match result {
        Ok(0) => "zero",
        Ok(n) if n > 0 => "positive: {n}",
        Ok(n) => "negative: {n}",
        Err(e) => "error: {e}"
    }
}

// List patterns
match items {
    [] => "empty",
    [single] => "one item: {single}",
    [first, second] => "two items",
    [first, ...rest] => "starts with {first}, {rest.len()} more"
}
```

```python
# Python 3.10+ - Limited pattern matching
match result:
    case Ok(0):
        return "zero"
    case Ok(n) if n > 0:
        return f"positive: {n}"
    case Ok(n):
        return f"negative: {n}"
    case Err(e):
        return f"error: {e}"

# List patterns more verbose
match items:
    case []:
        return "empty"
    case [single]:
        return f"one item: {single}"
    case [first, second]:
        return "two items"
    case [first, *rest]:
        return f"starts with {first}, {len(rest)} more"
```

**Advantage:** OwlLang has more consistent, expressive patterns.

---

### 5. Pipe Operator

```owl
// OwlLang - Clean data pipelines
let result = data
    |> filter(_ > 0)
    |> map(_ * 2)
    |> filter(_ < 100)
    |> sorted()
    |> take(10)
```

```python
# Python - Nested or broken into steps
# Option 1: Nested (hard to read)
result = list(itertools.islice(
    sorted(
        filter(lambda x: x < 100,
            map(lambda x: x * 2,
                filter(lambda x: x > 0, data)))),
    10))

# Option 2: Many intermediate variables
filtered = filter(lambda x: x > 0, data)
doubled = map(lambda x: x * 2, filtered)
under_100 = filter(lambda x: x < 100, doubled)
sorted_items = sorted(under_100)
result = list(itertools.islice(sorted_items, 10))
```

**Advantage:** OwlLang reads left-to-right, top-to-bottom.

---

### 6. Error Handling with Result Types

```owl
// OwlLang - Errors are values
fn divide(a: Int, b: Int) -> Result[Int, String] {
    if b == 0 {
        Err("Division by zero")
    } else {
        Ok(a / b)
    }
}

// Propagate errors with ?
fn calculate(x: Int, y: Int) -> Result[Int, String] {
    let a = divide(x, y)?     // Returns early if Err
    let b = divide(a, 2)?
    Ok(b * 10)
}

// Chain operations
let result = divide(10, 2)
    .and_then(|x| divide(x, 2))
    .map(|x| x * 10)
    .unwrap_or(0)
```

```python
# Python - Exceptions can be missed
def divide(a: int, b: int) -> int:
    if b == 0:
        raise ValueError("Division by zero")
    return a // b

def calculate(x: int, y: int) -> int:
    a = divide(x, y)  # Can throw!
    b = divide(a, 2)  # Can throw!
    return b * 10

# Must wrap in try/except
try:
    result = calculate(10, 0)
except ValueError as e:
    result = 0
```

**Advantage:** OwlLang makes error handling explicit in types.

---

### 7. Block Syntax (No Indentation Errors)

```owl
// OwlLang - Braces are clear
fn process(items: List[Int]) -> Int {
    let filtered = items.filter(_ > 0)
    let mapped = filtered.map(_ * 2)
    mapped.sum()
}

// Multi-line strings don't affect logic
let sql = """
    SELECT *
    FROM users
    WHERE active = true
"""
```

```python
# Python - Indentation can cause subtle bugs
def process(items: list[int]) -> int:
    filtered = [x for x in items if x > 0]
    mapped = [x * 2 for x in filtered]  # Tab vs spaces?
    return sum(mapped)  # Wrong indent = different logic!

# Mixing tabs and spaces causes errors
def buggy():
    x = 1
	y = 2  # TabError!
```

**Advantage:** OwlLang blocks are explicit, no invisible errors.

---

### 8. Concurrency Model

```owl
// OwlLang - Channels and actors
let (tx, rx) = channel[Int]()

spawn {
    for i in 0..10 {
        tx.send(i)
    }
    tx.close()
}

for value in rx {
    process(value)
}

// Parallel map
let results = urls
    |> parallel_map(fetch)
    |> await_all()
```

```python
# Python - GIL limits true parallelism
import asyncio
import multiprocessing

async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)

# For CPU-bound, need multiprocessing (complex)
with multiprocessing.Pool() as pool:
    results = pool.map(process, data)
```

**Advantage:** OwlLang has built-in, GIL-free concurrency.

---

## What OwlLang Does DIFFERENTLY

### 1. Explicit Mutability

```owl
// OwlLang - Mutable methods marked
impl Counter {
    fn increment(mut self) {  // 'mut' makes intent clear
        self.count += 1
    }
}
```

```python
# Python - Everything can mutate self
class Counter:
    def increment(self):  # No indication of mutation
        self.count += 1
```

---

### 2. Struct vs Class Distinction

```owl
// OwlLang - Data (struct) vs Behavior (class)
struct Point { x: Float, y: Float }  // Immutable data

class Canvas { var pixels: Array[Color] }  // Mutable state
```

```python
# Python - @dataclass is an afterthought
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

class Canvas:
    def __init__(self):
        self.pixels = []
```

---

### 3. Python Imports Are Explicit

```owl
// OwlLang - Python imports clearly marked
from python import numpy as np       // From Python
from owl.math import sin, cos        // From OwlLang
```

```python
# Python - No distinction
import numpy as np
from math import sin, cos
```

---

### 4. String Interpolation

```owl
// OwlLang - Simple, consistent
let name = "World"
let greeting = "Hello, {name}!"
let math = "2 + 2 = {2 + 2}"
```

```python
# Python - Multiple ways
name = "World"
greeting = f"Hello, {name}!"      # f-strings
greeting = "Hello, {}!".format(name)  # .format()
greeting = "Hello, %s!" % name    # %-formatting
```

---

## Migration Path

### Python to OwlLang (Gradual)

1. **Week 1:** Use OwlLang for new modules, import existing Python
2. **Month 1:** Add type hints, convert simple modules
3. **Month 3:** Convert core business logic
4. **Ongoing:** Keep Python for ecosystem-specific code

```owl
// Gradual migration example
from python import legacy_module  // Keep old Python

// New code in OwlLang
fn new_feature(data: Data) -> Result[Output, Error] {
    let processed = legacy_module.process(data)
    validate(processed)?
    Ok(transform(processed))
}
```

---

## Summary

| If you want...                        | Use...                        |
| ------------------------------------- | ----------------------------- |
| Quick scripts, prototyping            | Python                        |
| Type safety, fewer runtime errors     | OwlLang                       |
| Existing ecosystem (ML, data science) | Both (OwlLang calling Python) |
| Large team, maintainable code         | OwlLang                       |
| Maximum flexibility                   | Python                        |
| Explicit error handling               | OwlLang                       |
| Concurrency without GIL               | OwlLang                       |

**OwlLang is not a Python replacement—it's a Python enhancement.** Use them together.
