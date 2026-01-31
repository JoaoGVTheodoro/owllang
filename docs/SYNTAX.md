# OwlLang Syntax Specification

## Table of Contents

1. [Hello World](#hello-world)
2. [Variables](#variables)
3. [Types](#types)
4. [Functions](#functions)
5. [Control Flow](#control-flow)
6. [Classes & Structs](#classes--structs)
7. [Pattern Matching](#pattern-matching)
8. [Error Handling](#error-handling)
9. [Concurrency](#concurrency)
10. [Python Interop](#python-interop)

---

## Hello World

```owl
// The simplest OwlLang program
fn main() {
    print("Hello, World! 🦉")
}
```

Or even simpler (script mode):

```owl
print("Hello, World! 🦉")
```

---

## Variables

### Immutable by Default

```owl
// Immutable binding (default)
let name = "OwlLang"
let age = 1
let pi = 3.14159

// Type annotations (optional but recommended)
let count: Int = 42
let message: String = "Hello"
let ratio: Float = 0.5

// Compile error - cannot reassign immutable
let x = 10
x = 20  // Error: Cannot reassign immutable variable 'x'
```

### Mutable Variables

```owl
// Mutable binding (explicit)
var counter = 0
counter = counter + 1  // OK

var name: String = "Owl"
name = "OwlLang"  // OK
```

### Constants (Compile-time)

```owl
// Compile-time constants
const MAX_SIZE: Int = 1024
const API_URL: String = "https://api.example.com"
const PI: Float = 3.14159265359
```

### Destructuring

```owl
// Tuple destructuring
let (x, y, z) = (1, 2, 3)

// List destructuring
let [first, second, ...rest] = [1, 2, 3, 4, 5]
// first = 1, second = 2, rest = [3, 4, 5]

// Record destructuring
let {name, age} = user
let {name: user_name, age: user_age} = user  // Rename
```

---

## Types

### Primitive Types

```owl
// Numeric types
let integer: Int = 42
let big_int: Int64 = 9_223_372_036_854_775_807
let float: Float = 3.14
let decimal: Decimal = 99.99d  // Precise decimal for money

// Text
let char: Char = 'A'
let string: String = "Hello, OwlLang"
let multiline: String = """
    This is a
    multiline string
"""

// Boolean
let flag: Bool = true

// Unit (like Python's None, but type-safe)
let nothing: Unit = ()
```

### Composite Types

```owl
// Option (nullable alternative)
let maybe_number: Option[Int] = Some(42)
let no_number: Option[Int] = None

// Result (error handling)
let success: Result[Int, String] = Ok(42)
let failure: Result[Int, String] = Err("Something went wrong")

// Lists (immutable by default)
let numbers: List[Int] = [1, 2, 3, 4, 5]
let empty: List[String] = []

// Mutable lists
let mut_list: MutList[Int] = MutList([1, 2, 3])

// Tuples
let pair: (Int, String) = (42, "answer")
let triple: (Int, Int, Int) = (1, 2, 3)

// Maps (immutable)
let scores: Map[String, Int] = {
    "Alice": 100,
    "Bob": 85,
    "Charlie": 92
}

// Sets
let unique: Set[Int] = {1, 2, 3, 4, 5}
```

### Type Aliases

```owl
type UserId = Int
type Email = String
type UserMap = Map[UserId, User]

// Newtype (distinct type, not just alias)
newtype Meters(Float)
newtype Feet(Float)

let height: Meters = Meters(1.8)
let wrong: Meters = Feet(6.0)  // Compile error!
```

### Generics

```owl
// Generic function
fn first[T](list: List[T]) -> Option[T] {
    match list {
        [] => None,
        [head, ...] => Some(head)
    }
}

// Generic struct
struct Pair[A, B] {
    first: A,
    second: B
}

// Constraints
fn sum[T: Numeric](values: List[T]) -> T {
    values.fold(T.zero, |acc, x| acc + x)
}
```

---

## Functions

### Basic Functions

```owl
// Simple function
fn greet(name: String) -> String {
    "Hello, {name}!"
}

// Multiple parameters
fn add(a: Int, b: Int) -> Int {
    a + b
}

// No return value
fn log(message: String) {
    print("[LOG] {message}")
}

// Single expression (implicit return)
fn double(x: Int) -> Int = x * 2

fn is_even(n: Int) -> Bool = n % 2 == 0
```

### Default Parameters

```owl
fn greet(name: String, greeting: String = "Hello") -> String {
    "{greeting}, {name}!"
}

greet("Alice")              // "Hello, Alice!"
greet("Bob", "Hi")          // "Hi, Bob!"
greet("Charlie", greeting: "Hey")  // Named argument
```

### Lambda Functions

```owl
// Full lambda syntax
let add = |a: Int, b: Int| -> Int { a + b }

// Inferred types
let double = |x| x * 2

// Placeholder syntax for simple lambdas
let numbers = [1, 2, 3, 4, 5]
let doubled = numbers.map(_ * 2)        // [2, 4, 6, 8, 10]
let evens = numbers.filter(_ % 2 == 0)  // [2, 4]

// Multi-line lambda
let process = |data| {
    let cleaned = data.trim()
    let parsed = parse(cleaned)
    validate(parsed)
}
```

### Higher-Order Functions

```owl
// Function as parameter
fn apply_twice[T](f: (T) -> T, value: T) -> T {
    f(f(value))
}

let result = apply_twice(|x| x + 1, 5)  // 7

// Function as return value
fn multiplier(factor: Int) -> (Int) -> Int {
    |x| x * factor
}

let triple = multiplier(3)
triple(4)  // 12
```

### Pipe Operator

```owl
// Chain operations naturally
let result = data
    |> parse()
    |> validate()
    |> transform()
    |> save()

// Equivalent to:
let result = save(transform(validate(parse(data))))

// With partial application
let processed = numbers
    |> filter(_ > 0)
    |> map(_ * 2)
    |> sum()
```

---

## Control Flow

### If Expressions

```owl
// If as expression (always returns a value)
let status = if age >= 18 {
    "adult"
} else {
    "minor"
}

// Multi-branch
let grade = if score >= 90 {
    "A"
} else if score >= 80 {
    "B"
} else if score >= 70 {
    "C"
} else {
    "F"
}

// One-liner (when simple)
let abs = if x >= 0 { x } else { -x }
```

### Loops

```owl
// For loop (iterating)
for item in items {
    print(item)
}

// With index
for (index, item) in items.enumerate() {
    print("{index}: {item}")
}

// Range
for i in 0..10 {
    print(i)  // 0 to 9
}

for i in 0..=10 {
    print(i)  // 0 to 10 (inclusive)
}

// While loop
var count = 0
while count < 10 {
    print(count)
    count += 1
}

// Loop (infinite, break to exit)
loop {
    let input = read_line()
    if input == "quit" {
        break
    }
    process(input)
}
```

### Loop Expressions

```owl
// Loops can return values
let first_even = loop {
    let n = next_number()
    if n % 2 == 0 {
        break n  // Returns n from the loop
    }
}

// For with collection
let doubled = for x in numbers {
    yield x * 2  // Generator-style
}
```

---

## Classes & Structs

### Structs (Data-first)

```owl
// Simple struct
struct Point {
    x: Float,
    y: Float
}

// Create instance
let origin = Point { x: 0.0, y: 0.0 }
let p = Point { x: 3.0, y: 4.0 }

// Access fields
print(p.x)  // 3.0

// Structs are immutable - create new with changes
let moved = p with { x: 5.0 }  // Point { x: 5.0, y: 4.0 }
```

### Methods on Structs

```owl
struct Point {
    x: Float,
    y: Float
}

impl Point {
    // Constructor
    fn new(x: Float, y: Float) -> Point {
        Point { x, y }
    }
    
    // Method
    fn distance_from_origin(self) -> Float {
        (self.x ** 2 + self.y ** 2).sqrt()
    }
    
    // Method that returns new instance
    fn translate(self, dx: Float, dy: Float) -> Point {
        Point { x: self.x + dx, y: self.y + dy }
    }
}

let p = Point.new(3.0, 4.0)
print(p.distance_from_origin())  // 5.0
let p2 = p.translate(1.0, 1.0)   // Point { x: 4.0, y: 5.0 }
```

### Classes (When you need mutability/inheritance)

```owl
class Animal {
    name: String
    var age: Int  // Mutable field
    
    fn new(name: String, age: Int) -> Animal {
        Animal { name, age }
    }
    
    fn speak(self) -> String {
        "..."
    }
    
    fn have_birthday(mut self) {
        self.age += 1
    }
}

class Dog extends Animal {
    breed: String
    
    fn new(name: String, age: Int, breed: String) -> Dog {
        Dog { 
            ...super.new(name, age),  // Inherit from parent
            breed 
        }
    }
    
    override fn speak(self) -> String {
        "Woof!"
    }
}

let dog = Dog.new("Rex", 3, "Labrador")
print(dog.speak())  // "Woof!"
```

### Traits (Interfaces)

```owl
trait Drawable {
    fn draw(self)
    
    // Default implementation
    fn draw_twice(self) {
        self.draw()
        self.draw()
    }
}

struct Circle {
    center: Point,
    radius: Float
}

impl Drawable for Circle {
    fn draw(self) {
        print("Drawing circle at ({self.center.x}, {self.center.y})")
    }
}

// Use trait as type constraint
fn render[T: Drawable](item: T) {
    item.draw()
}
```

### Enums (Algebraic Data Types)

```owl
// Simple enum
enum Color {
    Red,
    Green,
    Blue
}

// Enum with data
enum Shape {
    Circle(center: Point, radius: Float),
    Rectangle(top_left: Point, width: Float, height: Float),
    Triangle(p1: Point, p2: Point, p3: Point)
}

// Option is just an enum
enum Option[T] {
    Some(value: T),
    None
}

// Result is just an enum
enum Result[T, E] {
    Ok(value: T),
    Err(error: E)
}
```

---

## Pattern Matching

```owl
// Basic matching
fn describe(color: Color) -> String {
    match color {
        Color.Red => "The color of fire",
        Color.Green => "The color of nature",
        Color.Blue => "The color of sky"
    }
}

// Matching with destructuring
fn area(shape: Shape) -> Float {
    match shape {
        Shape.Circle(_, radius) => 3.14159 * radius ** 2,
        Shape.Rectangle(_, width, height) => width * height,
        Shape.Triangle(p1, p2, p3) => {
            // Calculate triangle area
            calculate_triangle_area(p1, p2, p3)
        }
    }
}

// Guards
fn classify(n: Int) -> String {
    match n {
        0 => "zero",
        x if x < 0 => "negative",
        x if x % 2 == 0 => "positive even",
        _ => "positive odd"
    }
}

// Option matching
fn greet_user(user: Option[User]) {
    match user {
        Some(u) => print("Hello, {u.name}!"),
        None => print("Hello, stranger!")
    }
}

// List patterns
fn describe_list[T](list: List[T]) -> String {
    match list {
        [] => "empty",
        [single] => "single element",
        [first, second] => "two elements",
        [first, ...rest] => "many elements, starting with {first}"
    }
}
```

---

## Error Handling

### Result Type

```owl
fn divide(a: Int, b: Int) -> Result[Int, String] {
    if b == 0 {
        Err("Division by zero")
    } else {
        Ok(a / b)
    }
}

// Handle result
match divide(10, 2) {
    Ok(result) => print("Result: {result}"),
    Err(error) => print("Error: {error}")
}

// Use ? operator for propagation
fn calculate(x: Int, y: Int) -> Result[Int, String] {
    let a = divide(x, y)?   // Returns early if Err
    let b = divide(a, 2)?
    Ok(b * 2)
}

// Combinators
let result = divide(10, 2)
    .map(|x| x * 2)
    .unwrap_or(0)
```

### Try-Catch (for Python interop)

```owl
// When calling Python code that might throw
try {
    let response = requests.get(url)
    process(response)
} catch e: HttpError {
    print("HTTP error: {e}")
} catch e: TimeoutError {
    print("Timeout: {e}")
} catch e {
    print("Unknown error: {e}")
}
```

---

## Concurrency

### Async/Await

```owl
// Async function
async fn fetch_data(url: String) -> Result[String, Error] {
    let response = await http.get(url)
    Ok(response.text())
}

// Use async
async fn main() {
    let data = await fetch_data("https://api.example.com")
    print(data)
}

// Parallel execution
async fn fetch_all(urls: List[String]) -> List[Result[String, Error]] {
    await parallel(urls.map(fetch_data))
}
```

### Channels

```owl
// Create channel
let (sender, receiver) = channel[Int]()

// Spawn task
spawn {
    for i in 0..10 {
        sender.send(i)
    }
    sender.close()
}

// Receive
for value in receiver {
    print("Received: {value}")
}
```

---

## Python Interop

### Importing Python Modules

```owl
// Import entire module
from python import numpy as np
from python import pandas as pd
from python import requests

// Import specific items
from python.json import loads, dumps
from python.os.path import exists, join

// Import with type hints
from python import numpy as np: {
    array: (List[Any]) -> NDArray,
    zeros: (shape: Tuple[Int, ...]) -> NDArray
}
```

### Using Python Libraries

```owl
// NumPy
from python import numpy as np

let arr = np.array([1, 2, 3, 4, 5])
let doubled = arr * 2
let mean = np.mean(arr)

print("Array: {arr}")
print("Mean: {mean}")
```

```owl
// Pandas
from python import pandas as pd

let df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["NYC", "LA", "Chicago"]
})

let adults = df[df["age"] >= 30]
print(adults)
```

```owl
// Requests
from python import requests

fn fetch_user(id: Int) -> Result[User, Error] {
    try {
        let response = requests.get("https://api.example.com/users/{id}")
        response.raise_for_status()
        Ok(response.json() as User)
    } catch e {
        Err(e)
    }
}
```

```owl
// Matplotlib
from python import matplotlib.pyplot as plt
from python import numpy as np

let x = np.linspace(0, 2 * np.pi, 100)
let y = np.sin(x)

plt.figure(figsize: (10, 6))
plt.plot(x, y, label: "sin(x)")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Sine Wave")
plt.legend()
plt.show()
```

### Calling Python Code

```owl
// Inline Python
let result = python {
    import sys
    print(f"Python version: {sys.version}")
    result = sum(range(100))
}
print("Sum: {result}")

// Python function as OwlLang function
@python_fn
fn calculate_complex(data: List[Float]) -> Float {
    """
    import numpy as np
    return np.std(data) * np.mean(data)
    """
}

let value = calculate_complex([1.0, 2.0, 3.0, 4.0, 5.0])
```

### Exposing OwlLang to Python

```owl
// Export function for Python to use
@export_python
fn owl_function(x: Int, y: Int) -> Int {
    x * y + 42
}
```

```python
# In Python
from owl_module import owl_function

result = owl_function(10, 20)  # 242
```
