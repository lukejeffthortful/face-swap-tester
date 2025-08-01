#!/usr/bin/env python3
"""
Single Face Batch Testing Script
Runs comprehensive single face swap tests using diverse source faces
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
LOG_FILE = LOGS_DIR / "batch_test_results.csv"

# Card mapping for target templates
CARD_TARGETS = {
    "67816ae75990fc276575cd07": "card_template_01",
    "6855c0b6ebba0773538e8a15": "card_template_02"
}

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
                'timestamp', 'source_image', 'target_template', 'card_id',
                'result_image', 'api_version', 'test_type', 'success',
                'generation_time_seconds', 'request_time_seconds', 
                'error_message', 'notes'
            ])

def run_single_face_swap(source_path, card_id, auth_headers):
    """Perform single face swap using Thortful API"""
    start_time = time.time()
    
    try:
        # Encode source image to base64
        source_base64 = encode_image_to_base64(source_path)
        
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,
            "target_card_id": card_id
        }
        
        print(f"🚀 Testing {source_path.name} with card {card_id[:8]}...")
        
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
            result_filename = f"{source_path.stem}_to_{CARD_TARGETS[card_id]}_card_{card_id[:8]}.jpg"
            result_path = RESULTS_DIR / result_filename
            
            if 'image' in result_data:
                result_image_data = base64.b64decode(result_data['image'])
                with open(result_path, 'wb') as f:
                    f.write(result_image_data)
                print(f"✅ Success! Saved {result_filename}")
            
            return {
                'success': True,
                'result_image': result_filename,
                'generation_time': f"{request_time:.3f}",  
                'request_time': f"{request_time:.3f}",
                'error_message': ''
            }
        else:
            print(f"❌ API Error {response.status_code}")
            return {
                'success': False,
                'result_image': 'error',
                'generation_time': 'error',
                'request_time': f"{request_time:.3f}",
                'error_message': f"HTTP {response.status_code}: {response.text[:100]}"
            }
            
    except Exception as e:
        request_time = time.time() - start_time
        print(f"❌ Exception: {str(e)}")
        return {
            'success': False,
            'result_image': 'exception',
            'generation_time': 'exception', 
            'request_time': f"{request_time:.3f}",
            'error_message': str(e)
        }

def log_test_result(source_path, card_id, result_data):
    """Log test result to CSV file"""
    timestamp = datetime.now().isoformat()
    target_template = CARD_TARGETS.get(card_id, f"card_template_{card_id[:8]}")
    
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp, source_path.name, target_template, card_id,
            result_data['result_image'], 'v4-thortful', 'single_face_batch',
            result_data['success'], result_data['generation_time'],
            result_data['request_time'], result_data['error_message'],
            f'Single face batch test - {target_template}'
        ])

def main():
    """Main function to run batch tests"""
    print("🧪 Single Face Batch Testing")
    print("=" * 50)
    
    ensure_directories()
    create_csv_header()
    
    # Get authentication
    print("🔐 Getting Thortful authentication...")
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Failed to get authentication headers")
        return
    
    # Get source images
    source_images = list(SOURCE_DIR.glob('*.jpg'))
    if not source_images:
        print(f"❌ No source images found in {SOURCE_DIR}")
        return
    
    card_ids = list(CARD_TARGETS.keys())
    total_tests = len(source_images) * len(card_ids)
    
    print(f"📊 Found {len(source_images)} source images")
    print(f"🎯 Testing against {len(card_ids)} card templates")
    print(f"🔄 Running {total_tests} tests...")
    
    test_count = 0
    success_count = 0
    
    for source_path in source_images:
        for card_id in card_ids:
            test_count += 1
            print(f"\n=== Test {test_count}/{total_tests} ===")
            
            # Run the test
            result_data = run_single_face_swap(source_path, card_id, auth_headers)
            
            # Log the result
            log_test_result(source_path, card_id, result_data)
            
            if result_data['success']:
                success_count += 1
            
            # Brief pause between requests
            time.sleep(1)
    
    print(f"\n✅ Batch testing complete!")
    print(f"📊 Results: {success_count}/{test_count} successful")
    print(f"📋 Detailed logs saved to: {LOG_FILE}")
    print(f"🖼️  Result images saved to: {RESULTS_DIR}")

if __name__ == "__main__":
    main()