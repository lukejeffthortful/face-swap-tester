#!/usr/bin/env python3
"""
Debug Test Script for 5 Face Swaps with Comprehensive Logging

This script runs exactly 5 face swap tests with detailed logging
to help engineers replicate timeout and performance issues.
"""

import sys
import os
sys.path.append('..')

import requests
import json
import base64
import time
from datetime import datetime
from pathlib import Path
from thortful_auth import get_thortful_auth

# Configuration
API_ENDPOINT = "https://www.thortful.com/api/v1/faceswap?variation=true"
SOURCE_DIR = Path("diverse-source-images")
TARGET_DIR = Path("target-images")
DEBUG_LOG_FILE = Path("logs/debug_5_swaps.json")

# Test 5 different card IDs for variety
TEST_CARD_IDS = [
    "67816ae75990fc276575cd07",  # card_template_01
    "6855c0b6ebba0773538e8a15",  # card_template_02
    "66facc0a21fd6d6f34901ae6",  # card_template_03
    "66e01c85ded8e0212043629d",  # card_template_04
    "67d219a67d3f9803484845be"   # card_template_05
]

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def log_detailed_request(test_num, request_data, response_data, timing_data, error_data=None):
    """Log comprehensive test data for replication"""
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    log_entry = {
        "test_number": test_num,
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform,
            "script_location": str(Path(__file__).absolute())
        },
        "api_configuration": {
            "endpoint": API_ENDPOINT,
            "method": "POST",
            "timeout_seconds": 180,
            "max_retries": 3
        },
        "request_details": {
            "headers": {
                # Sanitize auth headers for logging (keep structure but hide sensitive data)
                key: "***REDACTED***" if "auth" in key.lower() or "token" in key.lower() or "key" in key.lower()
                else value for key, value in request_data.get("headers", {}).items()
            },
            "payload_structure": {
                "source_image": f"base64_string_length_{len(request_data.get('payload', {}).get('source_image', ''))}",
                "targetCardId": request_data.get("payload", {}).get("targetCardId"),
                "target_card_id": request_data.get("payload", {}).get("target_card_id"),
                "payload_size_bytes": len(json.dumps(request_data.get("payload", {})))
            },
            "source_image_info": request_data.get("source_info", {}),
            "target_image_info": request_data.get("target_info", {})
        },
        "timing": timing_data,
        "response_details": response_data,
        "error_details": error_data,
        "replication_notes": {
            "exact_curl_equivalent": f"""
curl -X POST "{API_ENDPOINT}" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: [YOUR_AUTH_HEADER]" \\
  --data '{{"source_image":"[BASE64_IMAGE]","targetCardId":"{request_data.get('payload', {}).get('targetCardId')}","target_card_id":"{request_data.get('payload', {}).get('targetCardId')}"}}' \\
  --max-time 180
            """.strip(),
            "python_requests_equivalent": """
import requests
response = requests.post(
    "https://api.thortful.com/v1/faceswap?variation=true",
    headers=auth_headers,
    json=payload,
    timeout=180
)
            """.strip()
        }
    }
    
    # Append to debug log file
    debug_logs = []
    if DEBUG_LOG_FILE.exists():
        try:
            with open(DEBUG_LOG_FILE, 'r') as f:
                debug_logs = json.load(f)
        except:
            debug_logs = []
    
    debug_logs.append(log_entry)
    
    with open(DEBUG_LOG_FILE, 'w') as f:
        json.dump(debug_logs, f, indent=2)
    
    return log_entry

def run_debug_face_swap(test_num, source_path, target_path, card_id, auth_headers):
    """
    Run a single face swap with comprehensive debug logging
    """
    print(f"\n{'='*60}")
    print(f"DEBUG TEST {test_num}/5")
    print(f"{'='*60}")
    print(f"Source: {source_path.name}")
    print(f"Target: {target_path.name}")
    print(f"Card ID: {card_id}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Start timing
    overall_start = time.time()
    
    try:
        # Encode images with timing
        encoding_start = time.time()
        print(f"📸 Encoding source image: {source_path.name}")
        source_base64 = encode_image_to_base64(source_path)
        
        print(f"📸 Encoding target image: {target_path.name}")
        target_base64 = encode_image_to_base64(target_path)
        encoding_time = time.time() - encoding_start
        
        # Get image info
        source_info = {
            "filename": source_path.name,
            "size_bytes": source_path.stat().st_size,
            "base64_length": len(source_base64)
        }
        target_info = {
            "filename": target_path.name,
            "size_bytes": target_path.stat().st_size,
            "base64_length": len(target_base64)
        }
        
        # Prepare payload
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,
            "target_card_id": card_id
        }
        
        print(f"📊 Payload size: {len(json.dumps(payload))} bytes")
        print(f"📊 Source base64 length: {len(source_base64)}")
        print(f"📊 Target base64 length: {len(target_base64)}")
        
        # Prepare request data for logging
        request_data = {
            "headers": auth_headers,
            "payload": payload,
            "source_info": source_info,
            "target_info": target_info
        }
        
        # Make API request with detailed timing
        request_start = time.time()
        print(f"🚀 Sending request at {datetime.now().isoformat()}")
        
        try:
            response = requests.post(
                API_ENDPOINT,
                headers=auth_headers,
                json=payload,
                timeout=180
            )
            request_end = time.time()
            request_time = request_end - request_start
            
            print(f"📡 Response received at {datetime.now().isoformat()}")
            print(f"⏱️  Request duration: {request_time:.3f} seconds")
            print(f"📊 Response status: {response.status_code}")
            print(f"📊 Response headers: {dict(response.headers)}")
            
            # Parse response
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": len(response.content),
                "response_time_seconds": request_time
            }
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    response_data["json_response"] = json_response
                    response_data["json_keys"] = list(json_response.keys()) if isinstance(json_response, dict) else None
                    
                    print(f"✅ SUCCESS!")
                    print(f"📋 Response keys: {response_data['json_keys']}")
                    
                    # Check for generation time in response
                    if isinstance(json_response, dict):
                        for key in ['generation_time', 'processing_time', 'duration', 'time_taken']:
                            if key in json_response:
                                print(f"⏱️  API reported {key}: {json_response[key]}")
                                break
                    
                except json.JSONDecodeError as e:
                    response_data["json_error"] = str(e)
                    response_data["raw_content"] = response.text[:1000]  # First 1000 chars
                    print(f"⚠️ JSON decode error: {e}")
            else:
                response_data["error_content"] = response.text
                print(f"❌ API Error {response.status_code}")
                print(f"📄 Error content: {response.text}")
            
            # Timing summary
            timing_data = {
                "encoding_time_seconds": encoding_time,
                "request_time_seconds": request_time,
                "total_time_seconds": time.time() - overall_start,
                "request_start_timestamp": datetime.fromtimestamp(request_start).isoformat(),
                "request_end_timestamp": datetime.fromtimestamp(request_end).isoformat()
            }
            
            # Log everything
            log_entry = log_detailed_request(test_num, request_data, response_data, timing_data)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "request_time": request_time,
                "log_entry": log_entry
            }
            
        except requests.exceptions.Timeout as e:
            request_time = time.time() - request_start
            print(f"⏰ TIMEOUT after {request_time:.3f} seconds")
            
            timing_data = {
                "encoding_time_seconds": encoding_time,
                "request_time_seconds": request_time,
                "total_time_seconds": time.time() - overall_start,
                "timeout_at_timestamp": datetime.now().isoformat()
            }
            
            error_data = {
                "error_type": "Timeout",
                "error_message": str(e),
                "timeout_seconds": 180
            }
            
            response_data = {
                "status_code": "TIMEOUT",
                "error": "Request timed out"
            }
            
            log_entry = log_detailed_request(test_num, request_data, response_data, timing_data, error_data)
            
            return {
                "success": False,
                "status_code": "TIMEOUT",
                "request_time": request_time,
                "error": str(e),
                "log_entry": log_entry
            }
            
        except Exception as e:
            request_time = time.time() - request_start
            print(f"💥 EXCEPTION: {str(e)}")
            
            timing_data = {
                "encoding_time_seconds": encoding_time,
                "request_time_seconds": request_time,
                "total_time_seconds": time.time() - overall_start,
                "exception_at_timestamp": datetime.now().isoformat()
            }
            
            error_data = {
                "error_type": "Exception",
                "error_message": str(e),
                "exception_class": e.__class__.__name__
            }
            
            response_data = {
                "status_code": "EXCEPTION",
                "error": str(e)
            }
            
            log_entry = log_detailed_request(test_num, request_data, response_data, timing_data, error_data)
            
            return {
                "success": False,
                "status_code": "EXCEPTION",
                "request_time": request_time,
                "error": str(e),
                "log_entry": log_entry
            }
            
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {str(e)}")
        return {
            "success": False,
            "status_code": "CRITICAL_ERROR",
            "error": str(e)
        }

def main():
    """Run 5 debug tests with comprehensive logging"""
    print("🔬 DEBUG: Running 5 Face Swap Tests with Full Logging")
    print("=" * 70)
    
    # Get authentication
    print("🔐 Getting Thortful authentication...")
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Failed to get authentication headers")
        return
    
    print(f"✅ Authentication obtained")
    print(f"📊 Auth headers keys: {list(auth_headers.keys())}")
    
    # Get test images
    source_images = list(SOURCE_DIR.glob('*.jpg')) + list(SOURCE_DIR.glob('*.png'))
    target_images = list(TARGET_DIR.glob('*.jpg')) + list(TARGET_DIR.glob('*.png'))
    
    if not source_images or not target_images:
        print("❌ No test images found")
        return
    
    print(f"📊 Found {len(source_images)} source images, {len(target_images)} target images")
    
    # Run 5 tests
    results = []
    for i in range(5):
        test_num = i + 1
        
        # Use different combinations for variety
        source_idx = i % len(source_images)
        target_idx = i % len(target_images)
        card_id = TEST_CARD_IDS[i]
        
        source_path = source_images[source_idx]
        target_path = target_images[target_idx]
        
        result = run_debug_face_swap(test_num, source_path, target_path, card_id, auth_headers)
        results.append(result)
        
        # Brief pause between tests
        if i < 4:  # Don't sleep after last test
            print(f"⏸️  Pausing 5 seconds before next test...")
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*70}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r['success'])
    timeouts = sum(1 for r in results if r.get('status_code') == 'TIMEOUT')
    errors = len(results) - successful - timeouts
    
    print(f"✅ Successful: {successful}/5")
    print(f"⏰ Timeouts: {timeouts}/5")
    print(f"❌ Errors: {errors}/5")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else ("⏰" if result.get('status_code') == 'TIMEOUT' else "❌")
        time_str = f"{result.get('request_time', 0):.3f}s" if 'request_time' in result else "N/A"
        print(f"  Test {i}: {status} {result.get('status_code', 'UNKNOWN')} ({time_str})")
    
    print(f"\n📋 Detailed logs saved to: {DEBUG_LOG_FILE.absolute()}")
    print(f"📋 Use this file to replicate the exact same API calls")
    
    # Show file location for easy access
    print(f"\n🔧 REPLICATION GUIDE:")
    print(f"1. Review detailed logs: {DEBUG_LOG_FILE.absolute()}")
    print(f"2. Each test includes exact curl and Python equivalents")
    print(f"3. Payload sizes and timing data included for performance analysis")
    print(f"4. Authentication headers structure preserved (sensitive data redacted)")

if __name__ == "__main__":
    main()