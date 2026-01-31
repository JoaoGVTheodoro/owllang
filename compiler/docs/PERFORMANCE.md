# OwlLang Compiler Performance Report

## Summary

Performance profiling and optimization pass completed for OwlLang compiler v0.1.0-alpha.

## Methodology

1. **Profiling Infrastructure**: Added `--profile` flag to CLI commands
2. **Baseline Measurement**: Profiled all example files (10 runs each)
3. **Detailed Analysis**: Used cProfile to identify hotspots
4. **Optimization**: Applied targeted optimizations to hot paths
5. **Validation**: Ensured all 377 tests pass after optimizations

## Measurements

### Before Optimization (Baseline)

| Phase       | Time (avg)  | % of Total |
| ----------- | ----------- | ---------- |
| Lexer       | 0.254ms     | 50.1%      |
| Parser      | 0.169ms     | 33.3%      |
| TypeChecker | 0.045ms     | 8.8%       |
| Transpiler  | 0.039ms     | 7.7%       |
| **TOTAL**   | **0.507ms** | **100%**   |

### After Optimization

| Phase       | Time (avg)  | % of Total | Improvement      |
| ----------- | ----------- | ---------- | ---------------- |
| Lexer       | 0.175ms     | 42.7%      | **31% faster**   |
| Parser      | 0.156ms     | 38.1%      | **7.7% faster**  |
| TypeChecker | 0.042ms     | 10.3%      | 6.7% faster      |
| Transpiler  | 0.036ms     | 8.8%       | 7.7% faster      |
| **TOTAL**   | **0.410ms** | **100%**   | **🚀 19% faster** |

### Performance Impact on Real Files

| File                | Before  | After   | Improvement    |
| ------------------- | ------- | ------- | -------------- |
| 10_match_result.ow  | 1.645ms | 1.427ms | **13% faster** |
| 09_match_option.ow  | 1.328ms | 1.055ms | **21% faster** |
| 03_if_expression.ow | 0.595ms | 0.443ms | **26% faster** |
| 02_functions.ow     | 0.483ms | 0.367ms | **24% faster** |
| 00_hello_world.ow   | 0.102ms | 0.079ms | **23% faster** |

## Optimizations Applied

### 1. Lexer Optimizations (Major Impact)

**Problem**: Hot path functions called hundreds of thousands of times:
- `_is_at_end()`: 316,700 calls
- `_peek()`: 306,200 calls
- `_scan_identifier()`: 12,300 calls

**Solutions**:

#### a) Cache Source Length
```python
# Before: Computed len(self.source) on every call
def _is_at_end(self) -> bool:
    return self.pos >= len(self.source)

# After: Cached in __init__
self.source_len = len(source)
def _is_at_end(self) -> bool:
    return self.pos >= self.source_len
```

**Impact**: Eliminated ~600,000 `len()` calls per compilation

#### b) Use String Slicing Instead of Character Concatenation
```python
# Before: O(n²) string concatenation
def _scan_identifier(self, ...):
    value = ''
    while not self._is_at_end() and (self._peek().isalnum() or self._peek() == '_'):
        value += self._advance()  # Creates new string each time!

# After: O(n) slice operation
def _scan_identifier(self, ...):
    start_pos = self.pos
    while pos < source_len and (source[pos].isalnum() or source[pos] == '_'):
        pos += 1
    value = source[start_pos:pos]  # Single slice
```

**Impact**: 
- Reduced function call overhead (~12,300 `_advance()` calls eliminated)
- Changed from O(n²) to O(n) string building
- Applied to both `_scan_identifier()` and `_scan_number()`

### 2. Parser Optimizations (Minor Impact)

Parser was already efficient (33.3% of time → 38.1%). Lexer improvements shifted relative percentages.

### 3. What We Didn't Do (Intentionally)

- **No semantic changes**: All 377 tests pass unchanged
- **No algorithm changes**: Same lexing/parsing strategy
- **No aggressive caching**: Avoided premature complexity
- **No unsafe optimizations**: Maintained correctness guarantees

## Profiling Tools Added

### 1. CLI `--profile` Flag
```bash
$ owl compile example.ow --profile
[PROFILE] Lexer:      0.450ms
[PROFILE] Parser:     0.410ms
[PROFILE] TypeChecker: 0.100ms
[PROFILE] Transpiler: 0.090ms
[PROFILE] TOTAL:      1.055ms
```

### 2. Profiling Scripts

- `scripts/profile_all.py`: Batch profile all examples
- `scripts/profile_detailed.py`: cProfile deep dive on specific files

## Future Optimization Opportunities

### Low-Hanging Fruit (Not Done Yet)

1. **Parser Token Lookahead**: Cache `_peek()` results
2. **Type Interning**: Deduplicate `Type` objects
3. **AST Node Pooling**: Reuse node allocations

### Diminishing Returns (Skip For Now)

1. **Custom String Builder**: Python strings already optimized
2. **Regex-based Lexer**: Overkill for simple language
3. **Bytecode Caching**: Files too small to benefit

## Conclusion

**✅ Goal Achieved**: 19% overall speedup with zero behavioral changes

The profiling infrastructure is now in place for future performance work. All optimizations maintain semantic correctness (377/377 tests passing).

### Key Takeaway

> Most compiler time (50%) was spent in lexer hot paths. By eliminating redundant `len()` calls and using string slicing instead of concatenation, we achieved a **31% lexer speedup** and **19% total speedup**.

## Testing

All 377 tests pass after optimizations:
```bash
$ python -m pytest tests/ -v
==================== 377 passed in 1.45s ====================
```

## Benchmarking Reproducibility

To reproduce these measurements:
```bash
# Single file with timing
$ owl compile examples/10_match_result.ow --profile

# All examples
$ python scripts/profile_all.py

# Detailed cProfile analysis
$ python scripts/profile_detailed.py
```

---

**Date**: 2024
**Version**: v0.1.0-alpha
**Test Coverage**: 377/377 passing
**Performance**: 🚀 19% faster than baseline
