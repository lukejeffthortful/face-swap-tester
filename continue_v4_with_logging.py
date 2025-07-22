#!/usr/bin/env python3
"""
Continue V4 single face testing with comprehensive CSV logging
"""

import csv
import os
import time
import glob
import json
from datetime import datetime
from batch_test_single_face import perform_face_swap_v4, load_api_key

def initialize_csv_log():
    """Initialize CSV log file with headers"""
    csv_file = "v4_requests_log.csv"
    
    if not os.path.exists(csv_file):
        headers = [
            'timestamp',
            'request_id', 
            'source_image',
            'target_image',
            'combo_key',
            'source_file_size_kb',
            'target_file_size_kb',
            'source_base64_size_kb',
            'target_base64_size_kb',
            'total_payload_size_mb',
            'request_start_time',
            'request_end_time',
            'request_duration_seconds',
            'http_status_code',
            'success',
            'timeout_occurred',
            'error_type',
            'error_message',
            'response_content_length',
            'response_content_type',
            'api_generation_time',
            'api_remaining_credits',
            'api_request_id',
            'detection_face_order',
            'model_type',
            'swap_type',
            'hardware_type',
            'source_face_index',
            'target_face_index',
            'output_file_saved',
            'batch_number',
            'session_start_time'
        ]
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        print(f"📊 Created CSV log: {csv_file}")
    else:
        print(f"📊 Using existing CSV log: {csv_file}")
    
    return csv_file

def get_file_size_kb(file_path):
    """Get file size in KB"""
    try:
        return round(os.path.getsize(file_path) / 1024, 2)
    except:
        return 0

def get_base64_size_kb(base64_string):
    """Get base64 string size in KB"""
    try:
        return round(len(base64_string) / 1024, 2)
    except:
        return 0

def log_v4_request(csv_file, log_data):
    """Log V4 request to CSV"""
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        row = [
            log_data.get('timestamp', ''),
            log_data.get('request_id', ''),
            log_data.get('source_image', ''),
            log_data.get('target_image', ''),
            log_data.get('combo_key', ''),
            log_data.get('source_file_size_kb', ''),
            log_data.get('target_file_size_kb', ''),
            log_data.get('source_base64_size_kb', ''),
            log_data.get('target_base64_size_kb', ''),
            log_data.get('total_payload_size_mb', ''),
            log_data.get('request_start_time', ''),
            log_data.get('request_end_time', ''),
            log_data.get('request_duration_seconds', ''),
            log_data.get('http_status_code', ''),
            log_data.get('success', ''),
            log_data.get('timeout_occurred', ''),
            log_data.get('error_type', ''),
            log_data.get('error_message', ''),
            log_data.get('response_content_length', ''),
            log_data.get('response_content_type', ''),
            log_data.get('api_generation_time', ''),
            log_data.get('api_remaining_credits', ''),
            log_data.get('api_request_id', ''),
            log_data.get('detection_face_order', ''),
            log_data.get('model_type', ''),
            log_data.get('swap_type', ''),
            log_data.get('hardware_type', ''),
            log_data.get('source_face_index', ''),
            log_data.get('target_face_index', ''),
            log_data.get('output_file_saved', ''),
            log_data.get('batch_number', ''),
            log_data.get('session_start_time', '')
        ]
        writer.writerow(row)

def perform_v4_face_swap_with_logging(source_path, target_path, output_path, metadata_path, csv_file, batch_number, session_start_time):
    """Perform V4 face swap with comprehensive logging"""
    import requests
    import base64
    import traceback
    
    # Initialize log data
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'request_id': f"v4_{int(time.time()*1000)}",
        'source_image': os.path.basename(source_path),
        'target_image': os.path.basename(target_path),
        'combo_key': os.path.basename(output_path).replace('_v4_result.jpg', ''),
        'source_file_size_kb': get_file_size_kb(source_path),
        'target_file_size_kb': get_file_size_kb(target_path),
        'detection_face_order': 'big_to_small',
        'model_type': 'speed',
        'swap_type': 'face',
        'hardware_type': 'cost',
        'source_face_index': 0,
        'target_face_index': 0,
        'batch_number': batch_number,
        'session_start_time': session_start_time,
        'success': False,
        'timeout_occurred': False,
        'output_file_saved': False
    }
    
    try:
        API_KEY = load_api_key()
        API_URL = "https://api.segmind.com/v1/faceswap-v4"
        
        print(f"  📊 Logging request: {log_data['request_id']}")
        
        # Encode images and measure sizes
        with open(source_path, 'rb') as f:
            source_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open(target_path, 'rb') as f:
            target_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        log_data['source_base64_size_kb'] = get_base64_size_kb(source_base64)
        log_data['target_base64_size_kb'] = get_base64_size_kb(target_base64)
        log_data['total_payload_size_mb'] = round((log_data['source_base64_size_kb'] + log_data['target_base64_size_kb']) / 1024, 2)
        
        data = {
            "source_image": source_base64,
            "target_image": target_base64,
            "source_face_index": 0,
            "target_face_index": 0,
            "detection_face_order": "big_to_small",
            "model_type": "speed",
            "swap_type": "face",
            "hardware_type": "cost"
        }
        
        headers = {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Make request with timing
        log_data['request_start_time'] = datetime.now().isoformat()
        start_time = time.time()
        
        try:
            response = requests.post(API_URL, json=data, headers=headers, timeout=120)
            end_time = time.time()
            log_data['request_end_time'] = datetime.now().isoformat()
            log_data['request_duration_seconds'] = round(end_time - start_time, 3)
            
            # Log response details
            log_data['http_status_code'] = response.status_code
            log_data['response_content_length'] = len(response.content)
            log_data['response_content_type'] = response.headers.get('Content-Type', '')
            log_data['api_generation_time'] = response.headers.get('X-generation-time', '')
            log_data['api_remaining_credits'] = response.headers.get('X-remaining-credits', '')
            log_data['api_request_id'] = response.headers.get('X-Request-ID', '')
            
            if response.status_code == 200:
                # Success - save files
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # Save metadata
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "source_image": os.path.basename(source_path),
                    "target_image": os.path.basename(target_path),
                    "output_image": os.path.basename(output_path),
                    "api_version": "v4",
                    "api_endpoint": "faceswap-v4",
                    "test_type": "single_face",
                    "source_face_index": 0,
                    "target_face_index": 0,
                    "detection_face_order": "big_to_small",
                    "model_type": "speed",
                    "swap_type": "face",
                    "hardware_type": "cost",
                    "generation_time": response.headers.get('X-generation-time'),
                    "remaining_credits": response.headers.get('X-remaining-credits'),
                    "request_id": response.headers.get('X-Request-ID'),
                    "request_time": f"{log_data['request_duration_seconds']:.3f}",
                    "csv_log_id": log_data['request_id']
                }
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                log_data['success'] = True
                log_data['output_file_saved'] = True
                
                return True, log_data['api_generation_time']
            else:
                # HTTP error
                log_data['error_type'] = 'http_error'
                log_data['error_message'] = f"HTTP {response.status_code}: {response.text[:200]}"
                return False, None
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            log_data['request_end_time'] = datetime.now().isoformat()
            log_data['request_duration_seconds'] = round(end_time - start_time, 3)
            log_data['timeout_occurred'] = True
            log_data['error_type'] = 'timeout'
            log_data['error_message'] = 'Request timed out after 120 seconds'
            return False, None
            
        except Exception as e:
            end_time = time.time()
            log_data['request_end_time'] = datetime.now().isoformat()
            log_data['request_duration_seconds'] = round(end_time - start_time, 3)
            log_data['error_type'] = 'request_exception'
            log_data['error_message'] = str(e)[:200]
            return False, None
            
    except Exception as e:
        log_data['error_type'] = 'setup_error'
        log_data['error_message'] = str(e)[:200]
        return False, None
        
    finally:
        # Always log the request
        log_v4_request(csv_file, log_data)

def continue_v4_with_logging(max_tests=3):
    """Continue V4 testing with comprehensive logging"""
    
    # Initialize CSV logging
    csv_file = initialize_csv_log()
    session_start_time = datetime.now().isoformat()
    
    # Setup
    source_images = sorted(glob.glob("source-single-face/*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.png"))
    results_dir = "test-results/single-face-results"
    
    print(f"🎯 Continue V4 Single Face Testing with CSV Logging")
    print(f"Sources: {len(source_images)}, Targets: {len(target_images)}")
    print(f"📊 Logging to: {csv_file}")
    
    # Count existing requests in CSV to determine batch number
    batch_number = 1
    if os.path.exists(csv_file):
        with open(csv_file, 'r') as f:
            batch_number = len(list(csv.reader(f)))  # Include header in count
    
    # Find missing V4 tests
    missing_v4_tests = []
    for i, source_path in enumerate(source_images, 1):
        source_clean = f"source_{i:02d}"
        
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.splitext(os.path.basename(target_path))[0]
            combo_key = f"{source_clean}_to_{target_name}"
            
            v4_output_path = f"{results_dir}/{combo_key}_v4_result.jpg"
            if not os.path.exists(v4_output_path):
                missing_v4_tests.append({
                    'source_path': source_path,
                    'target_path': target_path,
                    'combo_key': combo_key,
                    'output_path': v4_output_path,
                    'metadata_path': f"{results_dir}/{combo_key}_v4_metadata.json"
                })
    
    total_v4_expected = len(source_images) * len(target_images)
    completed_v4 = total_v4_expected - len(missing_v4_tests)
    
    print(f"📊 V4 progress: {completed_v4}/{total_v4_expected} ({completed_v4/total_v4_expected*100:.1f}%)")
    print(f"⏳ Missing V4 tests: {len(missing_v4_tests)}")
    print(f"🔢 Starting batch: {batch_number}")
    
    if not missing_v4_tests:
        print("🎉 All V4 tests completed!")
        return
    
    # Run next batch of V4 tests
    tests_to_run = min(max_tests, len(missing_v4_tests))
    print(f"🚀 Running next {tests_to_run} V4 tests with logging...")
    
    successful = 0
    for i, test in enumerate(missing_v4_tests[:tests_to_run]):
        print(f"\n[{i+1}/{tests_to_run}] {test['combo_key']} (V4)")
        
        success, gen_time = perform_v4_face_swap_with_logging(
            test['source_path'], 
            test['target_path'], 
            test['output_path'], 
            test['metadata_path'],
            csv_file,
            batch_number + i,
            session_start_time
        )
        
        if success:
            successful += 1
            print(f"  ✅ Success ({gen_time}s)")
        else:
            print(f"  ❌ Failed (logged to CSV)")
        
        time.sleep(2)  # Rate limiting
    
    new_completed = completed_v4 + successful
    print(f"\n📊 Updated V4 progress: {new_completed}/{total_v4_expected} ({new_completed/total_v4_expected*100:.1f}%)")
    print(f"✅ This batch: {successful}/{tests_to_run} successful")
    print(f"📊 All requests logged to: {csv_file}")
    
    if new_completed < total_v4_expected:
        print(f"⏳ Still need {total_v4_expected - new_completed} more V4 tests")
    else:
        print("🎉 All V4 tests complete!")

if __name__ == "__main__":
    print("🔄 Continue V4 Single Face Testing with CSV Logging")
    print("=" * 55)
    continue_v4_with_logging(max_tests=3)