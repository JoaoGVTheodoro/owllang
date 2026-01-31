# OwlLang Compiler

A minimal compiler that transpiles OwlLang to Python.

## Quick Start

```bash
# Compile a .owl file to .py
python -m owl compile hello.owl

# Compile and run
python -m owl run hello.owl

# Show tokens (debug)
python -m owl tokens hello.owl

# Show AST (debug)
python -m owl ast hello.owl
```

## Example

**Input (hello.owl):**
```owl
from python import math

fn main() {
    let x = 10
    let y = 20
    print(x + y)
    print(math.sqrt(16.0))
}
```

**Output (hello.py):**
```python
import math

def main():
    x = 10
    y = 20
    print((x + y))
    print(math.sqrt(16.0))

if __name__ == "__main__":
    main()
```

## Running Tests

```bash
cd compiler
python tests/test_compiler.py
```

## Project Structure

```
compiler/
├── owl/
│   ├── __init__.py      # Package exports
│   ├── __main__.py      # CLI entry point
│   ├── ast_nodes.py     # Token and AST definitions
│   ├── lexer.py         # Tokenizer
│   ├── parser.py        # Parser (tokens → AST)
│   └── transpiler.py    # Transpiler (AST → Python)
├── tests/
│   ├── hello.owl        # Test file
│   └── test_compiler.py # Unit tests
└── README.md
```

## MVP Features

- ✅ `let` for immutable variables
- ✅ Literals: Int, Float, String, Bool
- ✅ Functions (`fn`)
- ✅ Function calls
- ✅ `print()`
- ✅ `from python import ...`
- ✅ Binary operators: `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- ✅ Comments (`//`)
