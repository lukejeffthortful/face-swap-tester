#!/usr/bin/env python3
"""
Simple face swap test using Segmind API
Based on the working example code provided
"""

import requests
import base64
import os
import json
from datetime import datetime
from pathlib import Path

def image_file_to_base64(image_path):
    """Convert an image file from the filesystem to base64"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def save_result_image(image_url, filename):
    """Download and save result image from URL"""
    response = requests.get(image_url)
    response.raise_for_status()
    
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    print(f"Saved result image: {filename}")

def load_api_key():
    """Load API key from .env file or environment variable"""
    # First try environment variable
    api_key = os.getenv('REACT_APP_SEGMIND_API_KEY')
    if api_key:
        return api_key
    
    # Try to read from .env file
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('REACT_APP_SEGMIND_API_KEY='):
                    return line.split('=', 1)[1].strip()
    
    return None

def main():
    # Configuration
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file or environment variable")
        return
    
    API_URL = "https://api.segmind.com/v1/faceswap-v2"
    
    # Input images
    source_image_path = "example_images/input1.jpg"
    target_image_path = "example_images/target1.png"
    
    # Check if input images exist
    if not os.path.exists(source_image_path):
        print(f"Error: Source image not found: {source_image_path}")
        return
    
    if not os.path.exists(target_image_path):
        print(f"Error: Target image not found: {target_image_path}")
        return
    
    # Convert images to base64
    print("Converting images to base64...")
    source_base64 = image_file_to_base64(source_image_path)
    target_base64 = image_file_to_base64(target_image_path)
    
    print(f"Source image size: {len(source_base64)} characters")
    print(f"Target image size: {len(target_base64)} characters")
    
    # Prepare API request data for multiple face swaps
    # Map source faces "0,1,2,3" to target faces "0,1,2,3"
    data = {
        "source_img": source_base64,
        "target_img": target_base64,
        "input_faces_index": "0,1,2,3",  # Target face indices as string
        "source_faces_index": "0,1,2,3",  # Source face indices as string
        "face_restore": "codeformer-v0.1.0.pth",
        "base64": False  # Return URL instead of base64
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("Sending request to Segmind API...")
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response Content-Type: {response.headers.get('Content-Type')}")
        
        response.raise_for_status()
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Check if response is an image (when base64=False)
        if response.headers.get('Content-Type', '').startswith('image/'):
            # Direct image response
            result_filename = f"test-results/face_swap_v2_{timestamp}_result.jpg"
            
            with open(result_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"Saved result image: {result_filename}")
            
            # Extract metadata from headers
            metadata = {
                "timestamp": timestamp,
                "api_version": "v2",
                "source_faces_index": "0,1,2,3",
                "input_faces_index": "0,1,2,3",
                "face_restore": "codeformer-v0.1.0.pth",
                "generation_time": response.headers.get('X-generation-time'),
                "remaining_credits": response.headers.get('X-remaining-credits'),
                "request_id": response.headers.get('X-Request-ID'),
                "image_metadata": response.headers.get('X-output-metadata'),
                "content_type": response.headers.get('Content-Type'),
                "content_length": response.headers.get('Content-Length')
            }
        else:
            # JSON response
            result = response.json()
            print("API Response:", json.dumps(result, indent=2))
            
            # Save result image
            if 'image' in result and result['image']:
                result_filename = f"test-results/face_swap_v2_{timestamp}_result.png"
                
                if result['image'].startswith('http'):
                    # It's a URL - download the image
                    save_result_image(result['image'], result_filename)
                else:
                    # It's base64 - decode and save
                    image_data = base64.b64decode(result['image'])
                    with open(result_filename, 'wb') as f:
                        f.write(image_data)
                    print(f"Saved result image: {result_filename}")
            else:
                print("No image in API response")
            
            metadata = {
                "timestamp": timestamp,
                "api_version": "v2",
                "source_faces_index": "0,1,2,3",
                "input_faces_index": "0,1,2,3",
                "face_restore": "codeformer-v0.1.0.pth",
                "response": result
            }
        
        # Save metadata
        metadata_filename = f"test-results/face_swap_v2_{timestamp}_metadata.json"
        with open(metadata_filename, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Saved metadata: {metadata_filename}")
        print("Test completed successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response data: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()