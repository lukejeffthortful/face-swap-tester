#!/usr/bin/env python3
"""
Debug script to test face index handling between V2 and V4.3 APIs
"""
import requests
import json
import base64
import os
from datetime import datetime

# Get API key from environment
API_KEY = os.getenv('SEGMIND_API_KEY')
if not API_KEY:
    print("Error: SEGMIND_API_KEY environment variable not set")
    exit(1)

BASE_URL = "https://api.segmind.com/v1"

def load_image_as_base64(filepath):
    """Load image file and convert to base64"""
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_face_swap_v2(source_b64, target_b64, source_face_idx=0, target_face_idx=0):
    """Test Face Swap V2 API"""
    url = f"{BASE_URL}/faceswap-v2"
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "source_img": source_b64,
        "target_img": target_b64,
        "source_faces_index": source_face_idx,
        "input_faces_index": target_face_idx,
        "face_restore": "codeformer-v0.1.0.pth",
        "base64": False
    }
    
    print(f"\n=== V2 API Test (Source Face {source_face_idx} -> Target Face {target_face_idx}) ===")
    print(f"URL: {url}")
    print(f"Payload keys: {list(payload.keys())}")
    print(f"Face indices: source_faces_index={source_face_idx}, input_faces_index={target_face_idx}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Image URL: {result.get('image', 'No image key')}")
            print(f"Cost: {result.get('cost', 'N/A')}")
            print(f"Inference time: {result.get('inference_time', 'N/A')}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None

def test_face_swap_v4(source_b64, target_b64, source_face_idx=0, target_face_idx=0):
    """Test Face Swap V4.3 API"""
    url = f"{BASE_URL}/faceswap-v4.3"
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "source_image": source_b64,
        "target_image": target_b64,
        "source_face_index": source_face_idx,
        "target_face_index": target_face_idx,
        "detection_face_order": "big_to_small",  # Match V2 detection order
        "model_type": "quality"
    }
    
    print(f"\n=== V4.3 API Test (Source Face {source_face_idx} -> Target Face {target_face_idx}) ===")
    print(f"URL: {url}")
    print(f"Payload keys: {list(payload.keys())}")
    print(f"Face indices: source_face_index={source_face_idx}, target_face_index={target_face_idx}")
    print(f"Detection order: {payload['detection_face_order']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Image: {type(result.get('image', 'No image key'))}")
            print(f"Cost: {result.get('cost', 'N/A')}")
            print(f"Inference time: {result.get('inference_time', 'N/A')}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None

def save_result_image(result, filename_prefix, api_version):
    """Save the result image from API response"""
    if not result or 'image' not in result:
        print(f"No image to save for {api_version}")
        return
    
    image_data = result['image']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        if image_data.startswith('http'):
            # It's a URL - download it
            img_response = requests.get(image_data)
            if img_response.status_code == 200:
                filename = f"{filename_prefix}_{api_version}_{timestamp}.jpg"
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                print(f"Saved image from URL: {filename}")
            else:
                print(f"Failed to download image from URL: {image_data}")
        else:
            # It's base64 data
            if image_data.startswith('data:'):
                # Strip data URL prefix
                image_data = image_data.split(',')[1]
            
            filename = f"{filename_prefix}_{api_version}_{timestamp}.jpg"
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(image_data))
            print(f"Saved base64 image: {filename}")
            
    except Exception as e:
        print(f"Failed to save image for {api_version}: {e}")

def main():
    print("Face Swap API Debug Test")
    print("=" * 40)
    
    # Load test images
    source_path = "public/example_images/input1.jpg"
    target_path = "public/example_images/target1.png"
    
    if not os.path.exists(source_path) or not os.path.exists(target_path):
        print(f"Error: Test images not found")
        print(f"Looking for: {source_path}, {target_path}")
        return
    
    print(f"Loading images...")
    print(f"Source: {source_path}")
    print(f"Target: {target_path}")
    
    source_b64 = load_image_as_base64(source_path)
    target_b64 = load_image_as_base64(target_path)
    
    print(f"Source image size: {len(source_b64)} chars")
    print(f"Target image size: {len(target_b64)} chars")
    
    # Test different face index combinations
    test_cases = [
        (0, 0),  # First face to first face
        (1, 1),  # Second face to second face
        (0, 1),  # First source to second target
        (1, 0),  # Second source to first target
    ]
    
    for source_idx, target_idx in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing Face Index Combination: Source {source_idx} -> Target {target_idx}")
        print(f"{'='*60}")
        
        # Test V2
        v2_result = test_face_swap_v2(source_b64, target_b64, source_idx, target_idx)
        if v2_result:
            save_result_image(v2_result, f"debug_face_{source_idx}to{target_idx}", "v2")
        
        # Test V4.3
        v4_result = test_face_swap_v4(source_b64, target_b64, source_idx, target_idx)
        if v4_result:
            save_result_image(v4_result, f"debug_face_{source_idx}to{target_idx}", "v4")
        
        print(f"\nComparison for faces {source_idx}->{target_idx}:")
        print(f"V2 Success: {'✓' if v2_result else '✗'}")
        print(f"V4.3 Success: {'✓' if v4_result else '✗'}")

if __name__ == "__main__":
    main()