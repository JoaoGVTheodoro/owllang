# Contributing to OwlLang

Thank you for your interest in contributing to OwlLang! 🦉

## Ways to Contribute

### 🐛 Bug Reports

Found a bug? Please open an issue with:

1. OwlLang version (`owl --version`)
2. Operating system
3. Minimal code example that reproduces the issue
4. Expected vs actual behavior
5. Error message (if any)

### 💡 Feature Requests

Have an idea? Open an issue with:

1. Clear description of the feature
2. Use cases (why is this useful?)
3. Proposed syntax (if applicable)
4. Examples of how it would work

### 📖 Documentation

Help improve our docs:

- Fix typos or unclear explanations
- Add examples
- Write tutorials

### 🔧 Code Contributions

Ready to code? Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add tests
5. Run the test suite (`pytest`)
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.10+
- pip
- Git

### Building

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/owl-lang.git
cd owl-lang

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e "./compiler[dev]"

# Run tests
pytest compiler/tests

# Run the compiler
owl run examples/00_hello_world.ow
```

### Project Structure

```
owl-lang/
├── compiler/
│   └── src/owllang/
│       ├── lexer/        # Tokenization
│       ├── parser/       # AST generation  
│       ├── typechecker/  # Type checking
│       ├── transpiler/   # Python code generation
│       ├── diagnostics/  # Errors and warnings
│       └── cli.py        # Command-line interface
├── examples/             # Example programs
├── docs/                 # Documentation
└── spec/                 # Language specification
```

## Code Style

### Python Code

- Follow PEP 8
- Use type hints
- Keep functions small and focused
- Write docstrings for public APIs

### OwlLang Code (Examples)

- Use 4-space indentation
- Keep lines under 100 characters
- Add comments explaining the example

## Pull Request Guidelines

1. **One feature per PR** - Keep PRs focused
2. **Add tests** - All new features need tests
3. **Update docs** - If adding features, update documentation
4. **Write good commit messages** - Clear, descriptive messages

### Commit Message Format

```
<type>: <short description>

<longer description if needed>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Example:
```
feat: add for-in loop support

Implements iteration over List[T] with for-in syntax.
Adds parser support and transpiles to Python for loop.
```

## Testing

### Running Tests

```bash
# All tests
pytest compiler/tests

# Specific test file
pytest compiler/tests/test_typechecker.py

# With verbose output
pytest compiler/tests -v

# Stop on first failure
pytest compiler/tests -x
```

### Writing Tests

```python
def test_parser_function_declaration():
    source = "fn add(a: Int, b: Int) -> Int { a + b }"
    result = compile_source(source)
    assert "def add(a: int, b: int) -> int:" in result
```

## Architecture

See [docs/COMPILER.md](docs/COMPILER.md) for compiler internals.

Key concepts:
- **Lexer**: Characters → Tokens
- **Parser**: Tokens → AST
- **TypeChecker**: AST → Errors/Warnings
- **Transpiler**: AST → Python

## Questions?

- Open an issue for questions
- Check existing issues for answers
- Read the documentation

Thank you for contributing! 🦉
