#!/usr/bin/env python3
"""
Clean the main_test_results.csv to only include entries with existing files
"""

import csv
import os
from pathlib import Path

def clean_csv():
    # Read existing CSV
    with open('logs/main_test_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f'Original CSV has {len(rows)} entries')

    # Filter to only include entries where:
    # 1. Source image exists in source-images/
    # 2. Result image exists in results/ (if success=True)
    valid_rows = []
    source_dir = Path('source-images')
    results_dir = Path('results')

    for row in rows:
        source_path = source_dir / row['source_image']
        
        # Check if source image exists
        if not source_path.exists():
            print(f"❌ Source image missing: {row['source_image']}")
            continue
        
        # If it's a successful test, check if result image exists
        if row['success'] == 'True' and row['result_image'] != 'error':
            result_path = results_dir / row['result_image']
            if not result_path.exists():
                print(f"❌ Result image missing: {row['result_image']}")
                continue
        
        valid_rows.append(row)

    print(f'Filtered CSV has {len(valid_rows)} valid entries')

    # Create backup
    with open('logs/main_test_results.csv.backup', 'w') as f:
        with open('logs/main_test_results.csv', 'r') as original:
            f.write(original.read())

    # Write cleaned CSV
    with open('logs/main_test_results.csv', 'w', newline='') as f:
        if valid_rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(valid_rows)
        else:
            # Keep header only
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()

    print('✅ CSV cleaned - backup saved as main_test_results.csv.backup')
    
    # Show what's left
    print(f"\n📊 Remaining entries:")
    for row in valid_rows:
        status = "✅" if row['success'] == 'True' else "❌"
        print(f"  {status} {row['source_image']} -> {row['result_image']}")

if __name__ == "__main__":
    clean_csv()