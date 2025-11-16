#!/usr/bin/env python3
"""
Continuous monitoring script for 24-hour test
Tracks metrics, errors, and performance in real-time
"""
import sys
import os
import time
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ContinuousMonitor:
    """Monitor Agent 1 during 24-hour continuous test"""
    
    def __init__(self, log_file, duration_hours=24):
        """
        Initialize monitor
        
        Args:
            log_file: Path to agent1 log file
            duration_hours: Test duration in hours
        """
        self.log_file = log_file
        self.duration_hours = duration_hours
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=duration_hours)
        
        # Metrics
        self.total_cycles = 0
        self.successful_cycles = 0
        self.failed_cycles = 0
        self.execution_times = []
        self.errors_by_type = defaultdict(int)
        self.errors_timeline = []
        
        # Performance tracking
        self.hourly_stats = []
        self.current_hour_cycles = []
        self.last_processed_line = 0
        
        print(f"Continuous Monitor Started")
        print(f"Duration: {duration_hours} hours")
        print(f"Start Time: {self.start_time.isoformat()}")
        print(f"End Time: {self.end_time.isoformat()}")
        print(f"Monitoring log: {log_file}")
        print("-" * 60)
    
    def parse_log_line(self, line):
        """Parse a log line and extract metrics"""
        
        # Cycle started
        if "Cycle #" in line and "Started" in line:
            match = re.search(r'Cycle #(\d+)', line)
            if match:
                self.total_cycles = max(self.total_cycles, int(match.group(1)))
        
        # Cycle completed
        if "Cycle #" in line and "Completed in" in line:
            match = re.search(r'Completed in ([\d.]+)s', line)
            if match:
                exec_time = float(match.group(1))
                self.execution_times.append(exec_time)
                self.current_hour_cycles.append(exec_time)
                self.successful_cycles += 1
        
        # Error detected
        if "ERROR" in line:
            self.failed_cycles += 1
            
            # Classify error type
            if "yfinance" in line.lower() or "yahoo" in line.lower():
                error_type = "Network/API"
            elif "supabase" in line.lower() or "database" in line.lower():
                error_type = "Database"
            elif "timeout" in line.lower():
                error_type = "Timeout"
            else:
                error_type = "Other"
            
            self.errors_by_type[error_type] += 1
            self.errors_timeline.append({
                'timestamp': datetime.now().isoformat(),
                'type': error_type,
                'line': line.strip()
            })
    
    def calculate_hourly_stats(self):
        """Calculate stats for the current hour"""
        if not self.current_hour_cycles:
            return None
        
        import statistics
        
        stats = {
            'hour': len(self.hourly_stats) + 1,
            'cycles': len(self.current_hour_cycles),
            'avg_time': statistics.mean(self.current_hour_cycles),
            'min_time': min(self.current_hour_cycles),
            'max_time': max(self.current_hour_cycles),
            'median_time': statistics.median(self.current_hour_cycles),
        }
        
        # Reset for next hour
        self.current_hour_cycles = []
        
        return stats
    
    def print_status(self):
        """Print current monitoring status"""
        elapsed = datetime.now() - self.start_time
        remaining = self.end_time - datetime.now()
        
        # Calculate metrics
        success_rate = (self.successful_cycles / max(self.total_cycles, 1)) * 100
        
        avg_exec_time = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
        
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Status Update")
        print("-" * 60)
        print(f"Elapsed Time: {str(elapsed).split('.')[0]}")
        print(f"Remaining: {str(remaining).split('.')[0]}")
        print(f"Progress: {(elapsed.total_seconds() / (self.duration_hours * 3600)) * 100:.1f}%")
        print()
        print(f"Total Cycles: {self.total_cycles}")
        print(f"Successful: {self.successful_cycles}")
        print(f"Failed: {self.failed_cycles}")
        print(f"Success Rate: {success_rate:.2f}%")
        print()
        print(f"Avg Execution Time: {avg_exec_time:.2f}s")
        if self.execution_times:
            print(f"Min/Max: {min(self.execution_times):.2f}s / {max(self.execution_times):.2f}s")
        print()
        
        if self.errors_by_type:
            print("Errors by Type:")
            for error_type, count in sorted(self.errors_by_type.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count}")
        else:
            print("No errors detected")
        
        print("-" * 60)
    
    def generate_report(self, output_file):
        """Generate final JSON report"""
        
        # Calculate final stats
        import statistics
        
        success_rate = (self.successful_cycles / max(self.total_cycles, 1)) * 100
        
        report = {
            'test_metadata': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_hours': self.duration_hours,
                'planned_end_time': self.end_time.isoformat(),
            },
            'summary': {
                'total_cycles': self.total_cycles,
                'successful_cycles': self.successful_cycles,
                'failed_cycles': self.failed_cycles,
                'success_rate': round(success_rate, 2),
            },
            'performance': {
                'avg_execution_time': round(statistics.mean(self.execution_times), 2) if self.execution_times else 0,
                'min_execution_time': round(min(self.execution_times), 2) if self.execution_times else 0,
                'max_execution_time': round(max(self.execution_times), 2) if self.execution_times else 0,
                'median_execution_time': round(statistics.median(self.execution_times), 2) if self.execution_times else 0,
                'p95_execution_time': round(statistics.quantiles(self.execution_times, n=20)[18], 2) if len(self.execution_times) > 20 else 0,
                'p99_execution_time': round(statistics.quantiles(self.execution_times, n=100)[98], 2) if len(self.execution_times) > 100 else 0,
            },
            'errors': {
                'total': self.failed_cycles,
                'by_type': dict(self.errors_by_type),
                'error_rate': round((self.failed_cycles / max(self.total_cycles, 1)) * 100, 2),
            },
            'hourly_stats': self.hourly_stats,
            'recent_errors': self.errors_timeline[-50:],  # Last 50 errors
        }
        
        # Assessment
        report['assessment'] = {
            'success_rate_target_met': success_rate >= 95.0,
            'execution_time_target_met': report['performance']['p95_execution_time'] < 8.0 if self.execution_times else False,
            'overall_pass': success_rate >= 95.0 and (report['performance']['p95_execution_time'] < 8.0 if self.execution_times else False),
        }
        
        # Write report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {output_file}")
        
        return report
    
    def run(self, output_file='monitoring_report.json', update_interval=300):
        """
        Run continuous monitoring
        
        Args:
            output_file: Output report file path
            update_interval: Status update interval in seconds (default 5 minutes)
        """
        
        last_update = time.time()
        last_hour_check = datetime.now()
        
        try:
            # Wait for log file to exist
            while not os.path.exists(self.log_file):
                print(f"Waiting for log file: {self.log_file}")
                time.sleep(5)
            
            with open(self.log_file, 'r') as f:
                # Monitor until end time
                while datetime.now() < self.end_time:
                    # Read new lines
                    lines = f.readlines()
                    for line in lines[self.last_processed_line:]:
                        self.parse_log_line(line)
                    self.last_processed_line = len(lines)
                    
                    # Print status update
                    if time.time() - last_update > update_interval:
                        self.print_status()
                        last_update = time.time()
                    
                    # Calculate hourly stats
                    if (datetime.now() - last_hour_check).total_seconds() > 3600:
                        hourly = self.calculate_hourly_stats()
                        if hourly:
                            self.hourly_stats.append(hourly)
                            print(f"\nHour {hourly['hour']} completed:")
                            print(f"  Cycles: {hourly['cycles']}")
                            print(f"  Avg time: {hourly['avg_time']:.2f}s")
                        last_hour_check = datetime.now()
                    
                    time.sleep(10)  # Check every 10 seconds
            
            # Final status
            print("\n" + "=" * 60)
            print("24-HOUR TEST COMPLETED")
            print("=" * 60)
            self.print_status()
            
            # Generate report
            report = self.generate_report(output_file)
            
            # Print assessment
            print("\n" + "=" * 60)
            print("FINAL ASSESSMENT")
            print("=" * 60)
            print(f"Success Rate Target (>95%): {'PASS' if report['assessment']['success_rate_target_met'] else 'FAIL'}")
            print(f"Execution Time Target (<8s): {'PASS' if report['assessment']['execution_time_target_met'] else 'FAIL'}")
            print(f"\nOverall Result: {'PASS' if report['assessment']['overall_pass'] else 'FAIL'}")
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\nMonitoring interrupted by user")
            self.generate_report(output_file)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Continuous monitoring for Agent 1')
    parser.add_argument('--log-file', default='/var/log/agent1/agent1_staging.log',
                       help='Path to agent1 log file')
    parser.add_argument('--duration', type=int, default=24,
                       help='Test duration in hours (default: 24)')
    parser.add_argument('--output', default='monitoring_report_24h.json',
                       help='Output report file')
    parser.add_argument('--update-interval', type=int, default=300,
                       help='Status update interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    monitor = ContinuousMonitor(args.log_file, args.duration)
    monitor.run(args.output, args.update_interval)


if __name__ == "__main__":
    main()
