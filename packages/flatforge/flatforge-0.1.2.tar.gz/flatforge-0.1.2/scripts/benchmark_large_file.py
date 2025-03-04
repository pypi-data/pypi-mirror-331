#!/usr/bin/env python
"""
Benchmark script for testing large file processing performance.

This script generates a large test file and measures the performance of
processing it using different methods.

Usage:
    python benchmark_large_file.py [--size SIZE] [--output OUTPUT]

Options:
    --size SIZE       Size of the test file in MB [default: 100]
    --output OUTPUT   Output directory for benchmark results [default: .]
"""
import os
import sys
import time
import argparse
import tempfile
import gc
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

try:
    import psutil
except ImportError:
    print("Error: psutil is required for this benchmark.")
    print("Install it with: pip install psutil")
    sys.exit(1)

# Add parent directory to path to import flatforge
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flatforge.models import FileProperties, Section, Rule
from flatforge.processor import ValidationProcessor
from flatforge.utils import TextFormat


def create_test_config():
    """Create a test configuration."""
    file_props = FileProperties()
    file_props.text_format_code = TextFormat.DELIMITED.value
    file_props.field_separator = ","
    file_props.record_separator = "\n"
    
    # Create a section
    section = Section(index="0")
    section.section_format = TextFormat.DELIMITED.value
    
    # Add rules for columns
    section.rules = {
        0: [Rule(name="str", parameters=["10"])],
        1: [Rule(name="num", parameters=["5"])],
        2: [Rule(name="str", parameters=["20"])]
    }
    
    # Add to metadata
    file_props.sections["0"] = section
    
    return file_props


def create_large_file(size_mb):
    """Create a large test file of approximately the specified size in MB."""
    # Calculate number of records needed to reach the target size
    # Each record is approximately 30 bytes
    record_size = 30  # bytes
    num_records = int((size_mb * 1024 * 1024) / record_size)
    
    print(f"Creating test file with {num_records:,} records (~{size_mb} MB)...")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        for i in range(num_records):
            f.write(f"test{i % 10000:04d},{i % 100000},description{i % 1000}\n")
            
            # Print progress
            if i % 100000 == 0 and i > 0:
                print(f"  {i:,} records written ({i/num_records*100:.1f}%)")
    
    print(f"Test file created: {f.name}")
    return f.name


def measure_memory_usage(func, *args, **kwargs):
    """Measure memory usage of a function."""
    # Force garbage collection
    gc.collect()
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    memory_usage = [process.memory_info().rss / 1024 / 1024]  # MB
    
    # Start timer
    start_time = time.time()
    
    # Run the function and collect memory usage during execution
    result = func(*args, **kwargs)
    
    # End timer
    end_time = time.time()
    
    # Get final memory usage
    memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
    
    return {
        'result': result,
        'memory_before': memory_usage[0],
        'memory_after': memory_usage[1],
        'memory_increase': memory_usage[1] - memory_usage[0],
        'execution_time': end_time - start_time
    }


def run_benchmark(file_path, config, output_dir='.'):
    """Run benchmark comparing standard and line-by-line processing."""
    print("\nRunning benchmark...")
    
    # Create processor
    processor = ValidationProcessor(config)
    
    # Create temporary output files
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as out_f:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as err_f:
            # Measure standard processing
            print("\nTesting standard processing method...")
            try:
                standard_stats = measure_memory_usage(
                    processor.process, file_path, out_f.name, err_f.name
                )
                print(f"  Memory before: {standard_stats['memory_before']:.2f} MB")
                print(f"  Memory after: {standard_stats['memory_after']:.2f} MB")
                print(f"  Memory increase: {standard_stats['memory_increase']:.2f} MB")
                print(f"  Execution time: {standard_stats['execution_time']:.2f} seconds")
                print(f"  Messages: {len(standard_stats['result'])}")
            except MemoryError:
                print("  Memory error occurred - file too large for standard processing")
                standard_stats = {
                    'memory_before': 0,
                    'memory_after': 0,
                    'memory_increase': 0,
                    'execution_time': 0,
                    'result': []
                }
            
            # Measure line-by-line processing
            print("\nTesting line-by-line processing method...")
            line_by_line_stats = measure_memory_usage(
                processor.process_line_by_line, file_path, out_f.name, err_f.name
            )
            print(f"  Memory before: {line_by_line_stats['memory_before']:.2f} MB")
            print(f"  Memory after: {line_by_line_stats['memory_after']:.2f} MB")
            print(f"  Memory increase: {line_by_line_stats['memory_increase']:.2f} MB")
            print(f"  Execution time: {line_by_line_stats['execution_time']:.2f} seconds")
            print(f"  Messages: {len(line_by_line_stats['result'])}")
    
    # Clean up temporary files
    os.unlink(out_f.name)
    os.unlink(err_f.name)
    
    # Create comparison chart
    create_comparison_chart(standard_stats, line_by_line_stats, output_dir)
    
    return standard_stats, line_by_line_stats


def create_comparison_chart(standard_stats, line_by_line_stats, output_dir):
    """Create a comparison chart of the benchmark results."""
    try:
        # Set up the figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Memory usage comparison
        labels = ['Standard', 'Line-by-line']
        memory_increases = [standard_stats['memory_increase'], line_by_line_stats['memory_increase']]
        
        ax1.bar(labels, memory_increases, color=['#ff9999', '#66b3ff'])
        ax1.set_ylabel('Memory Increase (MB)')
        ax1.set_title('Memory Usage Comparison')
        
        # Add values on top of bars
        for i, v in enumerate(memory_increases):
            ax1.text(i, v + 0.1, f"{v:.2f} MB", ha='center')
        
        # Execution time comparison
        times = [standard_stats['execution_time'], line_by_line_stats['execution_time']]
        
        ax2.bar(labels, times, color=['#ff9999', '#66b3ff'])
        ax2.set_ylabel('Execution Time (seconds)')
        ax2.set_title('Performance Comparison')
        
        # Add values on top of bars
        for i, v in enumerate(times):
            ax2.text(i, v + 0.1, f"{v:.2f} s", ha='center')
        
        plt.tight_layout()
        
        # Save the figure
        output_path = os.path.join(output_dir, 'benchmark_results.png')
        plt.savefig(output_path)
        print(f"\nBenchmark chart saved to: {output_path}")
    except Exception as e:
        print(f"Error creating comparison chart: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Benchmark large file processing")
    parser.add_argument("--size", type=int, default=100, help="Size of the test file in MB")
    parser.add_argument("--output", type=str, default=".", help="Output directory for benchmark results")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Create test configuration
    config = create_test_config()
    
    # Create large test file
    file_path = create_large_file(args.size)
    
    try:
        # Run benchmark
        run_benchmark(file_path, config, args.output)
    finally:
        # Clean up test file
        os.unlink(file_path)


if __name__ == "__main__":
    main() 