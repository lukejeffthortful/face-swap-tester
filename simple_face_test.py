#!/usr/bin/env python3
"""
Simple test to verify basic V4.3 functionality and parameter compatibility
"""
import requests
import json
import base64
import os

API_KEY = os.getenv('SEGMIND_API_KEY')
BASE_URL = "https://api.segmind.com/v1"

def load_image_as_base64(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_v4_minimal():
    """Test V4.3 with minimal parameters"""
    url = f"{BASE_URL}/faceswap-v4.3"
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    source_b64 = load_image_as_base64("public/example_images/input1.jpg")
    target_b64 = load_image_as_base64("public/example_images/target1.png")
    
    # Test 1: Minimal parameters only
    payload = {
        "source_image": source_b64,
        "target_image": target_b64
    }
    
    print("=== V4.3 Minimal Test ===")
    print(f"Payload keys: {list(payload.keys())}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Success! Response keys: {list(result.keys())}")
                if 'image' in result:
                    print(f"Image type: {type(result['image'])}")
                    if isinstance(result['image'], str):
                        print(f"Image starts with: {result['image'][:50]}...")
                return result
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {response.text[:200]}...")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_v4_with_face_indices():
    """Test V4.3 with face index parameters"""
    url = f"{BASE_URL}/faceswap-v4.3"
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    source_b64 = load_image_as_base64("public/example_images/input1.jpg")
    target_b64 = load_image_as_base64("public/example_images/target1.png")
    
    # Test with face indices
    payload = {
        "source_image": source_b64,
        "target_image": target_b64,
        "source_face_index": 0,
        "target_face_index": 0,
        "detection_face_order": "big_to_small"
    }
    
    print("\n=== V4.3 with Face Indices Test ===")
    print(f"Payload keys: {list(payload.keys())}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Success! Response keys: {list(result.keys())}")
                return result
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response: {response.text[:200]}...")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_v2_minimal():
    """Test V2 with minimal parameters"""
    url = f"{BASE_URL}/faceswap-v2"
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    source_b64 = load_image_as_base64("public/example_images/input1.jpg")
    target_b64 = load_image_as_base64("public/example_images/target1.png")
    
    payload = {
        "source_img": source_b64,
        "target_img": target_b64,
        "base64": False
    }
    
    print("\n=== V2 Minimal Test ===")
    print(f"Payload keys: {list(payload.keys())}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {response.headers.get('content-length', 'Unknown')}")
        
        if response.status_code == 200:
            # Check if response is JSON or something else
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    result = response.json()
                    print(f"JSON Success! Response keys: {list(result.keys())}")
                    return result
                except json.JSONDecodeError as e:
                    print(f"JSON decode error despite content-type: {e}")
                    print(f"Raw response: {response.text[:200]}...")
            else:
                print(f"Non-JSON response. Content-Type: {content_type}")
                print(f"Response length: {len(response.content)} bytes")
                if response.content:
                    print(f"First 100 bytes: {response.content[:100]}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("Simple Face Swap API Test")
    print("=" * 40)
    
    # Test basic functionality first
    test_v4_minimal()
    test_v4_with_face_indices()  
    test_v2_minimal()