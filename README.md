# OwlLang 🦉

> A modern programming language with full Python ecosystem compatibility

**OwlLang** is a statically-typed language that combines the safety of modern type systems with the power of Python's ecosystem. Write safer, cleaner code while using all your favorite Python libraries.

## Why OwlLang?

| Python Pain Point        | OwlLang Solution                |
| ------------------------ | ------------------------------- |
| Runtime type errors      | Compile-time type checking      |
| `None` can be anything   | `Option[T]` types               |
| Exceptions are invisible | `Result[T, E]` error handling   |
| Mutable by default       | Immutable by default            |
| GIL limits concurrency   | First-class async & parallelism |
| Indentation errors       | Explicit block syntax           |

## Quick Example

```owl
from python import pandas as pd
from python import requests

struct User {
    name: String,
    email: String,
    age: Int
}

fn fetch_users() -> Result[List[User], String] {
    try {
        let response = requests.get("https://api.example.com/users")
        let data = response.json()
        
        Ok(data.map(|u| User {
            name: u["name"],
            email: u["email"],
            age: u["age"]
        }))
    } catch e {
        Err("Failed to fetch users: {e}")
    }
}

fn main() {
    match fetch_users() {
        Ok(users) => {
            let df = pd.DataFrame(users)
            let adults = df[df["age"] >= 18]
            print("Adult users:\n{adults}")
        },
        Err(e) => print("Error: {e}")
    }
}
```

## Key Features

### 🔒 Type Safety

```owl
fn add(a: Int, b: Int) -> Int {
    a + b
}

add(1, 2)       // ✅ OK
add(1, "two")   // ❌ Compile error
```

### 📦 Option Types (No More Null)

```owl
fn find_user(id: Int) -> Option[User] {
    users.get(id)
}

// Must handle both cases
match find_user(42) {
    Some(user) => use(user),
    None => handle_missing()
}
```

### ⚡ Pipe Operator

```owl
let result = data
    |> filter(_ > 0)
    |> map(_ * 2)
    |> sorted()
    |> take(10)
```

### 🔗 Full Python Interop

```owl
from python import numpy as np
from python import matplotlib.pyplot as plt

let x = np.linspace(0, 2 * np.pi, 100)
let y = np.sin(x)

plt.plot(x, y)
plt.show()
```

### 🚀 Modern Concurrency

```owl
async fn fetch_all(urls: List[String]) -> List[Response] {
    await parallel(urls.map(fetch))
}
```

## Installation

```bash
# Coming soon!
curl -sSf https://install.owllang.dev | sh
```

## Documentation

- [Philosophy](docs/PHILOSOPHY.md) - Why OwlLang exists
- [Syntax Guide](docs/SYNTAX.md) - Complete language reference
- [Architecture](docs/ARCHITECTURE.md) - Technical details
- [Comparison with Python](docs/COMPARISON.md) - What's different
- [Roadmap](docs/ROADMAP.md) - Development timeline

## Examples

See the [examples/](examples/) directory:

- [Hello World](examples/01_hello_world.owl)
- [Variables & Types](examples/02_variables.owl)
- [Functions](examples/03_functions.owl)
- [Classes & Structs](examples/04_classes.owl)
- [Python Interop](examples/05_python_interop.owl)

## Project Status

🚧 **Phase 1: MVP** - Currently in development

We're building the core compiler and Python transpiler. See our [Roadmap](docs/ROADMAP.md) for details.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

OwlLang is open source under the [MIT License](LICENSE).

---

<p align="center">
  <i>🦉 "Wisdom comes from seeing clearly in the dark"</i>
</p>
