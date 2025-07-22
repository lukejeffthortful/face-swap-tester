#!/usr/bin/env python3
"""
Test individual face swaps to understand how the API handles face indices
"""

import requests
import base64
import os
import json
from datetime import datetime

def image_file_to_base64(image_path):
    """Convert an image file from the filesystem to base64"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_api_key():
    """Load API key from .env file or environment variable"""
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

def test_face_swap(source_face_idx, target_face_idx):
    """Test a single face swap combination"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    API_URL = "https://api.segmind.com/v1/faceswap-v2"
    
    # Input images
    source_image_path = "example_images/input1.jpg"
    target_image_path = "example_images/target1.png"
    
    if not os.path.exists(source_image_path) or not os.path.exists(target_image_path):
        print(f"Error: Input images not found")
        return
    
    # Convert images to base64
    source_base64 = image_file_to_base64(source_image_path)
    target_base64 = image_file_to_base64(target_image_path)
    
    # Prepare API request data
    data = {
        "source_img": source_base64,
        "target_img": target_base64,
        "input_faces_index": target_face_idx,  # Single integer
        "source_faces_index": source_face_idx,  # Single integer
        "face_restore": "codeformer-v0.1.0.pth",
        "base64": False
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"Testing: Source face {source_face_idx} → Target face {target_face_idx}")
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save result image
            result_filename = f"test-results/face_swap_s{source_face_idx}_t{target_face_idx}_{timestamp}.jpg"
            
            with open(result_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Success: {result_filename}")
            
            # Save metadata
            metadata = {
                "timestamp": timestamp,
                "source_face_index": source_face_idx,
                "target_face_index": target_face_idx,
                "generation_time": response.headers.get('X-generation-time'),
                "remaining_credits": response.headers.get('X-remaining-credits'),
                "request_id": response.headers.get('X-Request-ID')
            }
            
            metadata_filename = f"test-results/face_swap_s{source_face_idx}_t{target_face_idx}_{timestamp}_meta.json"
            with open(metadata_filename, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Test all face combinations"""
    print("Testing individual face swaps...")
    
    # Test each face combination
    combinations = [
        (0, 0), (0, 1), (0, 2), (0, 3),
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2), (2, 3),
        (3, 0), (3, 1), (3, 2), (3, 3)
    ]
    
    successful_tests = 0
    
    for source_idx, target_idx in combinations:
        success = test_face_swap(source_idx, target_idx)
        if success:
            successful_tests += 1
        print()  # Add spacing between tests
    
    print(f"Completed: {successful_tests}/{len(combinations)} tests successful")

if __name__ == "__main__":
    main()