# Changelog

All notable changes to OwlLang will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1-alpha] - 2026-01-31

### Added
- **Multi-line comments** with `/** ... */` syntax
  - Can span multiple lines
  - Can contain any characters including `//`
  - Properly tracked line/column positions
- **Error code E0104**: Unterminated multi-line comment with helpful hint

### Improved
- Enhanced error messages with hints for unterminated strings
- Better diagnostic message for strings spanning multiple lines
- 6 new tests for multi-line comment behavior

### Technical
- No semantic changes to the language
- All 383 tests passing
- Zero breaking changes

## [0.1.0-alpha] - 2026-01-31

### 🎉 First Alpha Release

This is the first public alpha release of OwlLang. The core language is semantically
complete and ready for experimentation.

### Added

#### Core Language
- **Type system** with `Int`, `Float`, `String`, `Bool`, `Void`, `Any`
- **Option[T]** for nullable values with `Some(value)` and `None`
- **Result[T, E]** for error handling with `Ok(value)` and `Err(error)`
- **Pattern matching** with exhaustive `match` expressions
- **Error propagation** with the `?` operator
- **Implicit returns** — last expression is the return value
- **If expressions** — `if/else` returns a value

#### Functions
- Function declarations with `fn name(params) -> Type { body }`
- Type-annotated parameters
- Return type annotations
- Recursive function support

#### Python Interop
- `from python import module`
- `from python import module as alias`
- `from python import { name1, name2 } from module`

#### Diagnostics
- **Error codes** (E01xx-E05xx) for lexer, parser, type, and control flow errors
- **Warning codes** (W01xx-W04xx) for unused variables, dead code, style issues
- **Rich error messages** with source location, notes, and hints
- **Colored output** for terminal

#### CLI
- `owl compile <file.ow>` — Compile to Python
- `owl run <file.ow>` — Compile and execute
- `owl check <file.ow>` — Type check only
- `owl tokens <file.ow>` — Show lexer tokens (debug)
- `owl ast <file.ow>` — Show AST (debug)
- `--deny-warnings` / `-W` — Treat warnings as errors
- `--no-warnings` — Suppress warning output
- `--version` / `-v` — Show version

#### Testing
- 364 tests covering lexer, parser, typechecker, transpiler, and diagnostics
- Example files that serve as integration tests

### Known Limitations

- No generics beyond Option/Result
- No structs, classes, or enums
- No loops (while, for)
- No modules/imports between .ow files
- No LSP or IDE support
- Transpiles to Python (no native runtime)

---

## Future Releases

See [docs/ROADMAP.md](docs/ROADMAP.md) for planned features.
