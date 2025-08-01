#!/usr/bin/env python3
"""
Single Face Technical Verification Script
Quick verification that single face swap API is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'auth'))

import requests
import json
import base64
import csv
import time
from datetime import datetime
from pathlib import Path
from thortful_auth import get_thortful_auth

# Configuration
API_ENDPOINT = "https://www.thortful.com/api/v1/faceswap?variation=true"
SOURCE_DIR = Path("../source-images")
TARGET_DIR = Path("../target-images")
RESULTS_DIR = Path("../results")
LOGS_DIR = Path("../logs")
LOG_FILE = LOGS_DIR / "verification_results.csv"

# Single test card ID
TEST_CARD_ID = "67816ae75990fc276575cd07"  # card_template_01

def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in [SOURCE_DIR, TARGET_DIR, RESULTS_DIR, LOGS_DIR]:
        directory.mkdir(exist_ok=True)

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_csv_header():
    """Create CSV log file with headers if it doesn't exist"""
    if not LOG_FILE.exists():
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'timestamp', 'source_image', 'card_id', 'result_image',
                'api_version', 'test_type', 'success', 'generation_time_seconds',
                'request_time_seconds', 'error_message', 'status'
            ])

def run_verification_test(source_path, auth_headers):
    """Run a single verification test"""
    start_time = time.time()
    
    try:
        print(f"🔍 Verifying with {source_path.name}...")
        
        # Encode source image
        source_base64 = encode_image_to_base64(source_path)
        
        payload = {
            "source_image": source_base64,
            "targetCardId": TEST_CARD_ID,
            "target_card_id": TEST_CARD_ID
        }
        
        response = requests.post(
            API_ENDPOINT,
            headers=auth_headers,
            json=payload,
            timeout=180
        )
        
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            result_data = response.json()
            
            # Save result image
            result_filename = f"verification_{source_path.stem}_result.jpg"
            result_path = RESULTS_DIR / result_filename
            
            if 'image' in result_data:
                result_image_data = base64.b64decode(result_data['image'])
                with open(result_path, 'wb') as f:
                    f.write(result_image_data)
                
                print(f"✅ VERIFICATION PASSED - API is working correctly!")
                print(f"📸 Result saved: {result_filename}")
                print(f"⏱️  Processing time: {request_time:.2f}s")
                
                return {
                    'success': True,
                    'result_image': result_filename,
                    'generation_time': f"{request_time:.3f}",
                    'request_time': f"{request_time:.3f}",
                    'error_message': '',
                    'status': 'PASSED'
                }
            else:
                print(f"⚠️  No image returned in response")
                return {
                    'success': False,
                    'result_image': 'no_image',
                    'generation_time': f"{request_time:.3f}",
                    'request_time': f"{request_time:.3f}",
                    'error_message': 'No image in response',
                    'status': 'FAILED'
                }
        else:
            print(f"❌ VERIFICATION FAILED - API Error {response.status_code}")
            return {
                'success': False,
                'result_image': 'error',
                'generation_time': 'error',
                'request_time': f"{request_time:.3f}",
                'error_message': f"HTTP {response.status_code}: {response.text[:100]}",
                'status': 'FAILED'
            }
            
    except Exception as e:
        request_time = time.time() - start_time
        print(f"❌ VERIFICATION FAILED - Exception: {str(e)}")
        return {
            'success': False,
            'result_image': 'exception',
            'generation_time': 'exception',
            'request_time': f"{request_time:.3f}",
            'error_message': str(e),
            'status': 'FAILED'
        }

def log_verification_result(source_path, result_data):
    """Log verification result to CSV file"""
    timestamp = datetime.now().isoformat()
    
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp, source_path.name, TEST_CARD_ID,
            result_data['result_image'], 'v4-thortful', 'technical_verification',
            result_data['success'], result_data['generation_time'],
            result_data['request_time'], result_data['error_message'],
            result_data['status']
        ])

def main():
    """Main function to run verification test"""
    print("🔍 Single Face Technical Verification")
    print("=" * 50)
    
    ensure_directories()
    create_csv_header()
    
    # Get authentication
    print("🔐 Getting Thortful authentication...")
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Authentication failed - cannot proceed")
        return
    
    # Get first source image for testing
    source_images = list(SOURCE_DIR.glob('*.jpg'))
    if not source_images:
        print(f"❌ No source images found in {SOURCE_DIR}")
        return
    
    # Use first source image for verification
    test_source = source_images[0]
    print(f"🎯 Using {test_source.name} for verification test")
    
    # Run verification
    result_data = run_verification_test(test_source, auth_headers)
    
    # Log result
    log_verification_result(test_source, result_data)
    
    # Summary
    print(f"\n{'='*50}")
    if result_data['success']:
        print("🎉 VERIFICATION SUCCESSFUL - API is working!")
        print("✅ Single face swap functionality confirmed")
        print("🚀 Ready for batch testing")
    else:
        print("💥 VERIFICATION FAILED - API issues detected")
        print("❌ Single face swap not working properly")
        print("🔧 Check authentication and API status")
    
    print(f"📋 Full details logged to: {LOG_FILE}")

if __name__ == "__main__":
    main()