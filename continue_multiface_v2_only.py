#!/usr/bin/env python3
"""
Continue Multi-Face V2-ONLY testing with comprehensive CSV logging
Re-runs all V2 multi-face tests only, ignoring V4.3 results
"""

import csv
import os
import time
import glob
import json
import requests
import base64
import traceback
from datetime import datetime
from batch_test_single_face import load_api_key

def initialize_multiface_v2_csv_log():
    """Initialize CSV log file with headers for V2-only multi-face testing"""
    csv_file = "multiface_v2_only_requests_log.csv"
    
    if not os.path.exists(csv_file):
        headers = [
            'timestamp',
            'request_id',
            'source_image',
            'target_image',
            'combo_key',
            'api_version',
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
            'source_faces_index',
            'target_faces_index',
            'credits_used',
            'cost_per_request',
            'previous_credits',
            'output_file_saved',
            'batch_number',
            'session_start_time',
            'test_type',
            'api_endpoint_url',
            'face_restore',
            'face_upsample', 
            'codeformer_fidelity',
            'all_request_parameters_json'
        ]
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        print(f"📊 Created V2-only multi-face CSV log: {csv_file}")
    else:
        print(f"📊 Using existing V2-only multi-face CSV log: {csv_file}")
    
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

def get_last_credits_from_csv(csv_file):
    """Get the most recent remaining credits from CSV log"""
    if not os.path.exists(csv_file):
        return None
    
    try:
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            if len(lines) <= 1:  # Only header or empty
                return None
            
            # Get the last line and parse credits
            last_line = lines[-1].strip()
            if last_line:
                fields = last_line.split(',')
                # api_remaining_credits is at index 22 in our CSV
                if len(fields) > 22 and fields[22]:
                    return float(fields[22])
    except:
        pass
    return None

def calculate_cost_metrics(current_credits, previous_credits):
    """Calculate credits used and cost per request"""
    if previous_credits is None or current_credits is None:
        return None, None, previous_credits
    
    try:
        current_val = float(current_credits)
        previous_val = float(previous_credits)
        credits_used = previous_val - current_val
        
        # Assume $0.01 per credit (adjust based on actual pricing)
        cost_per_request = credits_used * 0.01 if credits_used > 0 else 0.0
        
        return credits_used, round(cost_per_request, 4), previous_val
    except:
        return None, None, previous_credits

def log_multiface_request(csv_file, log_data):
    """Log multi-face request to CSV"""
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        row = [
            log_data.get('timestamp', ''),
            log_data.get('request_id', ''),
            log_data.get('source_image', ''),
            log_data.get('target_image', ''),
            log_data.get('combo_key', ''),
            log_data.get('api_version', ''),
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
            log_data.get('source_faces_index', ''),
            log_data.get('target_faces_index', ''),
            log_data.get('credits_used', ''),
            log_data.get('cost_per_request', ''),
            log_data.get('previous_credits', ''),
            log_data.get('output_file_saved', ''),
            log_data.get('batch_number', ''),
            log_data.get('session_start_time', ''),
            log_data.get('test_type', ''),
            log_data.get('api_endpoint_url', ''),
            log_data.get('face_restore', ''),
            log_data.get('face_upsample', ''),
            log_data.get('codeformer_fidelity', ''),
            log_data.get('all_request_parameters_json', '')
        ]
        writer.writerow(row)

def perform_v2_multiface_swap_with_logging(source_path, target_path, output_path, metadata_path, csv_file, batch_number, session_start_time):
    """Perform V2 multi-face swap with comprehensive logging"""
    
    # Initialize log data
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'request_id': f"v2_multiface_{int(time.time()*1000)}",
        'source_image': os.path.basename(source_path),
        'target_image': os.path.basename(target_path),
        'combo_key': os.path.basename(output_path).replace('_v2_result.jpg', ''),
        'api_version': 'v2',
        'source_file_size_kb': get_file_size_kb(source_path),
        'target_file_size_kb': get_file_size_kb(target_path),
        'detection_face_order': 'N/A',
        'model_type': 'CodeFormer',
        'swap_type': 'face',
        'hardware_type': 'N/A',
        'source_faces_index': '0,1,2,3,4',
        'target_faces_index': '0,1,2,3,4',
        'batch_number': batch_number,
        'session_start_time': session_start_time,
        'success': False,
        'timeout_occurred': False,
        'output_file_saved': False,
        'test_type': 'multi_face',
        'api_endpoint_url': 'https://api.segmind.com/v1/faceswap-v2',
        'face_restore': 'codeformer-v0.1.0.pth',
        'face_upsample': 'N/A',
        'codeformer_fidelity': 'N/A'
    }
    
    try:
        API_KEY = load_api_key()
        API_URL = "https://api.segmind.com/v1/faceswap-v2"
        
        # Get previous credits for cost calculation
        previous_credits = get_last_credits_from_csv(csv_file)
        log_data['previous_credits'] = previous_credits
        
        print(f"  📊 Logging V2 request: {log_data['request_id']}")
        
        # Encode images and measure sizes
        with open(source_path, 'rb') as f:
            source_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open(target_path, 'rb') as f:
            target_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        log_data['source_base64_size_kb'] = get_base64_size_kb(source_base64)
        log_data['target_base64_size_kb'] = get_base64_size_kb(target_base64)
        log_data['total_payload_size_mb'] = round((log_data['source_base64_size_kb'] + log_data['target_base64_size_kb']) / 1024, 2)
        
        data = {
            "source_img": source_base64,
            "target_img": target_base64,
            "source_faces_index": [0, 1, 2, 3, 4],
            "target_faces_index": [0, 1, 2, 3, 4],
            "face_restore": "codeformer-v0.1.0.pth",
            "base64": False
        }
        
        # Log all request parameters (excluding base64 images for brevity)
        log_data['all_request_parameters_json'] = json.dumps({
            "source_faces_index": [0, 1, 2, 3, 4],
            "target_faces_index": [0, 1, 2, 3, 4], 
            "face_restore": "codeformer-v0.1.0.pth",
            "base64": False
        })
        
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
                # Calculate cost metrics
                current_credits = response.headers.get('X-remaining-credits')
                credits_used, cost_per_request, prev_credits = calculate_cost_metrics(
                    current_credits, previous_credits
                )
                log_data['credits_used'] = credits_used
                log_data['cost_per_request'] = cost_per_request
                
                # Success - save files
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # Save metadata
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "source_image": os.path.basename(source_path),
                    "target_image": os.path.basename(target_path),
                    "output_image": os.path.basename(output_path),
                    "api_version": "v2",
                    "api_endpoint": "faceswap-v2",
                    "test_type": "multi_face",
                    "source_faces_index": [0, 1, 2, 3, 4],
                    "target_faces_index": [0, 1, 2, 3, 4],
                    "face_restore": "codeformer-v0.1.0.pth",
                    "base64": False,
                    "generation_time": response.headers.get('X-generation-time'),
                    "remaining_credits": response.headers.get('X-remaining-credits'),
                    "request_id": response.headers.get('X-Request-ID'),
                    "request_time": f"{log_data['request_duration_seconds']:.3f}",
                    "csv_log_id": log_data['request_id'],
                    "credits_used": credits_used,
                    "cost_per_request": cost_per_request
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
        log_multiface_request(csv_file, log_data)

def continue_v2_only_multiface_testing(max_tests=10):
    """Continue V2-ONLY multi-face testing with comprehensive logging"""
    
    # Initialize CSV logging
    csv_file = initialize_multiface_v2_csv_log()
    session_start_time = datetime.now().isoformat()
    
    # Setup
    source_images = sorted(glob.glob("test-results/source-images/source_*.jpg"))
    target_images = sorted(glob.glob("test-results/multiface-target-images/target_*.png"))  # Multi-face targets
    results_dir = "test-results/results"
    
    print(f"🎯 Continue V2-ONLY Multi-Face Testing with CSV Logging")
    print(f"Sources: {len(source_images)}, Targets: {len(target_images)}")
    print(f"📊 Logging to: {csv_file}")
    
    # Count existing requests in CSV to determine batch number
    batch_number = 1
    if os.path.exists(csv_file):
        with open(csv_file, 'r') as f:
            batch_number = len(list(csv.reader(f)))  # Include header in count
    
    # Find ALL V2 tests to re-run (ignore existing results)
    all_v2_tests = []
    
    for i, source_path in enumerate(source_images, 1):
        source_name = f"source_{i:02d}"
        
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.splitext(os.path.basename(target_path))[0]
            combo_key = f"{source_name}_to_{target_name}"
            
            # Always add V2 test (re-run all V2 results)
            v2_output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
            all_v2_tests.append({
                'source_path': source_path,
                'target_path': target_path,
                'combo_key': combo_key,
                'output_path': v2_output_path,
                'metadata_path': f"{results_dir}/{combo_key}_v2_metadata.json",
                'api_version': 'v2'
            })
    
    total_v2_tests = len(all_v2_tests)
    
    print(f"📊 Total V2 tests to run: {total_v2_tests}")
    print(f"🔢 Starting batch: {batch_number}")
    
    if not all_v2_tests:
        print("❌ No V2 tests found to run!")
        return
    
    # Run next batch of V2 tests
    tests_to_run = min(max_tests, len(all_v2_tests))
    print(f"🚀 Running next {tests_to_run} V2-only multi-face tests with logging...")
    
    successful = 0
    for i, test in enumerate(all_v2_tests[:tests_to_run]):
        print(f"\n[{i+1}/{tests_to_run}] {test['combo_key']} (V2 multi-face)")
        
        success, gen_time = perform_v2_multiface_swap_with_logging(
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
        
        time.sleep(3)  # Rate limiting between requests
    
    print(f"\n📊 Batch completed: {successful}/{tests_to_run} successful")
    print(f"📊 All V2 requests logged to: {csv_file}")
    
    remaining_tests = total_v2_tests - tests_to_run
    if remaining_tests > 0:
        print(f"⏳ Still need {remaining_tests} more V2 tests")
        print(f"💡 Run script again to continue with next batch")
    else:
        print("🎉 All V2-only multi-face tests complete!")

if __name__ == "__main__":
    print("🔄 Continue V2-ONLY Multi-Face Testing with CSV Logging")
    print("=" * 60)
    continue_v2_only_multiface_testing(max_tests=10)