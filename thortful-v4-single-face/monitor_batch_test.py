#!/usr/bin/env python3
"""
Monitor the batch face swap test progress and periodically commit to GitHub
"""

import time
import subprocess
import os
from datetime import datetime
from pathlib import Path

def get_test_progress():
    """Get current test progress from CSV file"""
    csv_file = Path("logs/main_test_results.csv")
    if not csv_file.exists():
        return 0, 0
    
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    
    total_entries = len(lines) - 1  # Subtract header
    successful_entries = 0
    
    for line in lines[1:]:  # Skip header
        if ',True,' in line:  # Check success column
            successful_entries += 1
    
    return total_entries, successful_entries

def is_process_running(pid_file):
    """Check if the batch test process is still running"""
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        os.kill(pid, 0)
        return True
    except (FileNotFoundError, ProcessLookupError, ValueError):
        return False

def commit_to_github(total_tests, successful_tests):
    """Commit current results to GitHub"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True, cwd='.')
        
        # Create commit message
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        commit_msg = f"""Batch face swap testing progress: {total_tests} tests completed

- Tests completed: {total_tests}
- Successful: {successful_tests}
- Success rate: {success_rate:.1f}%
- Last update: {timestamp}
- Results viewable at: https://lukejeffthortful.github.io/face-swap-tester/thortful-v4-single-face/

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, cwd='.')
        
        # Push to GitHub
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, cwd='.')
        
        print(f"✅ Committed to GitHub: {total_tests} tests, {successful_tests} successful")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ GitHub commit failed: {e}")
        return False

def monitor_batch_test():
    """Monitor the batch test progress and commit periodically"""
    pid_file = "batch_test_pid.txt"
    last_commit_count = 0
    commit_interval = 10  # Commit every 10 new tests
    
    print("🔍 Starting batch test monitoring...")
    print("📊 Will check progress every 2 minutes")
    print("📤 Will commit to GitHub every 10 completed tests")
    print("=" * 60)
    
    while True:
        try:
            # Check if process is still running
            if not is_process_running(pid_file):
                print("🛑 Batch test process has stopped")
                break
            
            # Get current progress
            total_tests, successful_tests = get_test_progress()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"[{timestamp}] 📈 Progress: {total_tests} tests ({successful_tests} successful)")
            
            # Commit to GitHub if we have enough new tests
            if total_tests - last_commit_count >= commit_interval:
                if commit_to_github(total_tests, successful_tests):
                    last_commit_count = total_tests
            
            # Wait 2 minutes before next check
            time.sleep(120)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
            time.sleep(60)  # Wait 1 minute on error
    
    # Final commit when done
    total_tests, successful_tests = get_test_progress()
    if total_tests > last_commit_count:
        print("📤 Making final commit...")
        commit_to_github(total_tests, successful_tests)
    
    print(f"✅ Monitoring complete. Final results: {total_tests} tests, {successful_tests} successful")

if __name__ == "__main__":
    monitor_batch_test()