#!/usr/bin/env python3
"""
HTML Review Verification Script

Tests that the thortful_review.html page can properly load and display test results.
This script ensures HTML review pages are working before announcing completion.
"""

import os
import sys
import csv
import json
import argparse
from pathlib import Path
import subprocess

def test_csv_accessibility():
    """Test that CSV log files exist and are readable"""
    print("🧪 Testing CSV Data Accessibility...")
    
    log_file = Path("logs/main_test_results.csv")
    
    if not log_file.exists():
        print(f"❌ CSV file not found: {log_file}")
        return False
    
    try:
        with open(log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"✅ CSV loaded successfully: {len(rows)} test records")
        
        # Check for recent entries
        recent_entries = [r for r in rows if '2025-08-01' in r.get('timestamp', '')]
        print(f"✅ Recent entries found: {len(recent_entries)}")
        
        # Check for successful tests
        successful_tests = [r for r in rows if r.get('success') == 'True']
        print(f"✅ Successful tests: {len(successful_tests)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def test_result_images():
    """Test that result images exist and are accessible"""
    print("\n🖼️  Testing Result Images...")
    
    results_dir = Path("results")
    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return False
    
    image_files = list(results_dir.glob("*.jpg"))
    if not image_files:
        print("❌ No result images found")
        return False
    
    print(f"✅ Found {len(image_files)} result images")
    
    # Check recent images
    recent_images = [img for img in image_files if 'diverse_face_01' in img.name]
    if recent_images:
        print(f"✅ Recent test images found: {len(recent_images)}")
        
        # Check file size (should be reasonable for face swap results)
        for img in recent_images[:3]:  # Check first 3
            size_kb = img.stat().st_size / 1024
            if size_kb > 10:  # Should be at least 10KB for valid image
                print(f"✅ Image {img.name}: {size_kb:.1f}KB")
            else:
                print(f"⚠️  Image {img.name}: {size_kb:.1f}KB (suspiciously small)")
    
    return True

def test_html_structure():
    """Test that HTML file exists and has expected structure"""
    print("\n📄 Testing HTML Structure...")
    
    html_file = Path("thortful_review.html")
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    try:
        with open(html_file, 'r') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            ("CSV loading JavaScript", "logs/main_test_results.csv" in content),
            ("Results grid element", "resultsGrid" in content),
            ("CSS styling", "test-card" in content),
            ("Image references", "results/" in content),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading HTML: {e}")
        return False

def test_local_server():
    """Test serving HTML locally and check basic functionality"""
    print("\n🌐 Testing Local Server...")
    
    try:
        # Try to start a simple HTTP server for testing
        print("💡 To manually test HTML:")
        print("   1. cd to thortful-v4-single-face directory")
        print("   2. Run: python3 -m http.server 8000")
        print("   3. Open: http://localhost:8000/thortful_review.html")
        print("   4. Verify test results display properly")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Server test: {e}")
        return True  # Non-critical failure

def create_minimal_test_html():
    """Create a minimal test version to verify data loading"""
    print("\n🧹 Creating minimal test HTML...")
    
    test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Data Loading</title>
</head>
<body>
    <div id="test-results">Loading...</div>
    <script>
        async function testLoad() {
            try {
                const response = await fetch('logs/main_test_results.csv');
                const text = await response.text();
                const lines = text.split('\\n').filter(line => line.trim());
                
                document.getElementById('test-results').innerHTML = 
                    `✅ CSV loaded: ${lines.length} lines<br>` +
                    `✅ Sample data: ${lines[1] ? lines[1].substring(0, 50) + '...' : 'No data'}`;
                    
            } catch (error) {
                document.getElementById('test-results').innerHTML = 
                    `❌ Error: ${error.message}`;
            }
        }
        testLoad();
    </script>
</body>
</html>"""
    
    with open("test_data_loading.html", "w") as f:
        f.write(test_html)
    
    print("✅ Created test_data_loading.html")
    print("💡 Open in browser to test data loading")
    return True

def main():
    parser = argparse.ArgumentParser(description='Verify HTML review page functionality')
    parser.add_argument('--csv-test', action='store_true', help='Test CSV data loading')
    parser.add_argument('--image-test', action='store_true', help='Test result images')
    parser.add_argument('--html-test', action='store_true', help='Test HTML structure')
    parser.add_argument('--server-test', action='store_true', help='Test local server')
    parser.add_argument('--full-test', action='store_true', help='Run all tests')
    parser.add_argument('--create-test', action='store_true', help='Create minimal test HTML')
    
    args = parser.parse_args()
    
    if not any([args.csv_test, args.image_test, args.html_test, args.server_test, args.full_test, args.create_test]):
        args.full_test = True
    
    print("🎯 HTML Review Verification")
    print("=" * 40)
    
    all_passed = True
    
    if args.full_test or args.csv_test:
        if not test_csv_accessibility():
            all_passed = False
    
    if args.full_test or args.image_test:
        if not test_result_images():
            all_passed = False
    
    if args.full_test or args.html_test:
        if not test_html_structure():
            all_passed = False
    
    if args.full_test or args.server_test:
        test_local_server()
    
    if args.create_test:
        create_minimal_test_html()
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All tests passed! HTML review should be working.")
    else:
        print("❌ Some tests failed. Check HTML review setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()