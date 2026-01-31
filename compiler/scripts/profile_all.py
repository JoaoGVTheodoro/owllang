#!/usr/bin/env python3
"""
Profile all example files and generate a timing report.
"""
import time
from pathlib import Path
from owllang import compile_source

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"

def profile_file(filepath: Path, runs: int = 10) -> dict:
    """Profile a single file multiple times."""
    source = filepath.read_text()
    
    times = {
        'lex': [],
        'parse': [],
        'check': [],
        'transpile': [],
        'total': []
    }
    
    for _ in range(runs):
        import owllang.lexer as lexer
        import owllang.parser as parser
        from owllang.typechecker import TypeChecker
        from owllang.transpiler import transpile
        
        # Lexer
        start = time.perf_counter()
        tokens = lexer.tokenize(source)
        times['lex'].append(time.perf_counter() - start)
        
        # Parser
        start = time.perf_counter()
        ast = parser.parse(tokens)
        times['parse'].append(time.perf_counter() - start)
        
        # TypeChecker
        start = time.perf_counter()
        checker = TypeChecker()
        checker.check(ast)
        times['check'].append(time.perf_counter() - start)
        
        # Transpiler
        start = time.perf_counter()
        transpile(ast)
        times['transpile'].append(time.perf_counter() - start)
        
        # Total
        times['total'].append(sum([times['lex'][-1], times['parse'][-1], 
                                   times['check'][-1], times['transpile'][-1]]))
    
    # Calculate averages
    return {
        'lex': sum(times['lex']) / runs,
        'parse': sum(times['parse']) / runs,
        'check': sum(times['check']) / runs,
        'transpile': sum(times['transpile']) / runs,
        'total': sum(times['total']) / runs,
        'lines': len(source.split('\n'))
    }

def main():
    """Profile all example files."""
    files = sorted(EXAMPLES_DIR.glob("*.ow"))
    
    print("=" * 80)
    print("OwlLang Compiler Performance Profile")
    print("=" * 80)
    print()
    
    results = []
    for file in files:
        try:
            stats = profile_file(file)
            results.append((file.name, stats))
            print(f"✓ {file.name:<30} ({stats['lines']:3d} lines) {stats['total']*1000:6.3f}ms")
        except Exception as e:
            print(f"✗ {file.name:<30} ERROR: {e}")
    
    print()
    print("=" * 80)
    print("Average Breakdown (across all files)")
    print("=" * 80)
    
    avg_lex = sum(s['lex'] for _, s in results) / len(results)
    avg_parse = sum(s['parse'] for _, s in results) / len(results)
    avg_check = sum(s['check'] for _, s in results) / len(results)
    avg_transpile = sum(s['transpile'] for _, s in results) / len(results)
    avg_total = sum(s['total'] for _, s in results) / len(results)
    
    print(f"Lexer:       {avg_lex*1000:6.3f}ms ({avg_lex/avg_total*100:5.1f}%)")
    print(f"Parser:      {avg_parse*1000:6.3f}ms ({avg_parse/avg_total*100:5.1f}%)")
    print(f"TypeChecker: {avg_check*1000:6.3f}ms ({avg_check/avg_total*100:5.1f}%)")
    print(f"Transpiler:  {avg_transpile*1000:6.3f}ms ({avg_transpile/avg_total*100:5.1f}%)")
    print(f"TOTAL:       {avg_total*1000:6.3f}ms")
    print()
    
    # Find slowest files
    print("=" * 80)
    print("Slowest Files")
    print("=" * 80)
    results.sort(key=lambda x: x[1]['total'], reverse=True)
    for filename, stats in results[:5]:
        print(f"{filename:<30} {stats['total']*1000:6.3f}ms  "
              f"(L:{stats['lex']*1000:.2f}ms P:{stats['parse']*1000:.2f}ms "
              f"C:{stats['check']*1000:.2f}ms T:{stats['transpile']*1000:.2f}ms)")

if __name__ == "__main__":
    main()
