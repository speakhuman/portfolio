#!/usr/bin/env python
"""
Script to run all QA automation tests.
"""
import os
import sys
import time
import argparse
import subprocess
from datetime import datetime


def run_test(test_script, args=None):
    """
    Run a test script.
    
    Args:
        test_script: Name of the test script
        args: Additional arguments to pass to the script
    
    Returns:
        int: Return code of the process
    """
    # Get the full path to the test script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, test_script)
    
    cmd = [sys.executable, full_path]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*80}")
    print(f"Running {os.path.basename(test_script)}")
    print(f"{'='*80}")
    
    start_time = time.time()
    process = subprocess.run(cmd)
    end_time = time.time()
    
    print(f"\nCompleted in {end_time - start_time:.2f} seconds")
    print(f"Return code: {process.returncode}")
    
    return process.returncode


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run QA automation tests")
    parser.add_argument("--accessibility", action="store_true", help="Run accessibility tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--battery", action="store_true", help="Run battery simulation tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--url", default="http://localhost:3000", help="URL to test")
    
    args = parser.parse_args()
    
    # If no specific tests are selected, run all tests
    run_all = args.all or not (args.accessibility or args.api or args.performance or args.battery)
    
    # Create reports directory if it doesn't exist
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize results
    results = {}
    
    # Run accessibility tests
    if run_all or args.accessibility:
        print("\nRunning accessibility tests...")
        results["accessibility"] = run_test("test_accessibility.py", ["--url", args.url])
    
    # Run API tests
    if run_all or args.api:
        print("\nRunning API tests...")
        results["api"] = run_test("test_api.py", ["--url", args.url])
    
    # Run performance tests
    if run_all or args.performance:
        print("\nRunning performance tests...")
        results["performance"] = run_test("test_performance.py", ["--url", args.url])
    
    # Run battery simulation tests
    if run_all or args.battery:
        print("\nRunning battery simulation tests...")
        results["battery"] = run_test("test_battery_simulation.py", ["--url", args.url])
    
    # Record end time
    end_time = time.time()
    total_time = end_time - start_time
    
    # Print summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Timestamp: {timestamp}")
    
    for test, return_code in results.items():
        status = "PASSED" if return_code == 0 else "FAILED"
        print(f"{test}: {status} (return code: {return_code})")
    
    # Return non-zero if any test failed
    return 1 if any(rc != 0 for rc in results.values()) else 0


if __name__ == "__main__":
    sys.exit(main())