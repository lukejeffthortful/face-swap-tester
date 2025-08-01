#!/usr/bin/env python3
"""
Quick timeout test - shorter timeout to capture multiple tests
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
TIMEOUT_LOG_FILE = Path("logs/timeout_analysis.json")

TEST_CARD_IDS = [
    "67816ae75990fc276575cd07",  # card_template_01
    "6855c0b6ebba0773538e8a15",  # card_template_02
    "66facc0a21fd6d6f34901ae6",  # card_template_03
]

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def run_timeout_test(test_num, source_path, target_path, card_id, auth_headers, timeout_seconds=70):
    """Run a single test with specified timeout"""
    print(f"\n=== TIMEOUT TEST {test_num} ===")
    print(f"Source: {source_path.name}")
    print(f"Target: {target_path.name}")
    print(f"Timeout: {timeout_seconds}s")
    
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
        
        # Make request with specified timeout
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
            "duration_seconds": duration,
            "timeout_setting": timeout_seconds,
            "status_code": response.status_code,
            "source_file": source_path.name,
            "target_file": target_path.name,
            "card_id": card_id,
            "payload_size": len(json.dumps(payload)),
            "completed": "success" if response.status_code == 200 else "error"
        }
        
        if response.status_code == 504:
            print(f"⏰ Gateway timeout after {duration:.1f}s")
            result["error_type"] = "gateway_timeout"
        elif response.status_code == 200:
            print(f"✅ Success after {duration:.1f}s")
        else:
            print(f"❌ Error {response.status_code} after {duration:.1f}s")
            result["error_type"] = f"http_{response.status_code}"
        
        return result
        
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"⏰ Client timeout after {duration:.1f}s")
        return {
            "test_number": test_num,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "timeout_setting": timeout_seconds,
            "status_code": "CLIENT_TIMEOUT",
            "source_file": source_path.name,
            "target_file": target_path.name, 
            "card_id": card_id,
            "completed": "timeout",
            "error_type": "client_timeout"
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Exception after {duration:.1f}s: {e}")
        return {
            "test_number": test_num,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "timeout_setting": timeout_seconds,
            "status_code": "EXCEPTION",
            "error": str(e),
            "source_file": source_path.name,
            "target_file": target_path.name,
            "card_id": card_id,
            "completed": "exception",
            "error_type": "exception"
        }

def main():
    print("⏰ Quick Timeout Analysis - 3 Tests")
    print("=" * 50)
    
    # Get authentication
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Authentication failed")
        return
    
    # Get test images
    source_images = list(SOURCE_DIR.glob('*.jpg'))[:3]  # First 3 only
    target_images = list(TARGET_DIR.glob('*.png'))
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    results = []
    
    # Run 3 quick tests with 70s timeout (less than 2min bash timeout)
    for i in range(3):
        source_path = source_images[i % len(source_images)]
        target_path = target_images[i % len(target_images)]
        card_id = TEST_CARD_IDS[i]
        
        result = run_timeout_test(i+1, source_path, target_path, card_id, auth_headers, timeout_seconds=70)
        results.append(result)
        
        # Brief pause between tests
        if i < 2:
            print("⏸️ Pausing 3 seconds...")
            time.sleep(3)
    
    # Save results
    with open(TIMEOUT_LOG_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n{'='*50}")
    print("🎯 TIMEOUT ANALYSIS SUMMARY")
    print(f"{'='*50}")
    
    for result in results:
        status = "✅" if result["completed"] == "success" else ("⏰" if "timeout" in result["completed"] else "❌")
        print(f"Test {result['test_number']}: {status} {result.get('status_code', 'N/A')} ({result['duration_seconds']:.1f}s)")
    
    print(f"\n📋 Results saved to: {TIMEOUT_LOG_FILE}")
    
    # Key insights
    gateway_timeouts = [r for r in results if r.get("error_type") == "gateway_timeout"]
    if gateway_timeouts:
        avg_timeout = sum(r["duration_seconds"] for r in gateway_timeouts) / len(gateway_timeouts)
        print(f"🔍 Gateway timeouts occur around {avg_timeout:.1f} seconds")

if __name__ == "__main__":
    main()