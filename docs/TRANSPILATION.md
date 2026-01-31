# OwlLang Transpilation Examples

This document shows how OwlLang code translates to Python.

## Basic Examples

### Hello World

**OwlLang:**
```owl
fn main() {
    print("Hello, World! 🦉")
}
```

**Generated Python:**
```python
def main():
    print("Hello, World! 🦉")

if __name__ == "__main__":
    main()
```

---

### Variables

**OwlLang:**
```owl
let name = "Alice"
let age: Int = 30
var counter = 0
const MAX_SIZE: Int = 100
```

**Generated Python:**
```python
from typing import Final

name: str = "Alice"  # Immutable (by convention)
age: int = 30
counter: int = 0  # Mutable
MAX_SIZE: Final[int] = 100
```

---

### Functions

**OwlLang:**
```owl
fn add(a: Int, b: Int) -> Int {
    a + b
}

fn greet(name: String, greeting: String = "Hello") -> String {
    "{greeting}, {name}!"
}
```

**Generated Python:**
```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"
```

---

### Option Types

**OwlLang:**
```owl
fn find_user(id: Int) -> Option[User] {
    if user_exists(id) {
        Some(get_user(id))
    } else {
        None
    }
}

match find_user(42) {
    Some(user) => print(user.name),
    None => print("Not found")
}
```

**Generated Python:**
```python
from typing import Optional
from owl_runtime import Some, NONE, match

def find_user(id: int) -> Optional[User]:
    if user_exists(id):
        return Some(get_user(id))
    else:
        return NONE

# Pattern matching (Python 3.10+)
match find_user(42):
    case Some(user):
        print(user.name)
    case _:
        print("Not found")
```

---

### Result Types

**OwlLang:**
```owl
fn divide(a: Int, b: Int) -> Result[Int, String] {
    if b == 0 {
        Err("Division by zero")
    } else {
        Ok(a / b)
    }
}

fn calculate(x: Int, y: Int) -> Result[Int, String] {
    let a = divide(x, y)?
    let b = divide(a, 2)?
    Ok(b * 10)
}
```

**Generated Python:**
```python
from owl_runtime import Ok, Err, Result, propagate_error

def divide(a: int, b: int) -> Result[int, str]:
    if b == 0:
        return Err("Division by zero")
    else:
        return Ok(a // b)

def calculate(x: int, y: int) -> Result[int, str]:
    a = propagate_error(divide(x, y))
    if isinstance(a, Err):
        return a
    a = a.value
    
    b = propagate_error(divide(a, 2))
    if isinstance(b, Err):
        return b
    b = b.value
    
    return Ok(b * 10)
```

---

### Structs

**OwlLang:**
```owl
struct Point {
    x: Float,
    y: Float
}

impl Point {
    fn new(x: Float, y: Float) -> Point {
        Point { x, y }
    }
    
    fn distance_from_origin(self) -> Float {
        (self.x ** 2 + self.y ** 2).sqrt()
    }
}

let p = Point.new(3.0, 4.0)
let moved = p with { x: 5.0 }
```

**Generated Python:**
```python
from dataclasses import dataclass, replace
import math

@dataclass(frozen=True)
class Point:
    x: float
    y: float
    
    @staticmethod
    def new(x: float, y: float) -> 'Point':
        return Point(x=x, y=y)
    
    def distance_from_origin(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

p = Point.new(3.0, 4.0)
moved = replace(p, x=5.0)
```

---

### Enums

**OwlLang:**
```owl
enum Shape {
    Circle(radius: Float),
    Rectangle(width: Float, height: Float)
}

fn area(shape: Shape) -> Float {
    match shape {
        Shape.Circle(r) => 3.14159 * r ** 2,
        Shape.Rectangle(w, h) => w * h
    }
}
```

**Generated Python:**
```python
from dataclasses import dataclass
from typing import Union

@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

Shape = Union[Circle, Rectangle]

def area(shape: Shape) -> float:
    match shape:
        case Circle(radius=r):
            return 3.14159 * r ** 2
        case Rectangle(width=w, height=h):
            return w * h
```

---

### Pipe Operator

**OwlLang:**
```owl
let result = data
    |> filter(_ > 0)
    |> map(_ * 2)
    |> sorted()
    |> take(10)
```

**Generated Python:**
```python
from itertools import islice

result = list(islice(
    sorted(
        map(lambda x: x * 2,
            filter(lambda x: x > 0, data))),
    10))

# Or using owl_runtime pipe helper:
from owl_runtime import pipe

result = pipe(data,
    lambda d: filter(lambda x: x > 0, d),
    lambda d: map(lambda x: x * 2, d),
    sorted,
    lambda d: list(islice(d, 10))
)
```

---

### Async/Await

**OwlLang:**
```owl
async fn fetch_data(url: String) -> Result[String, Error] {
    try {
        let response = await http.get(url)
        Ok(response.text())
    } catch e {
        Err(e)
    }
}

async fn fetch_all(urls: List[String]) -> List[Result[String, Error]] {
    await parallel(urls.map(fetch_data))
}
```

**Generated Python:**
```python
import asyncio
import aiohttp

async def fetch_data(url: str) -> Result[str, Exception]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return Ok(await response.text())
    except Exception as e:
        return Err(e)

async def fetch_all(urls: list[str]) -> list[Result[str, Exception]]:
    return await asyncio.gather(*[fetch_data(url) for url in urls])
```

---

### Pattern Matching

**OwlLang:**
```owl
fn describe(list: List[Int]) -> String {
    match list {
        [] => "empty",
        [single] => "one element: {single}",
        [first, second] => "two elements",
        [first, ...rest] => "starts with {first}, {rest.len()} more"
    }
}
```

**Generated Python:**
```python
def describe(lst: list[int]) -> str:
    match lst:
        case []:
            return "empty"
        case [single]:
            return f"one element: {single}"
        case [first, second]:
            return "two elements"
        case [first, *rest]:
            return f"starts with {first}, {len(rest)} more"
```

---

### Python Interop

**OwlLang:**
```owl
from python import numpy as np
from python import pandas as pd

let arr = np.array([1, 2, 3, 4, 5])
let mean = np.mean(arr)

let df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30]
})
let adults = df[df["age"] >= 30]
```

**Generated Python:**
```python
import numpy as np
import pandas as pd

arr = np.array([1, 2, 3, 4, 5])
mean = np.mean(arr)

df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30]
})
adults = df[df["age"] >= 30]
```

---

## OwlLang Runtime Library

The transpiler generates code that may depend on a small runtime library:

```python
# owl_runtime.py

from typing import TypeVar, Generic, Optional, Callable, Any
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Some(Generic[T]):
    value: T
    
    def unwrap(self) -> T:
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        return self.value
    
    def map(self, f: Callable[[T], Any]) -> 'Option':
        return Some(f(self.value))

class _None:
    def unwrap(self):
        raise ValueError("Called unwrap on None")
    
    def unwrap_or(self, default):
        return default
    
    def map(self, f):
        return NONE

NONE = _None()
Option = Some | _None

@dataclass
class Ok(Generic[T]):
    value: T
    
    def is_ok(self) -> bool:
        return True
    
    def is_err(self) -> bool:
        return False
    
    def unwrap(self) -> T:
        return self.value

@dataclass  
class Err(Generic[E]):
    error: E
    
    def is_ok(self) -> bool:
        return False
    
    def is_err(self) -> bool:
        return True
    
    def unwrap(self):
        raise ValueError(f"Called unwrap on Err: {self.error}")

Result = Ok | Err

def pipe(value, *funcs):
    """Pipe operator implementation"""
    for f in funcs:
        value = f(value)
    return value
```
