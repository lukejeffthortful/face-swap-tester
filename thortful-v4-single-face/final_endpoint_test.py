#!/usr/bin/env python3
"""
Final test with www.thortful.com endpoint and longer timeout
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
FINAL_LOG_FILE = Path("logs/final_endpoint_test.json")

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def run_final_test(test_num, source_path, target_path, card_id, auth_headers, timeout_seconds=120):
    """Run a single test with extended timeout to confirm success"""
    print(f"\n=== FINAL TEST {test_num} ===")
    print(f"Source: {source_path.name}")
    print(f"Target: {target_path.name}")
    print(f"Timeout: {timeout_seconds}s")
    print(f"Endpoint: {API_ENDPOINT}")
    
    start_time = time.time()
    
    try:
        # Encode images
        source_base64 = encode_image_to_base64(source_path)
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,
            "target_card_id": card_id
        }
        
        print(f"🚀 Request started at {datetime.now().strftime('%H:%M:%S')}")
        
        # Make request with extended timeout
        response = requests.post(
            API_ENDPOINT,
            headers=auth_headers,
            json=payload,
            timeout=timeout_seconds
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = {
            "test_number": test_num,
            "timestamp": datetime.now().isoformat(),
            "endpoint": API_ENDPOINT,
            "duration_seconds": duration,
            "timeout_setting": timeout_seconds,
            "status_code": response.status_code,
            "source_file": source_path.name,
            "target_file": target_path.name,
            "card_id": card_id,
            "payload_size": len(json.dumps(payload)),
            "success": response.status_code == 200
        }
        
        if response.status_code == 200:
            print(f"✅ SUCCESS after {duration:.1f}s")
            try:
                json_response = response.json()
                result["has_image"] = "image" in json_response
                result["response_keys"] = list(json_response.keys()) if isinstance(json_response, dict) else []
                print(f"📋 Response keys: {result['response_keys']}")
            except:
                result["json_parse_error"] = True
        else:
            print(f"❌ Error {response.status_code} after {duration:.1f}s")
            result["error_content"] = response.text[:500]  # First 500 chars
        
        return result
        
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"⏰ Client timeout after {duration:.1f}s")
        return {
            "test_number": test_num,
            "timestamp": datetime.now().isoformat(),
            "endpoint": API_ENDPOINT,
            "duration_seconds": duration,
            "timeout_setting": timeout_seconds,
            "status_code": "CLIENT_TIMEOUT",
            "source_file": source_path.name,
            "target_file": target_path.name,
            "card_id": card_id,
            "success": False,
            "error_type": "client_timeout"
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Exception after {duration:.1f}s: {e}")
        return {
            "test_number": test_num,
            "timestamp": datetime.now().isoformat(),
            "endpoint": API_ENDPOINT,
            "duration_seconds": duration,
            "timeout_setting": timeout_seconds,
            "status_code": "EXCEPTION",
            "error": str(e),
            "source_file": source_path.name,
            "target_file": target_path.name,
            "card_id": card_id,
            "success": False,
            "error_type": "exception"
        }

def main():
    print("🎯 Final Endpoint Test - www.thortful.com")
    print("=" * 50)
    
    # Get authentication
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Authentication failed")
        return
    
    # Get test images
    source_images = list(SOURCE_DIR.glob('*.jpg'))
    target_images = list(TARGET_DIR.glob('*.png'))
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    results = []
    
    # Test the larger image that timed out before with extended timeout
    test_cases = [
        (source_images[0], target_images[0], "66facc0a21fd6d6f34901ae6"),  # diverse_face_01.jpg (larger)
        (source_images[3], target_images[1], "66e01c85ded8e0212043629d"),  # diverse_face_04.jpg (medium)
    ]
    
    for i, (source_path, target_path, card_id) in enumerate(test_cases):
        result = run_final_test(i+1, source_path, target_path, card_id, auth_headers, timeout_seconds=120)
        results.append(result)
        
        # Brief pause between tests
        if i < len(test_cases) - 1:
            print("⏸️ Pausing 5 seconds...")
            time.sleep(5)
    
    # Save results
    with open(FINAL_LOG_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n{'='*50}")
    print("🎯 FINAL ENDPOINT TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Endpoint: {API_ENDPOINT}")
    
    successful = sum(1 for r in results if r["success"])
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"Test {result['test_number']}: {status} {result.get('status_code', 'N/A')} ({result['duration_seconds']:.1f}s) - {result['source_file']}")
    
    print(f"\n📋 Success rate: {successful}/{len(results)}")
    print(f"📋 Results saved to: {FINAL_LOG_FILE}")
    
    if successful > 0:
        print(f"🎉 SUCCESS! The www.thortful.com endpoint works beyond 60 seconds!")
        avg_success_time = sum(r["duration_seconds"] for r in results if r["success"]) / successful
        print(f"📊 Average successful processing time: {avg_success_time:.1f}s")

if __name__ == "__main__":
    main()