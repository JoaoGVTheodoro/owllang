# OwlLang Examples

These examples demonstrate OwlLang features progressively.

## Examples

| File                   | Topic            | Concepts                                  |
| ---------------------- | ---------------- | ----------------------------------------- |
| `01_hello_world.ow`    | Hello World      | Basic program structure                   |
| `02_variables.ow`      | Variables        | `let`, `let mut`, type annotations        |
| `03_functions.ow`      | Functions        | Parameters, return types, implicit return |
| `04_if_expression.ow`  | Conditionals     | `if` statement vs expression              |
| `05_option.ow`         | Option Type      | `Some`, `None`, optional values           |
| `06_result.ow`         | Result Type      | `Ok`, `Err`, error handling               |
| `07_try_operator.ow`   | Try Operator     | `?` for error propagation                 |
| `08_match.ow`          | Pattern Matching | `match` expression                        |
| `09_lists.ow`          | Lists            | `List[T]`, `len`, `get`, `push`           |
| `10_while_loop.ow`     | While Loop       | `while` statement                         |
| `11_for_loop.ow`       | For-In Loop      | Iteration with `for x in xs`              |
| `12_loop_range.ow`     | Loop & Range     | `loop`, `range(a, b)`                     |
| `13_break_continue.ow` | Loop Control     | `break`, `continue`                       |

## Running Examples

```bash
# Compile and run
owl run examples/01_hello_world.ow

# Compile only (outputs Python)
owl build examples/01_hello_world.ow

# Check types without compiling
owl check examples/01_hello_world.ow
```

## Future Examples

The `_future/` directory contains examples that use features not yet implemented:
- `04_classes.ow` - Structs and methods (planned for v0.2.5)
- `06_rest_api_client.ow` - Real-world API example

These will be moved to the main directory when the features are ready.
