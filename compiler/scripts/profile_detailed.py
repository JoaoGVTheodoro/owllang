#!/usr/bin/env python3
"""
Detailed profiling with cProfile to identify bottlenecks.
"""
import cProfile
import pstats
from pathlib import Path
from owllang import compile_source

# Use one of the larger example files
EXAMPLE_FILE = Path(__file__).parent.parent.parent / "examples" / "10_match_result.ow"

def profile_compilation():
    """Profile a single compilation."""
    source = EXAMPLE_FILE.read_text()
    compile_source(source, check_types=True)

if __name__ == "__main__":
    print(f"Profiling compilation of {EXAMPLE_FILE.name}")
    print("=" * 80)
    
    # Run cProfile
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run compilation multiple times for better statistics
    for _ in range(100):
        profile_compilation()
    
    profiler.disable()
    
    # Print stats
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    
    print("\nTop 30 functions by cumulative time:")
    print("=" * 80)
    stats.print_stats(30)
    
    print("\n" + "=" * 80)
    print("Top 30 functions by total time:")
    print("=" * 80)
    stats.sort_stats('tottime')
    stats.print_stats(30)
