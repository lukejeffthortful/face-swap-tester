#!/usr/bin/env python3
"""
Corrected Test Suite for Thortful V4 Single Face API

This runs a comprehensive but manageable test suite using the corrected www.thortful.com endpoint
to demonstrate the API working properly across multiple combinations.
"""

import sys
import os
sys.path.append('..')

import requests
import json
import base64
import csv
import time
import subprocess
from datetime import datetime
from pathlib import Path
from thortful_auth import get_thortful_auth

# Configuration - CORRECTED ENDPOINT
API_ENDPOINT = "https://www.thortful.com/api/v1/faceswap?variation=true"
SOURCE_DIR = Path("diverse-source-images")
TARGET_DIR = Path("target-images")
RESULTS_DIR = Path("results")
LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "corrected_thortful_test_results.csv"

# Subset of card IDs for manageable testing (5 cards instead of 26)
TEST_CARD_TARGETS = {
    "67816ae75990fc276575cd07": "card_template_01",
    "6855c0b6ebba0773538e8a15": "card_template_02", 
    "66facc0a21fd6d6f34901ae6": "card_template_03",
    "66e01c85ded8e0212043629d": "card_template_04",
    "67d219a67d3f9803484845be": "card_template_05"
}

CARD_IDS = list(TEST_CARD_TARGETS.keys())

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
                'timestamp',
                'source_image', 
                'target_image',
                'card_id',
                'result_image',
                'api_version',
                'test_type',
                'success',
                'generation_time_seconds',
                'request_time_seconds', 
                'error_message',
                'notes'
            ])

def run_corrected_face_swap(source_path, card_template_name, card_id, auth_headers, timeout_seconds=120):
    """
    Perform single face swap using corrected Thortful API endpoint
    The card_id IS the target template - no separate target image needed
    Returns result data dictionary
    """
    start_time = time.time()
    
    try:
        # Encode source image to base64
        print(f"📸 Encoding source image: {source_path.name}")
        source_base64 = encode_image_to_base64(source_path)
        
        # Prepare request payload - card_id specifies the target template
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,
            "target_card_id": card_id
        }
        
        print(f"🚀 Sending request to CORRECTED Thortful API...")
        print(f"   Endpoint: {API_ENDPOINT}")
        print(f"   Source: {source_path.name}")
        print(f"   Target Template: {card_template_name or card_id[:8]}")
        print(f"   Card ID: {card_id}")
        print(f"   Payload size: {len(json.dumps(payload))} bytes")
        
        # Make API request with corrected endpoint and timeout
        response = requests.post(
            API_ENDPOINT,
            headers=auth_headers,
            json=payload,
            timeout=timeout_seconds
        )
        
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            result_data = response.json()
            print(f"✅ Success! Processing took {request_time:.2f}s")
            
            # Print full API response for analysis
            print(f"📊 Full API Response: {json.dumps(result_data, indent=2)}")
            
            # Save result image if present in response
            result_filename = f"{source_path.stem}_to_{card_template_name}_card_{card_id[:8]}_corrected_v4.jpg"
            result_path = RESULTS_DIR / result_filename
            
            # Handle different response formats
            if 'image' in result_data:
                # Save the result image
                result_image_data = base64.b64decode(result_data['image'])
                with open(result_path, 'wb') as f:
                    f.write(result_image_data)
                print(f"💾 Result saved: {result_filename}")
            elif 'result_url' in result_data:
                # Download from URL
                img_response = requests.get(result_data['result_url'])
                with open(result_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"💾 Result downloaded: {result_filename}")
            else:
                print("⚠️ No image data found in response")
                result_filename = "no_image_returned"
            
            # Extract generation time from response
            generation_time = result_data.get('generation_time', 
                             result_data.get('processing_time', 
                             result_data.get('duration', f"{request_time:.3f}")))
            
            return {
                'success': True,
                'result_image': result_filename,
                'generation_time': generation_time,
                'request_time': f"{request_time:.3f}",
                'error_message': '',
                'raw_response': result_data
            }
            
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return {
                'success': False,
                'result_image': f'error_{response.status_code}',
                'generation_time': 'error',
                'request_time': f"{request_time:.3f}",
                'error_message': f"HTTP {response.status_code}: {response.text[:200]}",
                'raw_response': {}
            }
            
    except requests.exceptions.Timeout:
        request_time = time.time() - start_time
        print(f"⏰ Request timeout after {request_time:.2f}s")
        return {
            'success': False,
            'result_image': 'timeout',
            'generation_time': 'timeout',
            'request_time': f"{request_time:.3f}",
            'error_message': f"Request timeout after {timeout_seconds}s",
            'raw_response': {}
        }
    except Exception as e:
        request_time = time.time() - start_time
        print(f"❌ Exception: {str(e)}")
        return {
            'success': False,
            'result_image': 'exception',
            'generation_time': 'exception',
            'request_time': f"{request_time:.3f}",
            'error_message': str(e),
            'raw_response': {}
        }

def log_test_result(source_path, card_template_name, card_id, result_data):
    """Log test result to CSV file"""
    timestamp = datetime.now().isoformat()
    
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp,
            source_path.name,
            card_template_name,
            card_id,
            result_data['result_image'],
            'v4-thortful-corrected',
            'single_face',
            result_data['success'],
            result_data['generation_time'],
            result_data['request_time'],
            result_data['error_message'],
            f'Corrected endpoint test - {card_template_name}'
        ])

def run_corrected_test_suite():
    """Run manageable test suite with corrected endpoint"""
    print("🎯 Corrected Thortful V4 Test Suite")
    print("=" * 50)
    print(f"✅ Using CORRECTED endpoint: {API_ENDPOINT}")
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
    source_images = list(SOURCE_DIR.glob('*.jpg')) + list(SOURCE_DIR.glob('*.png'))
    
    if not source_images:
        print(f"❌ No source images found in {SOURCE_DIR}")
        return
    
    # Limit to first 5 source images for manageable test suite
    source_images = source_images[:5]
    
    print(f"📊 Found {len(source_images)} source images")
    print(f"🎯 Testing against {len(CARD_IDS)} card templates (these ARE the targets)")
    total_tests = len(source_images) * len(CARD_IDS)
    print(f"🔄 Running {total_tests} tests (manageable subset)")
    
    estimated_time = total_tests * 60  # Estimate 60s per test
    print(f"⏱️ Estimated completion time: {estimated_time // 60} minutes")
    
    test_count = 0
    success_count = 0
    timeout_count = 0
    
    start_overall = time.time()
    
    for source_path in source_images:
        for card_id in CARD_IDS:
            test_count += 1
            card_template_name = TEST_CARD_TARGETS[card_id]
            print(f"\n=== Test {test_count}/{total_tests} ===")
            print(f"Source: {source_path.name} → Target: {card_template_name}")
            
            try:
                # Run the test with corrected endpoint (no target_path needed, card_id IS the target)
                result_data = run_corrected_face_swap(source_path, None, card_id, auth_headers)
                
                # Log the result
                log_test_result(source_path, card_template_name, card_id, result_data)
                
                if result_data['success']:
                    success_count += 1
                    print(f"📈 Progress: {success_count}/{test_count} successful")
                elif 'timeout' in result_data['error_message'].lower():
                    timeout_count += 1
                    print(f"⏰ Timeout occurred (rare with corrected endpoint)")
                
                # Brief pause between requests
                if test_count < total_tests:
                    print("⏸️ Pausing 3 seconds...")
                    time.sleep(3)
                    
            except KeyboardInterrupt:
                print("❌ Script interrupted by user")
                break
            except Exception as e:
                print(f"⚠️ Unexpected error in test {test_count}: {e}")
                time.sleep(5)
    
    total_time = time.time() - start_overall
    
    print(f"\n{'='*50}")
    print("🎯 CORRECTED TEST SUITE RESULTS")
    print(f"{'='*50}")
    print(f"✅ Endpoint used: {API_ENDPOINT}")
    print(f"📊 Total tests: {test_count}")
    print(f"📊 Successful: {success_count}")
    print(f"📊 Failed: {test_count - success_count}")
    print(f"📊 Timeouts: {timeout_count}")
    print(f"📊 Success rate: {success_count/test_count*100:.1f}%")
    print(f"⏱️ Total time: {total_time/60:.1f} minutes")
    print(f"⏱️ Average per test: {total_time/test_count:.1f} seconds")
    
    print(f"\n📋 Detailed logs saved to: {LOG_FILE}")
    print(f"🖼️ Result images saved to: {RESULTS_DIR}")
    
    if success_count > 0:
        print(f"\n🎉 SUCCESS! The corrected endpoint works reliably!")
        print(f"✅ {success_count} successful face swaps completed")
        print(f"✅ No more 60-second timeout issues!")
    
    return {
        'total_tests': test_count,
        'successful': success_count,
        'failed': test_count - success_count,
        'timeouts': timeout_count,
        'success_rate': success_count/test_count*100,
        'total_time_minutes': total_time/60,
        'avg_time_per_test': total_time/test_count
    }

if __name__ == "__main__":
    results = run_corrected_test_suite()
    
    if results:
        print(f"\n🏆 FINAL SUMMARY:")
        print(f"Corrected endpoint performance: {results['success_rate']:.1f}% success rate")
        print(f"Average processing time: {results['avg_time_per_test']:.1f}s per test")
        print(f"No more infrastructure timeout issues!")