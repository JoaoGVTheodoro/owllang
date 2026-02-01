# Changelog

All notable changes to OwlLang will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4.2-alpha] - 2026-01-31

### Semantic Tightening & Transpiler Simplification

This release focuses on **internal consistency and code hygiene**, not new features.
It audits the codebase for dead code, redundancies, and documentation errors.

### Fixed
- **CHANGELOG documentation**: `range(a, b)` correctly documented as transpiling to `range(a, b)` 
  (was incorrectly documented as `list(range(a, b))`)

### Technical
- 566 tests passing
- Code audit: no dead code found in transpiler or typechecker
- Dual error system (`_error` + `_add_diagnostic`) documented as required for backward compatibility
- `TypeError` dataclass is legacy but required by test suite

### Design Notes
- This release validates the v0.2.x architecture is clean and well-documented
- Ready for v0.2.5-alpha (Structs) development

---

## [0.2.4.1-alpha] - 2026-01-31

### Conceptual Consolidation Release

This release focuses on **simplification and consistency**, not new features.
It treats all prior versions (v0.1.0 → v0.2.4) as a unified system and consolidates
the language design for clarity.

### Added
- **INVARIANTS.md**: New document defining the fundamental language invariants
  - Expression vs statement rules
  - Type system invariants
  - Mutability model
  - Control flow guarantees
  - Diagnostic code stability

### Improved
- **Diagnostic codes documentation**: Clear status for each warning code
  - ✅ Implemented warnings are marked
  - 📋 Reserved codes are documented for future implementation
- **STABILITY.md**: Updated for v0.2.x with complete feature list
- **README.md**: Updated version, test count, and feature summary

### Removed
- **W0302 TRIVIAL_IF**: Removed redundant warning code (superseded by W0306 CONSTANT_CONDITION)

### Technical
- 563 tests passing (unchanged from v0.2.4)
- Zero new features (consolidation only)
- Zero breaking changes
- Documentation now reflects unified v0.1→v0.2.4 design

### Design Notes
This release establishes the conceptual foundation for v0.2.5 (Structs):
- Language invariants are now explicit and documented
- Stability guarantees are clear and versioned
- Warning codes are properly categorized as implemented or reserved

---

## [0.2.4-alpha] - 2026-01-31

### Added
- **`loop` (infinite loop)**: Executes indefinitely until `break` or `return`
  ```owl
  loop {
      print("forever")
      if done {
          break
      }
  }
  ```
- **`range(start, end)` builtin**: Produces `List[Int]` from `start` to `end-1`
  ```owl
  for i in range(0, 5) {
      print(i)  // 0, 1, 2, 3, 4
  }
  ```
- **Warning W0204**: "`loop without exit`" when loop has no `break` or `return`

### Technical
- 563 tests passing (17 new tests for loop and range)
- `loop { }` transpiles to `while True:` in Python
- `range(a, b)` transpiles to `range(a, b)` in Python (lazy, supports indexing and iteration)
- `continue` works in `loop` as expected

### Design Notes
- `loop` is the canonical way to write intentional infinite loops
- Combined with `for-in`, completes the iteration model:
  - `for x in xs { }` — iterate over collection
  - `while cond { }` — conditional repetition  
  - `loop { }` — infinite (exit via break/return)
  - `range(a, b)` — numeric sequences for indexed iteration

---

## [0.2.3-alpha] - 2026-01-31

### Added
- **`for-in` loop**: Ergonomic iteration over lists
  ```owl
  for item in [1, 2, 3] {
      print(item)
  }
  ```
- **Syntactic sugar**: `for-in` is equivalent to index-based `while` loops but more readable
  ```owl
  // Before (v0.2.2)
  let mut i = 0
  while i < len(xs) {
      let x = get(xs, i)
      print(x)
      i = i + 1
  }
  
  // After (v0.2.3)
  for x in xs {
      print(x)
  }
  ```
- **Loop variable scoping**: `item` is scoped to the loop body and is immutable
- **Error E0507**: "`cannot iterate over type X`" when collection is not `List[T]`

### Technical
- 546 tests passing (19 new tests for for-in loops)
- `break` and `continue` work in for-in loops
- `return` works in for-in loops
- Transpiles directly to Python `for item in collection:` (no explicit indices)

### Design Notes
- `for-in` is a **statement** (like `while`), not an expression
- Loop variable is always **immutable** (cannot be reassigned inside loop)
- Semantics unchanged from v0.2.2 - just improved ergonomics

---

## [0.2.2-alpha] - 2026-01-31

### Added
- **`List[T]` type**: Typed lists for storing multiple values
  ```owl
  let xs: List[Int] = [1, 2, 3]
  let names = ["Alice", "Bob"]  // inferred as List[String]
  ```
- **List literals**: `[element1, element2, ...]` with trailing comma support
  ```owl
  let empty = []
  let nums = [1, 2, 3,]  // trailing comma allowed
  ```
- **Built-in function `len(list) -> Int`**: Returns the number of elements
  ```owl
  print(len([1, 2, 3]))  // 3
  ```
- **Built-in function `get(list, index) -> T`**: Returns element at index
  ```owl
  let xs = [10, 20, 30]
  print(get(xs, 1))  // 20
  ```
- **Built-in function `push(list, value) -> List[T]`**: Returns new list with value appended
  ```owl
  let xs = [1, 2]
  let ys = push(xs, 3)  // [1, 2, 3]
  // xs is still [1, 2] (immutable)
  ```
- **Built-in function `is_empty(list) -> Bool`**: Returns true if list is empty
  ```owl
  if is_empty([]) { print("empty") }
  ```

### Technical
- 527 tests passing (30 new tests for List[T])
- Lists are **immutable** - `push` returns a new list
- Type checking ensures **homogeneous** lists (all elements same type)
- Integration with `while` loops enables classic algorithms (sum, find, etc.)
- Transpiles directly to Python lists

### Design Notes
- `List[T]` enables practical programming with loops from v0.2.0/v0.2.1
- Lists use functional style: operations return new lists
- Empty list `[]` has type `List[Any]`, allowing assignment to any typed list

---

## [0.2.1-alpha] - 2026-01-31

### Added
- **`break` statement**: Exit the innermost loop immediately
  ```owl
  while true {
      if done {
          break
      }
  }
  ```
- **`continue` statement**: Skip to the next iteration of the innermost loop
  ```owl
  while i < 10 {
      i = i + 1
      if i % 2 == 0 {
          continue  // skip even numbers
      }
      print(i)
  }
  ```
- **Error E0505**: "`break` outside of loop" with helpful hint
- **Error E0506**: "`continue` outside of loop" with helpful hint

### Technical
- 497 tests passing (15 new tests for break/continue)
- New example: `examples/10_break_continue.ow`
- Loop context tracking in TypeChecker for proper validation

---

## [0.2.0-alpha] - 2026-01-31

### Added
- **`while` loops**: Iterative control flow for real algorithms
  ```owl
  let mut i = 10
  while i > 0 {
      print(i)
      i = i - 1
  }
  ```
- **`let mut` for mutable variables**: Local mutability with explicit opt-in
  ```owl
  let mut count = 0
  count = count + 1  // OK: count is mutable
  ```
- **Assignment statements**: `x = value` for mutable variables
- **Error E0323**: "cannot assign to immutable variable" with helpful hint
  ```
  error[E0323]: cannot assign to immutable variable `x`
    hint: consider declaring with `let mut x` to make it mutable
  ```

### Improved
- **Diagnostic codes in errors**: All type errors now show proper error codes (E0xxx)
- **Hints in error messages**: Error messages now display hints to help fix issues
- **New example**: `examples/09_while_loop.ow` demonstrating countdown and sum algorithms

### Technical
- 482 tests passing (added 17 v0.2.0 feature tests)
- **First release of 0.2.x line**: Focus on practical programming capabilities
- Design principle: "Capacidade vem antes de abstração" (capability before abstraction)

### Design Notes
- `while` is a **statement**, not an expression (cannot be used as value)
- Mutability does NOT propagate implicitly - each variable must be explicitly `let mut`
- Immutable by default preserves safety guarantees

## [0.1.6-alpha] - 2026-01-31

### Added
- **Stability contract**: `docs/STABILITY.md` defining what is stable, experimental, and internal
- **Contract regression tests**: 25 new tests verifying stability guarantees
  - CLI interface (5 tests)
  - Exit codes (4 tests)
  - JSON schema (6 tests)
  - Diagnostic codes (2 tests)
  - Language semantics (4 tests)
  - Determinism (2 tests)
  - Warning suppression (2 tests)

### Improved
- **INVARIANTS.md**: Added cross-reference to STABILITY.md
- **README.md**: Updated to v0.1.6-alpha, added link to stability contract
- **Documentation**: Clearer versioning policy and deprecation rules

### Technical
- 465 tests passing (added 25 stability contract tests)
- Zero language changes (stability freeze)
- Zero breaking changes
- **Final release of 0.1.x line**

## [0.1.5-alpha] - 2026-01-31

### Added
- **Directory support in CLI**: `owl check examples/` now checks all `.ow` files recursively
- **JSON output**: `owl check file.ow --json` outputs structured diagnostics for tooling integration
- **Explicit exit codes**:
  - `0` - Success
  - `1` - Compilation error
  - `2` - Warnings treated as errors (with `--deny-warnings` or `-W`)
- **CLI UX tests**: 24 new tests covering directory support, exit codes, JSON output, and output consistency

### Improved
- **Execution UX**: 
  - `owl compile` no longer generates output file on error
  - `owl run` shows clear error message before aborting
- **Output consistency**:
  - All diagnostics (errors/warnings) go to stderr
  - Program output and JSON go to stdout
  - Deterministic ordering of diagnostics by file and line
- **Compile safety**: Type check before generating output to prevent partial compilation

### Technical
- 440 tests passing (added 24 CLI UX tests)
- New file: `tests/test_cli_ux.py` with 6 test categories
- Zero language changes (tooling-only release)
- Zero breaking changes

## [0.1.4-alpha] - 2026-01-31

### Improved
- **Semantic consistency pass**: Comprehensive validation of semantic rules across the language
- **Diagnostic message normalization**: Type names in warnings now consistently use backticks
  - `Result value is ignored` → `` `Result` value is ignored ``
  - `Option value is ignored` → `` `Option` value is ignored ``
- **Hint consistency**: All hints now use backticks for code references (e.g., `` `match`/`?` operator ``)

### Added
- **Semantic consistency tests**: 20 new tests organized in 5 categories:
  - Expression vs Statement semantics (5 tests)
  - Return semantics (4 tests)
  - Scope and shadowing (5 tests)
  - Diagnostic consistency (3 tests)
  - Edge cases (3 tests)

### Technical
- All diagnostic messages follow consistent formatting patterns
- Warning hints use backticks uniformly for code elements
- 416 tests passing (added 20 semantic consistency tests)
- Zero new features (stabilization release)
- Zero breaking changes

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
