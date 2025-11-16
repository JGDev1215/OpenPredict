#!/usr/bin/env python3
"""
Health check script for Agent 1
Validates environment, dependencies, and external connections
"""
import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_python_version():
    """Check Python version is 3.11+"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"  FAIL: Python {version.major}.{version.minor} (requires 3.11+)")
        return False
    print(f"  PASS: Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check required dependencies are installed"""
    print("\nChecking dependencies...")
    required_packages = {
        'yfinance': '0.2.32',
        'supabase': '2.0.0',
        'pandas': '2.1.0',
        'dotenv': '1.0.0',
        'apscheduler': '3.10.4',
        'pytz': '2023.3',
        'numpy': '1.24.0',
    }
    
    all_ok = True
    for package, min_version in required_packages.items():
        try:
            if package == 'dotenv':
                import dotenv
                module = dotenv
            elif package == 'apscheduler':
                import apscheduler
                module = apscheduler
            else:
                module = __import__(package)
            
            version = getattr(module, '__version__', 'unknown')
            print(f"  PASS: {package} {version}")
        except ImportError:
            print(f"  FAIL: {package} not installed (requires >={min_version})")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Check .env file exists and has required variables"""
    print("\nChecking .env configuration...")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    if not os.path.exists(env_path):
        print(f"  FAIL: .env file not found at {env_path}")
        return False
    
    print(f"  PASS: .env file exists")
    
    # Load env
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'INSTRUMENT']
    all_ok = True
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == '':
            print(f"  FAIL: {var} not set in .env")
            all_ok = False
        else:
            # Mask sensitive values
            if 'KEY' in var or 'PASSWORD' in var:
                display = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display = value
            print(f"  PASS: {var} = {display}")
    
    return all_ok


def check_database_connection():
    """Check Supabase database connection"""
    print("\nChecking Supabase connection...")
    
    try:
        from supabase_client import db_client
        
        # Try a simple query
        result = db_client.client.table("ohlc_data").select("*").limit(1).execute()
        
        print(f"  PASS: Connected to Supabase")
        print(f"  INFO: Query successful")
        return True
        
    except Exception as e:
        print(f"  FAIL: Cannot connect to Supabase")
        print(f"  ERROR: {str(e)}")
        return False


def check_yfinance_connection():
    """Check Yahoo Finance API connection"""
    print("\nChecking Yahoo Finance API...")
    
    try:
        import yfinance as yf
        from config import INSTRUMENT
        
        # Try to fetch data
        ticker = yf.Ticker(INSTRUMENT)
        data = ticker.history(period="1d", interval="1m")
        
        if data.empty:
            print(f"  WARN: API responded but no data for {INSTRUMENT}")
            print(f"  INFO: This may be normal outside market hours")
            return True
        
        print(f"  PASS: Fetched {len(data)} bars for {INSTRUMENT}")
        print(f"  INFO: Latest price: {data['Close'].iloc[-1]:.2f}")
        return True
        
    except Exception as e:
        print(f"  FAIL: Cannot connect to Yahoo Finance")
        print(f"  ERROR: {str(e)}")
        return False


def check_log_directory():
    """Check log directory exists and is writable"""
    print("\nChecking log directory...")
    
    from config import LOG_FILE
    
    log_dir = os.path.dirname(LOG_FILE)
    
    if not log_dir:
        log_dir = "."
    
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            print(f"  PASS: Created log directory: {log_dir}")
        except Exception as e:
            print(f"  FAIL: Cannot create log directory: {log_dir}")
            print(f"  ERROR: {str(e)}")
            return False
    else:
        print(f"  PASS: Log directory exists: {log_dir}")
    
    # Check if writable
    test_file = os.path.join(log_dir, '.write_test')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"  PASS: Log directory is writable")
        return True
    except Exception as e:
        print(f"  FAIL: Log directory not writable")
        print(f"  ERROR: {str(e)}")
        return False


def main():
    """Main health check"""
    parser = argparse.ArgumentParser(description='Agent 1 Health Check')
    parser.add_argument('--check-db', action='store_true', help='Check database connection')
    parser.add_argument('--check-yfinance', action='store_true', help='Check Yahoo Finance API')
    parser.add_argument('--all', action='store_true', help='Run all checks')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Agent 1 - Data Collector Health Check")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    results = []
    
    # Always check basics
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Environment Config", check_env_file()))
    results.append(("Log Directory", check_log_directory()))
    
    # Optional checks
    if args.check_db or args.all:
        results.append(("Database Connection", check_database_connection()))
    
    if args.check_yfinance or args.all:
        results.append(("Yahoo Finance API", check_yfinance_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status:6} | {check}")
    
    print("-" * 60)
    print(f"Result: {passed}/{total} checks passed")
    print("=" * 60)
    
    # Exit code
    if passed == total:
        print("\nAll checks passed! System is healthy.")
        sys.exit(0)
    else:
        print(f"\n{total - passed} check(s) failed. Please fix issues before deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
