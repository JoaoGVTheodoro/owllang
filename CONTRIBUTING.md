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
- Translate documentation
- Write tutorials

### 🔧 Code Contributions

Ready to code? Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add tests
5. Run the test suite (`cargo test`)
6. Submit a pull request

## Development Setup

### Prerequisites

- Rust (latest stable)
- Python 3.10+
- Git

### Building

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/owl.git
cd owl

# Build
cargo build

# Run tests
cargo test

# Run the compiler
cargo run -- run examples/hello.owl
```

### Project Structure

```
owl/
├── src/
│   ├── lexer/        # Tokenization
│   ├── parser/       # AST generation
│   ├── typechecker/  # Type analysis
│   ├── codegen/      # Python transpiler
│   └── cli/          # Command-line interface
├── tests/            # Test suite
├── examples/         # Example programs
├── docs/             # Documentation
└── spec/             # Language specification
```

## Code Style

### Rust Code

- Follow `rustfmt` conventions
- Use `clippy` for linting
- Write doc comments for public APIs
- Keep functions small and focused

### OwlLang Code

- Use 4-space indentation
- Follow the examples in `examples/`
- Keep lines under 100 characters
- Add comments for complex logic

## Pull Request Guidelines

1. **One feature per PR** - Keep PRs focused
2. **Add tests** - All new features need tests
3. **Update docs** - If adding features, update documentation
4. **Write good commit messages** - Clear, descriptive messages
5. **Be patient** - Reviews may take time

### Commit Message Format

```
<type>: <short description>

<longer description if needed>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

Example:
```
feat: add pipe operator support

Implements the |> pipe operator for chaining function calls.
Adds parser support and transpiles to nested function calls in Python.
```

## Testing

### Running Tests

```bash
# All tests
cargo test

# Specific test
cargo test test_name

# With output
cargo test -- --nocapture
```

### Writing Tests

```rust
#[test]
fn test_parser_function_declaration() {
    let source = "fn add(a: Int, b: Int) -> Int { a + b }";
    let ast = parse(source).unwrap();
    
    assert!(matches!(ast[0], Stmt::FnDecl { .. }));
}
```

## Community

- **Discussions**: GitHub Discussions for questions and ideas
- **Issues**: GitHub Issues for bugs and feature requests
- **Chat**: Discord server (coming soon)

## Code of Conduct

Be respectful and inclusive. We're all here to learn and build something great together.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make OwlLang better! 🦉
