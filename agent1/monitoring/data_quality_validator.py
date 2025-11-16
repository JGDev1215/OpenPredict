#!/usr/bin/env python3
"""
Data quality validation script
Validates data integrity in Supabase database
"""
import sys
import os
import argparse
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import db_client
from config import INSTRUMENT


class DataQualityValidator:
    """Validates data quality in database"""
    
    def __init__(self, window_hours=1):
        """
        Initialize validator
        
        Args:
            window_hours: Time window to validate (hours)
        """
        self.window_hours = window_hours
        self.since = datetime.utcnow() - timedelta(hours=window_hours)
        self.issues = []
    
    def check_ohlc_continuity(self):
        """Check for gaps in OHLC data"""
        print(f"\nChecking OHLC data continuity (last {self.window_hours}h)...")
        
        try:
            # Fetch recent OHLC data
            response = (
                db_client.client.table("ohlc_data")
                .select("timestamp")
                .eq("instrument", INSTRUMENT)
                .gte("timestamp", self.since.isoformat())
                .order("timestamp")
                .execute()
            )
            
            data = response.data
            
            if not data:
                print("  WARN: No OHLC data found")
                self.issues.append("No OHLC data in time window")
                return
            
            print(f"  Found {len(data)} OHLC records")
            
            # Check for gaps >2 minutes
            gaps_found = 0
            for i in range(1, len(data)):
                prev_ts = datetime.fromisoformat(data[i-1]['timestamp'].replace('Z', '+00:00'))
                curr_ts = datetime.fromisoformat(data[i]['timestamp'].replace('Z', '+00:00'))
                gap_seconds = (curr_ts - prev_ts).total_seconds()
                
                if gap_seconds > 120:  # >2 minutes
                    gaps_found += 1
                    if gaps_found <= 5:  # Only print first 5
                        print(f"  WARN: Gap of {gap_seconds}s between {prev_ts} and {curr_ts}")
            
            if gaps_found > 0:
                print(f"  WARN: Found {gaps_found} gaps >2 minutes")
                self.issues.append(f"{gaps_found} data gaps detected")
            else:
                print(f"  PASS: No significant gaps detected")
        
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            self.issues.append(f"OHLC continuity check failed: {str(e)}")
    
    def check_reference_levels(self):
        """Check reference levels are being calculated"""
        print(f"\nChecking reference levels (last {self.window_hours}h)...")
        
        try:
            response = (
                db_client.client.table("reference_levels")
                .select("level_type")
                .eq("instrument", INSTRUMENT)
                .gte("timestamp", self.since.isoformat())
                .execute()
            )
            
            data = response.data
            
            if not data:
                print("  WARN: No reference levels found")
                self.issues.append("No reference levels calculated")
                return
            
            # Count by type
            level_types = {}
            for record in data:
                lt = record['level_type']
                level_types[lt] = level_types.get(lt, 0) + 1
            
            print(f"  Found {len(data)} reference levels:")
            for level_type, count in sorted(level_types.items()):
                print(f"    {level_type}: {count}")
            
            # Expected types
            expected_types = ['DAILY_OPEN', '1H_OPEN']
            missing_types = [t for t in expected_types if t not in level_types]
            
            if missing_types:
                print(f"  WARN: Missing level types: {missing_types}")
                self.issues.append(f"Missing reference level types: {missing_types}")
            else:
                print(f"  PASS: All expected level types present")
        
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            self.issues.append(f"Reference levels check failed: {str(e)}")
    
    def check_data_freshness(self):
        """Check data freshness (last update time)"""
        print(f"\nChecking data freshness...")
        
        tables = ['ohlc_data', 'reference_levels', 'fibonacci_pivots']
        
        for table in tables:
            try:
                response = (
                    db_client.client.table(table)
                    .select("timestamp")
                    .eq("instrument", INSTRUMENT)
                    .order("timestamp", desc=True)
                    .limit(1)
                    .execute()
                )
                
                data = response.data
                
                if not data:
                    print(f"  {table}: No data")
                    continue
                
                latest_ts = datetime.fromisoformat(data[0]['timestamp'].replace('Z', '+00:00'))
                age_seconds = (datetime.utcnow() - latest_ts.replace(tzinfo=None)).total_seconds()
                
                status = "PASS" if age_seconds < 300 else "WARN"  # <5 minutes
                print(f"  {table}: {age_seconds:.0f}s ago ({status})")
                
                if age_seconds > 300:
                    self.issues.append(f"{table} data is stale ({age_seconds:.0f}s old)")
            
            except Exception as e:
                print(f"  {table}: ERROR - {str(e)}")
                self.issues.append(f"{table} freshness check failed: {str(e)}")
    
    def check_for_duplicates(self):
        """Check for duplicate records"""
        print(f"\nChecking for duplicate timestamps...")
        
        try:
            # This query checks for duplicate timestamps in OHLC data
            # Note: May need to adjust based on actual schema
            response = (
                db_client.client.table("ohlc_data")
                .select("timestamp")
                .eq("instrument", INSTRUMENT)
                .gte("timestamp", self.since.isoformat())
                .execute()
            )
            
            data = response.data
            timestamps = [record['timestamp'] for record in data]
            
            if len(timestamps) != len(set(timestamps)):
                duplicates = len(timestamps) - len(set(timestamps))
                print(f"  WARN: Found {duplicates} duplicate timestamps")
                self.issues.append(f"{duplicates} duplicate OHLC records")
            else:
                print(f"  PASS: No duplicates detected")
        
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            self.issues.append(f"Duplicate check failed: {str(e)}")
    
    def run_validation(self):
        """Run all validation checks"""
        print("=" * 60)
        print("Data Quality Validation")
        print("=" * 60)
        print(f"Time window: Last {self.window_hours} hour(s)")
        print(f"Instrument: {INSTRUMENT}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        self.check_data_freshness()
        self.check_ohlc_continuity()
        self.check_reference_levels()
        self.check_for_duplicates()
        
        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.issues:
            print(f"Found {len(self.issues)} issue(s):")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
            print("\nStatus: FAIL")
            return False
        else:
            print("No issues detected")
            print("\nStatus: PASS")
            return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Data quality validator for Agent 1')
    parser.add_argument('--window', type=int, default=1,
                       help='Time window to validate in hours (default: 1)')
    
    args = parser.parse_args()
    
    validator = DataQualityValidator(window_hours=args.window)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
