#!/usr/bin/env python3
"""
Test a single V4 API call to debug issues
"""

import requests
import base64
import os
import json
from datetime import datetime
import time

def load_api_key():
    api_key = os.getenv('REACT_APP_SEGMIND_API_KEY')
    if api_key:
        return api_key
    
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('REACT_APP_SEGMIND_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return None

def image_file_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_v4_simple():
    """Test V4 API with simple parameters"""
    API_KEY = load_api_key()
    API_URL = "https://api.segmind.com/v1/faceswap-v4"
    
    # Use first source and first target
    source_path = "source-single-face/1443_v9_bc.jpg"
    target_path = "test-results/target-images/target_01.png"
    
    print("🧪 Testing V4 API")
    print(f"Source: {source_path}")
    print(f"Target: {target_path}")
    
    if not os.path.exists(source_path):
        print(f"❌ Source not found: {source_path}")
        return
    
    if not os.path.exists(target_path):
        print(f"❌ Target not found: {target_path}")
        return
    
    source_base64 = image_file_to_base64(source_path)
    target_base64 = image_file_to_base64(target_path)
    
    data = {
        "source_image": source_base64,
        "target_image": target_base64,
        "source_face_index": 0,
        "target_face_index": 0,
        "detection_face_order": "big_to_small",
        "model_type": "quality",
        "swap_type": "face"
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("🚀 Making API request...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=60)
        request_time = time.time() - start_time
        
        print(f"⏱️  Request time: {request_time:.2f}s")
        print(f"📊 Status code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Success! Response keys: {list(result.keys())}")
                
                if 'image' in result:
                    image_data = result['image']
                    print(f"🖼️  Image type: {type(image_data)}")
                    if isinstance(image_data, str):
                        if image_data.startswith('http'):
                            print(f"🔗 Image URL: {image_data[:100]}...")
                        else:
                            print(f"📝 Image data: {len(image_data)} chars")
                    
                    print(f"💰 Cost: {result.get('cost', 'N/A')}")
                    print(f"⚡ Inference time: {result.get('inference_time', 'N/A')}")
                else:
                    print("❌ No image in response")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response (first 500 chars): {response.text[:500]}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_v4_simple()