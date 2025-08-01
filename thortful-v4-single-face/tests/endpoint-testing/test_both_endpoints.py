#!/usr/bin/env python3
"""
Test both Thortful API endpoints with fresh authentication
- Original: https://api.thortful.com/v1/faceswap?variation=true
- Working: https://www.thortful.com/api/v1/faceswap?variation=true
"""

import sys
import os
sys.path.append('..')

import requests
import json
import base64
import time
from pathlib import Path
from thortful_auth import get_thortful_auth

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_endpoint(endpoint_url, name):
    """Test a specific endpoint"""
    print(f"\n🧪 Testing {name}")
    print(f"📍 Endpoint: {endpoint_url}")
    print("-" * 60)
    
    # Get fresh authentication
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Failed to get authentication headers")
        return False
    
    # Use first available source and card ID
    source_dir = Path("diverse-source-images")
    source_images = list(source_dir.glob('*.jpg')) + list(source_dir.glob('*.png'))
    
    if not source_images:
        print("❌ No source images found")
        return False
    
    source_path = source_images[0]
    card_id = "67816ae75990fc276575cd07"
    
    print(f"📸 Using: {source_path.name}")
    print(f"🎯 Card ID: {card_id}")
    
    try:
        # Encode source image
        source_base64 = encode_image_to_base64(source_path)
        
        # Prepare payload
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,
            "target_card_id": card_id
        }
        
        print("🚀 Sending request...")
        start_time = time.time()
        
        response = requests.post(
            endpoint_url,
            headers=auth_headers,
            json=payload,
            timeout=180
        )
        
        request_time = time.time() - start_time
        print(f"⏱️  Request time: {request_time:.2f}s")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result_data = response.json()
            print("✅ SUCCESS!")
            print(f"📋 Response keys: {list(result_data.keys())}")
            
            if 'image' in result_data:
                # Save test result
                endpoint_name = name.lower().replace(' ', '_')
                result_filename = f"test_{endpoint_name}_{source_path.stem}_{card_id[:8]}.jpg"
                result_path = Path("results") / result_filename
                result_path.parent.mkdir(exist_ok=True)
                
                result_image_data = base64.b64decode(result_data['image'])
                with open(result_path, 'wb') as f:
                    f.write(result_image_data)
                print(f"💾 Result saved: {result_filename}")
            
            return True
            
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Authentication issue")
            print(f"📄 Response: {response.text}")
            return False
            
        elif response.status_code == 504:
            print("❌ 504 Gateway Timeout - Processing took too long")
            return False
            
        else:
            print(f"❌ Error {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after {time.time() - start_time:.2f}s")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Test both endpoints"""
    print("🔄 Thortful API Endpoint Comparison")
    print("=" * 60)
    
    # Test both endpoints
    results = {}
    
    endpoints = [
        ("https://api.thortful.com/v1/faceswap?variation=true", "Original API Endpoint"),
        ("https://www.thortful.com/api/v1/faceswap?variation=true", "Working WWW Endpoint")
    ]
    
    for url, name in endpoints:
        results[name] = test_endpoint(url, name)
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ENDPOINT COMPARISON SUMMARY")
    print("=" * 60)
    
    for name, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{name:.<40} {status}")
    
    # Recommendation
    working_endpoints = [name for name, success in results.items() if success]
    if working_endpoints:
        print(f"\n💡 RECOMMENDATION: Use {working_endpoints[0]}")
        if len(working_endpoints) > 1:
            print("   Multiple endpoints working - both are viable options")
    else:
        print("\n⚠️  WARNING: No endpoints working - check authentication")
    
    print(f"\n🎫 Token used: {get_thortful_auth().get('user_token', 'NONE')[:20]}...")

if __name__ == "__main__":
    main()