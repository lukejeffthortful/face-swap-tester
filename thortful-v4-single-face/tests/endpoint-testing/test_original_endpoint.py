#!/usr/bin/env python3
"""
Test the original Thortful API endpoint with fresh authentication
Specifically tests: https://api.thortful.com/v1/faceswap?variation=true
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

# Original API endpoint
ORIGINAL_ENDPOINT = "https://api.thortful.com/v1/faceswap?variation=true"

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_original_endpoint():
    """Test the original API endpoint with fresh authentication"""
    print("🧪 Testing Original Thortful API Endpoint")
    print("=" * 60)
    print(f"🎯 Endpoint: {ORIGINAL_ENDPOINT}")
    
    # Get fresh authentication - this will load our newly generated token
    print("🔐 Loading fresh authentication...")
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Failed to get authentication headers")
        return False
    
    # Verify we have a fresh token
    if 'user_token' in auth_headers:
        token = auth_headers['user_token']
        print(f"🎫 Token: {token[:20]}...{token[-10:]}")
        print(f"📋 Customer ID: {auth_headers.get('x-thortful-customer-id', 'NOT_FOUND')}")
    else:
        print("⚠️ No user_token found in headers")
        return False
    
    # Use first available source image
    source_dir = Path("diverse-source-images")
    source_images = list(source_dir.glob('*.jpg')) + list(source_dir.glob('*.png'))
    
    if not source_images:
        print("❌ No source images found")
        return False
    
    source_path = source_images[0]
    card_id = "67816ae75990fc276575cd07"  # First card template
    
    print(f"📸 Source: {source_path.name}")
    print(f"🎨 Card ID: {card_id}")
    
    try:
        # Encode source image
        print("📦 Encoding image...")
        source_base64 = encode_image_to_base64(source_path)
        
        # Prepare payload exactly as the working script does
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,
            "target_card_id": card_id  # Fallback field
        }
        
        print("🚀 Sending request to original API endpoint...")
        print(f"   Headers count: {len(auth_headers)}")
        print(f"   Payload keys: {list(payload.keys())}")
        
        start_time = time.time()
        
        # Make request with shorter timeout to see response faster
        response = requests.post(
            ORIGINAL_ENDPOINT,
            headers=auth_headers,
            json=payload,
            timeout=60  # Shorter timeout to see what happens
        )
        
        request_time = time.time() - start_time
        print(f"⏱️  Request completed in {request_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result_data = response.json()
            print("✅ SUCCESS! Original endpoint is working!")
            print(f"📋 Response keys: {list(result_data.keys())}")
            
            # Check if we got an image
            if 'image' in result_data:
                # Save result
                result_filename = f"original_endpoint_test_{source_path.stem}_{card_id[:8]}.jpg"
                result_path = Path("results") / result_filename
                result_path.parent.mkdir(exist_ok=True)
                
                result_image_data = base64.b64decode(result_data['image'])
                with open(result_path, 'wb') as f:
                    f.write(result_image_data)
                print(f"💾 Result saved: {result_filename}")
            
            return True
            
        elif response.status_code == 403:
            print("❌ 403 FORBIDDEN")
            print(f"   Response text: '{response.text}'")
            print("   This suggests authentication issue despite fresh token")
            return False
            
        elif response.status_code == 504:
            print("❌ 504 GATEWAY TIMEOUT")
            print("   Processing is taking longer than gateway allows")
            print("   This actually suggests the endpoint is trying to work!")
            return False
            
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ TIMEOUT after {elapsed:.2f}s")
        print("   This could mean the endpoint is working but slow")
        print("   (Unlike immediate 403 errors we saw before)")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_original_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ORIGINAL ENDPOINT IS WORKING!")
        print("   The timeout issues appear to be fixed!")
    else:
        print("⚠️  Original endpoint still has issues")
        print("   But check the specific error type above")
    print("=" * 60)