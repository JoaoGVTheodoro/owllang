# Changelog

All notable changes to OwlLang will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3-alpha] - 2026-01-31

### Improved
- **Error recovery in parser**: Parser now uses synchronization to recover from syntax errors and continue parsing, reducing cascading errors
- **Diagnostic deduplication**: TypeChecker prevents duplicate errors and warnings at the same location with the same message
- **Precise error spans**: Match expression errors (exhaustiveness, invalid patterns) now use structured diagnostics with accurate source locations
- **Return and condition errors**: Refined error messages for return type mismatches and non-boolean conditions

### Added
- **Error code E0504**: Invalid pattern in match expression
- **Robustness tests**: 7 new tests verifying error deduplication, span precision, and error recovery behavior

### Technical
- Parser accumulates errors and synchronizes at safe tokens (fn, let, return, if, })
- TypeChecker tracks reported diagnostics by (code, line, column, message) to avoid duplicates
- Warnings without spans are not deduplicated (allows multiple unreachable code warnings)
- 396 tests passing (added 7 robustness tests)
- Zero breaking changes

## [0.1.2-alpha] - 2026-01-31

### Added
- **Warning W0304**: Result value is ignored
  - Warns when calling a function that returns `Result[T, E]` without handling the result
  - Suggests using `let _ = ...` to explicitly ignore or handling with match/`?` operator
- **Warning W0305**: Option value is ignored
  - Warns when calling a function that returns `Option[T]` without handling the value
  - Suggests using `let _ = ...` to explicitly ignore or handling with match
- **Warning W0306**: Constant condition detected
  - Warns when using `if true { ... }` or `if false { ... }`
  - Helps identify unreachable code or debugging leftovers

### Improved
- Better detection of ignored values in expression statements
- Implicit returns are correctly excluded from ignored value warnings

### Technical
- 6 new tests for static analysis warnings
- All 389 tests passing
- Zero breaking changes

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
