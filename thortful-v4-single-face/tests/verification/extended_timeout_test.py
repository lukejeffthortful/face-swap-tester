#!/usr/bin/env python3
"""
Extended timeout test to get successful calls beyond 60 seconds
Keep testing until we get at least one call that succeeds beyond 60s
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
EXTENDED_LOG_FILE = Path("logs/extended_timeout_test.json")

# All available card IDs for maximum variety
ALL_CARD_IDS = [
    "67816ae75990fc276575cd07",  # card_template_01
    "6855c0b6ebba0773538e8a15",  # card_template_02
    "66facc0a21fd6d6f34901ae6",  # card_template_03
    "66e01c85ded8e0212043629d",  # card_template_04
    "67d219a67d3f9803484845be",  # card_template_05
    "68497934ad723e68b9792266",  # card_template_06
    "680b65d36010d4505cbac642",  # card_template_07
    "6854af2294654d25b467e33b",  # card_template_08
    "68097dd5b46c0a5b4e3543f8",  # card_template_09
    "680b635ab4259a1b1933d009",  # card_template_10
]

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def run_extended_test(test_num, source_path, target_path, card_id, auth_headers, timeout_seconds=150):
    """Run a single test with extended timeout"""
    print(f"\n=== EXTENDED TEST {test_num} ===")
    print(f"Source: {source_path.name}")
    print(f"Target: {target_path.name}")
    print(f"Card ID: {card_id}")
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
        print(f"📊 Payload size: {len(json.dumps(payload))} bytes")
        
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
            "success": response.status_code == 200,
            "exceeded_60s": duration > 60.0
        }
        
        if response.status_code == 200:
            print(f"✅ SUCCESS after {duration:.1f}s" + (" 🎯 BEYOND 60s!" if duration > 60 else " (under 60s)"))
            try:
                json_response = response.json()
                result["has_image"] = "image" in json_response
                result["response_keys"] = list(json_response.keys()) if isinstance(json_response, dict) else []
                print(f"📋 Response keys: {result['response_keys']}")
                
                # If we have a successful call beyond 60s, this is our proof!
                if duration > 60:
                    print(f"🎉 PROOF FOUND! Successful call at {duration:.1f}s (beyond 60s limit)")
                    result["is_proof"] = True
                else:
                    result["is_proof"] = False
                    
            except:
                result["json_parse_error"] = True
        elif response.status_code == 504:
            print(f"⏰ Gateway timeout after {duration:.1f}s")
            result["error_type"] = "gateway_timeout"
        else:
            print(f"❌ Error {response.status_code} after {duration:.1f}s")
            result["error_content"] = response.text[:200]  # First 200 chars
            result["error_type"] = f"http_{response.status_code}"
        
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
            "exceeded_60s": duration > 60.0,
            "error_type": "client_timeout",
            "is_proof": False
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
            "exceeded_60s": duration > 60.0,
            "error_type": "exception",
            "is_proof": False
        }

def main():
    print("🎯 Extended Timeout Test - Find Success Beyond 60s")
    print("=" * 60)
    print("Goal: Get at least one successful call that takes >60 seconds")
    print("This will prove the endpoint change truly resolved the issue")
    print("=" * 60)
    
    # Get authentication
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Authentication failed")
        return
    
    # Get test images - use all available for variety
    source_images = list(SOURCE_DIR.glob('*.jpg'))
    target_images = list(TARGET_DIR.glob('*.png'))
    
    print(f"📊 Available: {len(source_images)} source images, {len(target_images)} target images")
    print(f"📊 Testing with {len(ALL_CARD_IDS)} different card templates")
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    results = []
    proof_found = False
    test_count = 0
    max_tests = 20  # Limit to prevent infinite loop
    
    print(f"\n🔄 Will run up to {max_tests} tests until we find success beyond 60s")
    
    # Keep testing until we find a successful call beyond 60s
    while not proof_found and test_count < max_tests:
        test_count += 1
        
        # Use variety in combinations
        source_idx = (test_count - 1) % len(source_images)
        target_idx = (test_count - 1) % len(target_images)
        card_idx = (test_count - 1) % len(ALL_CARD_IDS)
        
        source_path = source_images[source_idx]
        target_path = target_images[target_idx]
        card_id = ALL_CARD_IDS[card_idx]
        
        result = run_extended_test(test_count, source_path, target_path, card_id, auth_headers, timeout_seconds=150)
        results.append(result)
        
        # Check if this is our proof
        if result.get("is_proof", False):
            proof_found = True
            print(f"\n🎉🎉 PROOF ESTABLISHED! 🎉🎉")
            print(f"Successfully completed request in {result['duration_seconds']:.1f} seconds")
            print(f"This proves www.thortful.com endpoint works beyond 60s!")
            break
        elif result["success"] and result["duration_seconds"] > 60:
            proof_found = True
            result["is_proof"] = True
            print(f"\n🎉🎉 PROOF ESTABLISHED! 🎉🎉")
            break
        
        # Brief pause between tests (longer for unsuccessful tests)
        if test_count < max_tests and not proof_found:
            pause_time = 10 if not result["success"] else 5
            print(f"⏸️ Pausing {pause_time} seconds before next test...")
            time.sleep(pause_time)
    
    # Save results
    with open(EXTENDED_LOG_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎯 EXTENDED TIMEOUT TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Endpoint: {API_ENDPOINT}")
    print(f"Tests completed: {test_count}")
    
    successful = [r for r in results if r["success"]]
    beyond_60s = [r for r in results if r["success"] and r["duration_seconds"] > 60]
    
    print(f"\n📊 Results:")
    print(f"  - Total successful: {len(successful)}/{test_count}")
    print(f"  - Successful beyond 60s: {len(beyond_60s)}")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        beyond_60_indicator = " 🎯" if result.get("exceeded_60s") and result["success"] else ""
        proof_indicator = " 🏆 PROOF!" if result.get("is_proof") else ""
        print(f"  Test {result['test_number']}: {status} {result.get('status_code', 'N/A')} ({result['duration_seconds']:.1f}s){beyond_60_indicator}{proof_indicator}")
    
    print(f"\n📋 Results saved to: {EXTENDED_LOG_FILE}")
    
    if proof_found:
        print(f"\n🎉 CONCLUSION: PROOF ESTABLISHED!")
        print(f"The www.thortful.com endpoint successfully processes requests beyond 60 seconds.")
        print(f"This definitively proves the endpoint change resolved the timeout issue.")
    else:
        print(f"\n⚠️ No proof yet - all successful calls were under 60s")
        print(f"May need to continue testing or try different combinations")

if __name__ == "__main__":
    main()