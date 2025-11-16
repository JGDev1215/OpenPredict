#!/usr/bin/env python3
"""
Performance benchmarking script for Agent 1
Measures execution time, resource usage, and success rate
"""
import sys
import os
import time
import json
import argparse
from datetime import datetime
import statistics

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent1_main import Agent1


class PerformanceBenchmark:
    """Performance benchmark runner"""
    
    def __init__(self, cycles=100):
        """
        Initialize benchmark
        
        Args:
            cycles: Number of cycles to run
        """
        self.cycles = cycles
        self.execution_times = []
        self.step_times = {
            'fetch': [],
            'store_ohlc': [],
            'calc_ref_levels': [],
            'calc_pivots': [],
            'detect_liquidity': [],
            'detect_fvg': [],
            'segment_blocks': [],
            'detect_structure': [],
        }
        self.success_count = 0
        self.error_count = 0
        self.memory_samples = []
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return None
    
    def run_benchmark(self):
        """Run performance benchmark"""
        print("=" * 60)
        print("Agent 1 Performance Benchmark")
        print("=" * 60)
        print(f"Cycles to run: {self.cycles}")
        print(f"Start time: {datetime.now().isoformat()}")
        print()
        
        agent = Agent1()
        
        # Initial memory
        initial_memory = self.get_memory_usage()
        if initial_memory:
            print(f"Initial memory: {initial_memory:.2f} MB")
        
        print("\nRunning benchmark...")
        print("-" * 60)
        
        for i in range(self.cycles):
            start = time.time()
            
            try:
                # Run one cycle
                agent.run_collection_cycle()
                
                elapsed = time.time() - start
                self.execution_times.append(elapsed)
                self.success_count += 1
                
                # Sample memory every 10 cycles
                if i % 10 == 0:
                    mem = self.get_memory_usage()
                    if mem:
                        self.memory_samples.append(mem)
                
                # Progress update every 10 cycles
                if (i + 1) % 10 == 0:
                    avg_time = statistics.mean(self.execution_times[-10:])
                    print(f"Cycle {i+1}/{self.cycles} | Avg time (last 10): {avg_time:.2f}s")
                
            except Exception as e:
                self.error_count += 1
                print(f"Cycle {i+1} failed: {str(e)}")
        
        # Final memory
        final_memory = self.get_memory_usage()
        
        print("-" * 60)
        print("\nBenchmark completed!")
        print()
        
        # Calculate statistics
        self.print_results(initial_memory, final_memory)
        
        return self.generate_report(initial_memory, final_memory)
    
    def print_results(self, initial_memory, final_memory):
        """Print benchmark results"""
        
        print("=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        
        print(f"\nExecution Summary:")
        print(f"  Total cycles: {self.cycles}")
        print(f"  Successful: {self.success_count}")
        print(f"  Failed: {self.error_count}")
        print(f"  Success rate: {(self.success_count / self.cycles) * 100:.2f}%")
        
        if self.execution_times:
            print(f"\nExecution Time Statistics:")
            print(f"  Mean: {statistics.mean(self.execution_times):.2f}s")
            print(f"  Median: {statistics.median(self.execution_times):.2f}s")
            print(f"  Min: {min(self.execution_times):.2f}s")
            print(f"  Max: {max(self.execution_times):.2f}s")
            print(f"  Std Dev: {statistics.stdev(self.execution_times):.2f}s" if len(self.execution_times) > 1 else "  Std Dev: N/A")
            
            if len(self.execution_times) >= 20:
                p95 = statistics.quantiles(self.execution_times, n=20)[18]
                print(f"  P95: {p95:.2f}s")
            
            if len(self.execution_times) >= 100:
                p99 = statistics.quantiles(self.execution_times, n=100)[98]
                print(f"  P99: {p99:.2f}s")
        
        if self.memory_samples:
            print(f"\nMemory Usage:")
            print(f"  Initial: {initial_memory:.2f} MB")
            print(f"  Final: {final_memory:.2f} MB")
            print(f"  Peak: {max(self.memory_samples):.2f} MB")
            print(f"  Growth: {final_memory - initial_memory:.2f} MB")
            print(f"  Growth rate: {(final_memory - initial_memory) / self.cycles:.4f} MB/cycle")
        
        # Assessment
        print(f"\n" + "=" * 60)
        print("ASSESSMENT")
        print("=" * 60)
        
        success_rate_pass = (self.success_count / self.cycles) * 100 >= 95.0
        print(f"Success Rate (>95%): {'PASS' if success_rate_pass else 'FAIL'}")
        
        if self.execution_times:
            avg_time_pass = statistics.mean(self.execution_times) < 8.0
            print(f"Avg Execution Time (<8s): {'PASS' if avg_time_pass else 'FAIL'}")
            
            if len(self.execution_times) >= 20:
                p95 = statistics.quantiles(self.execution_times, n=20)[18]
                p95_pass = p95 < 8.0
                print(f"P95 Execution Time (<8s): {'PASS' if p95_pass else 'FAIL'}")
        
        if self.memory_samples and initial_memory and final_memory:
            memory_pass = (final_memory - initial_memory) < 100  # <100 MB growth
            print(f"Memory Stability (<100MB growth): {'PASS' if memory_pass else 'FAIL'}")
        
        print("=" * 60)
    
    def generate_report(self, initial_memory, final_memory):
        """Generate JSON report"""
        
        report = {
            'benchmark_metadata': {
                'timestamp': datetime.now().isoformat(),
                'cycles': self.cycles,
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
            },
            'summary': {
                'total_cycles': self.cycles,
                'successful_cycles': self.success_count,
                'failed_cycles': self.error_count,
                'success_rate': round((self.success_count / self.cycles) * 100, 2),
            },
            'execution_time': {},
            'memory': {},
            'assessment': {},
        }
        
        if self.execution_times:
            report['execution_time'] = {
                'mean': round(statistics.mean(self.execution_times), 2),
                'median': round(statistics.median(self.execution_times), 2),
                'min': round(min(self.execution_times), 2),
                'max': round(max(self.execution_times), 2),
                'stdev': round(statistics.stdev(self.execution_times), 2) if len(self.execution_times) > 1 else 0,
            }
            
            if len(self.execution_times) >= 20:
                report['execution_time']['p95'] = round(statistics.quantiles(self.execution_times, n=20)[18], 2)
            
            if len(self.execution_times) >= 100:
                report['execution_time']['p99'] = round(statistics.quantiles(self.execution_times, n=100)[98], 2)
        
        if self.memory_samples:
            report['memory'] = {
                'initial_mb': round(initial_memory, 2),
                'final_mb': round(final_memory, 2),
                'peak_mb': round(max(self.memory_samples), 2),
                'growth_mb': round(final_memory - initial_memory, 2),
                'growth_rate_mb_per_cycle': round((final_memory - initial_memory) / self.cycles, 4),
            }
        
        # Assessment
        report['assessment'] = {
            'success_rate_pass': report['summary']['success_rate'] >= 95.0,
            'avg_time_pass': report['execution_time'].get('mean', 999) < 8.0,
            'p95_time_pass': report['execution_time'].get('p95', 999) < 8.0,
            'memory_stable': report['memory'].get('growth_mb', 999) < 100 if self.memory_samples else None,
        }
        
        return report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Performance benchmark for Agent 1')
    parser.add_argument('--cycles', type=int, default=100,
                       help='Number of cycles to run (default: 100)')
    parser.add_argument('--output', default='benchmark_report.json',
                       help='Output report file')
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark(cycles=args.cycles)
    report = benchmark.run_benchmark()
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
