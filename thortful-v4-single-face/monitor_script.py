#!/usr/bin/env python3
"""
Monitor Script for Thortful Face Swap Testing

Run this script to check the status of the testing process.
Usage: python3 monitor_script.py
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def check_script_status():
    """Check if the testing script is currently running"""
    try:
        # Check for running python processes with our script name
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        running_scripts = []
        for line in processes.split('\n'):
            if 'thortful_test_single_face.py' in line and 'grep' not in line:
                running_scripts.append(line.strip())
        
        return running_scripts
    except Exception as e:
        print(f"Error checking process status: {e}")
        return []

def check_log_files():
    """Check recent activity in log files"""
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print("❌ Logs directory not found")
        return
    
    # Check status log
    status_log = logs_dir / "script_status.log"
    error_log = logs_dir / "errors.log"
    csv_log = logs_dir / "thortful_diverse_face_tests.csv"
    
    print("\n📊 LOG FILE STATUS:")
    print("=" * 50)
    
    # Check main CSV log
    if csv_log.exists():
        stat = csv_log.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        time_diff = datetime.now() - modified_time
        
        print(f"📋 Test Results CSV:")
        print(f"   Last modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Time since last update: {time_diff}")
        
        # Count lines to get test count
        try:
            with open(csv_log, 'r') as f:
                lines = f.readlines()
                test_count = len(lines) - 1  # Subtract header
                print(f"   Total tests logged: {test_count}")
                
                if lines and len(lines) > 1:
                    last_line = lines[-1].strip()
                    parts = last_line.split(',')
                    if len(parts) >= 8:
                        success = parts[7] == 'True'
                        timestamp = parts[0]
                        status_emoji = "✅" if success else "❌"
                        print(f"   Last test: {status_emoji} {timestamp}")
        except Exception as e:
            print(f"   Error reading CSV: {e}")
    else:
        print("❌ Test results CSV not found")
    
    # Check status log
    if status_log.exists():
        print(f"\n📝 Status Log:")
        try:
            with open(status_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    # Show last 5 status messages
                    print("   Recent status messages:")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
                else:
                    print("   No status messages found")
        except Exception as e:
            print(f"   Error reading status log: {e}")
    else:
        print("📝 No status log found")
    
    # Check error log
    if error_log.exists():
        print(f"\n🚨 Error Log:")
        try:
            with open(error_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    print("   Recent errors:")
                    for line in lines[-3:]:  # Show last 3 errors
                        print(f"   {line.strip()}")
                else:
                    print("   No errors logged")
        except Exception as e:
            print(f"   Error reading error log: {e}")
    else:
        print("✅ No error log found (good!)")

def main():
    print("🔍 THORTFUL TESTING MONITOR")
    print("=" * 50)
    print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if script is running
    running_processes = check_script_status()
    
    print(f"\n🔄 SCRIPT STATUS:")
    if running_processes:
        print("✅ Testing script is currently RUNNING")
        for process in running_processes:
            print(f"   {process}")
    else:
        print("❌ Testing script is NOT running")
        print("   To start it: python3 thortful_test_single_face.py")
    
    # Check log files
    check_log_files()
    
    print(f"\n🌐 DASHBOARD:")
    print("   https://lukejeffthortful.github.io/face-swap-tester/thortful-v4-single-face/")
    
    print(f"\n💡 MONITORING TIPS:")
    print("   - Run this monitor script periodically to check status")
    print("   - Check the error log if tests aren't progressing")
    print("   - The script will auto-stop after 10 consecutive failures")
    print("   - CSV file should update every successful test")
    print("   - GitHub commits happen every 2 tests")

if __name__ == "__main__":
    main()