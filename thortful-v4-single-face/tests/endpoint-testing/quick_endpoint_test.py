#!/usr/bin/env python3
"""
Quick test to verify the original Thortful API endpoint is working
Tests the fixed https://api.thortful.com/v1/faceswap?variation=true endpoint
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

# Original API endpoint that was having timeout issues
API_ENDPOINT = "https://api.thortful.com/v1/faceswap?variation=true"

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def quick_test():
    """Run a quick test to verify the API endpoint is working"""
    print("🧪 Quick Endpoint Test - Original Thortful API")
    print("=" * 50)
    print(f"Testing endpoint: {API_ENDPOINT}")
    
    # Refresh authentication (always get fresh token for testing)
    print("🔐 Refreshing authentication token...")
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Failed to get authentication headers")
        return False
    
    # Verify we have fresh token
    if 'user_token' in auth_headers:
        print(f"🎫 Using fresh token: {auth_headers['user_token'][:20]}...")
    else:
        print("⚠️ No user_token found in headers")
    
    # Use first available source and card ID
    source_dir = Path("diverse-source-images")
    source_images = list(source_dir.glob('*.jpg')) + list(source_dir.glob('*.png'))
    
    if not source_images:
        print("❌ No source images found")
        return False
    
    source_path = source_images[0]  # Use first available image
    card_id = "67816ae75990fc276575cd07"  # Use first card template
    
    print(f"📸 Using source image: {source_path.name}")
    print(f"🎯 Using card ID: {card_id}")
    
    try:
        # Encode source image
        source_base64 = encode_image_to_base64(source_path)
        
        # Prepare payload
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,
            "target_card_id": card_id  # Fallback
        }
        
        print("🚀 Sending request to API...")
        start_time = time.time()
        
        # Make API request with generous timeout
        response = requests.post(
            API_ENDPOINT,
            headers=auth_headers,
            json=payload,
            timeout=180
        )
        
        request_time = time.time() - start_time
        print(f"⏱️  Request completed in {request_time:.2f}s")
        
        if response.status_code == 200:
            result_data = response.json()
            print("✅ SUCCESS! API is working properly")
            print(f"📊 Response keys: {list(result_data.keys())}")
            
            # Check if we got an image back
            if 'image' in result_data:
                print("🖼️  Response contains image data")
                
                # Save test result
                result_filename = f"quick_test_{source_path.stem}_card_{card_id[:8]}.jpg"
                result_path = Path("results") / result_filename
                result_path.parent.mkdir(exist_ok=True)
                
                result_image_data = base64.b64decode(result_data['image'])
                with open(result_path, 'wb') as f:
                    f.write(result_image_data)
                print(f"💾 Test result saved: {result_filename}")
            
            return True
            
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after {time.time() - start_time:.2f}s")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 Original API endpoint is working! Timeout issues appear to be fixed.")
    else:
        print("\n⚠️  Original API endpoint still has issues.")