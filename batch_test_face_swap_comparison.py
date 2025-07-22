#!/usr/bin/env python3
"""
Comparative batch test: Test both v2 and v4.3 APIs side-by-side
Creates results for both API versions for easy comparison
"""

import requests
import base64
import os
import json
from datetime import datetime
import time
import glob

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

def image_file_to_base64(image_path):
    """Convert an image file from the filesystem to base64"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def perform_face_swap_v2(source_base64, target_base64, api_key):
    """Perform face swap using v2 API"""
    API_URL = "https://api.segmind.com/v1/faceswap-v2"
    
    data = {
        "source_img": source_base64,
        "target_img": target_base64,
        "input_faces_index": "0,1,2,3",
        "source_faces_index": "0,1,2,3",
        "face_restore": "codeformer-v0.1.0.pth",
        "base64": False
    }
    
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response, None
    except Exception as e:
        return None, str(e)

def perform_face_swap_v4(source_base64, target_base64, api_key):
    """Perform face swap using v4.3 API"""
    API_URL = "https://api.segmind.com/v1/faceswap-v4.3"
    
    data = {
        "source_image": source_base64,
        "target_image": target_base64,
        "source_face_index": "0,1,2,3",
        "target_face_index": "0,1,2,3",
        "detection_face_order": "big_to_small",
        "model_type": "speed",
        "swap_type": "face",
        "style_type": "normal",
        "base64": False
    }
    
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response, None
    except Exception as e:
        return None, str(e)

def save_result(response, output_path, metadata_path, version, source_path, target_path):
    """Save result image and metadata"""
    # Save result image
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    # Save metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "source_image": os.path.basename(source_path),
        "target_image": os.path.basename(target_path),
        "output_image": os.path.basename(output_path),
        "api_version": version,
        "source_faces_index": "0,1,2,3",
        "input_faces_index": "0,1,2,3" if version == "v2" else "0,1,2,3",
        "generation_time": response.headers.get('X-generation-time'),
        "remaining_credits": response.headers.get('X-remaining-credits'),
        "request_id": response.headers.get('X-Request-ID'),
        "image_metadata": response.headers.get('X-output-metadata'),
        "content_length": response.headers.get('Content-Length')
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata.get('generation_time', 'N/A')

def run_comparative_tests():
    """Run comparative tests for both API versions"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    # Get source and target images
    source_images = sorted(glob.glob("test-results/source-images/source_*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.jpg") + glob.glob("test-results/target-images/target_*.png"))
    
    print(f"Found {len(source_images)} source images")
    print(f"Found {len(target_images)} target images")
    print(f"Total combinations per API: {len(source_images) * len(target_images)}")
    print(f"Total tests (both APIs): {len(source_images) * len(target_images) * 2}")
    
    if not source_images or not target_images:
        print("❌ No source or target images found.")
        return
    
    total_combinations = len(source_images) * len(target_images)
    successful_v2 = 0
    successful_v4 = 0
    failed_tests = 0
    total_time_v2 = 0
    total_time_v4 = 0
    
    start_time = time.time()
    
    for i, source_path in enumerate(source_images, 1):
        source_name = os.path.basename(source_path).replace('.jpg', '').replace('.jpeg', '')
        
        # Convert source image once per source
        source_base64 = image_file_to_base64(source_path)
        
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.basename(target_path).replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
            
            # Convert target image
            target_base64 = image_file_to_base64(target_path)
            
            current_combo = (i-1) * len(target_images) + j
            print(f"\n[{current_combo}/{total_combinations}] Testing: {source_name} → {target_name}")
            
            # Test v2 API
            print("  🔄 Testing v2...")
            start_v2 = time.time()
            response_v2, error_v2 = perform_face_swap_v2(source_base64, target_base64, API_KEY)
            end_v2 = time.time()
            
            if response_v2:
                output_path_v2 = f"test-results/results/{source_name}_to_{target_name}_v2_result.jpg"
                metadata_path_v2 = f"test-results/results/{source_name}_to_{target_name}_v2_metadata.json"
                
                gen_time_v2 = save_result(response_v2, output_path_v2, metadata_path_v2, "v2", source_path, target_path)
                successful_v2 += 1
                total_time_v2 += (end_v2 - start_v2)
                print(f"    ✅ v2 Success ({gen_time_v2}s)")
            else:
                failed_tests += 1
                print(f"    ❌ v2 Failed: {error_v2}")
            
            time.sleep(1)  # Brief pause between API calls
            
            # Test v4.3 API
            print("  🔄 Testing v4.3...")
            start_v4 = time.time()
            response_v4, error_v4 = perform_face_swap_v4(source_base64, target_base64, API_KEY)
            end_v4 = time.time()
            
            if response_v4:
                output_path_v4 = f"test-results/results/{source_name}_to_{target_name}_v4_result.jpg"
                metadata_path_v4 = f"test-results/results/{source_name}_to_{target_name}_v4_metadata.json"
                
                gen_time_v4 = save_result(response_v4, output_path_v4, metadata_path_v4, "v4.3", source_path, target_path)
                successful_v4 += 1
                total_time_v4 += (end_v4 - start_v4)
                print(f"    ✅ v4.3 Success ({gen_time_v4}s)")
            else:
                failed_tests += 1
                print(f"    ❌ v4.3 Failed: {error_v4}")
            
            time.sleep(2)  # Longer pause between combinations
    
    # Final summary
    elapsed_total = time.time() - start_time
    total_tests = total_combinations * 2
    successful_total = successful_v2 + successful_v4
    
    print(f"\n🎉 Comparative testing complete!")
    print(f"📊 Results Summary:")
    print(f"   Total combinations tested: {total_combinations}")
    print(f"   Total API calls: {total_tests}")
    print(f"   v2 Success: {successful_v2}/{total_combinations} ({successful_v2/total_combinations*100:.1f}%)")
    print(f"   v4.3 Success: {successful_v4}/{total_combinations} ({successful_v4/total_combinations*100:.1f}%)")
    print(f"   Overall Success: {successful_total}/{total_tests} ({successful_total/total_tests*100:.1f}%)")
    print(f"   Total elapsed time: {elapsed_total/60:.1f} minutes")
    
    if successful_v2 > 0:
        print(f"   Average v2 time: {total_time_v2/successful_v2:.2f}s per request")
    if successful_v4 > 0:
        print(f"   Average v4.3 time: {total_time_v4/successful_v4:.2f}s per request")
    
    print(f"\n📁 Results saved to: test-results/results/")
    print(f"   Files ending in '_v2_result.jpg' are v2 API results")
    print(f"   Files ending in '_v4_result.jpg' are v4.3 API results")

def main():
    """Main function"""
    print("🚀 Comparative Face Swap Testing (v2 vs v4.3)")
    print("==============================================")
    print("This will test both APIs for each source/target combination")
    print("Each source-target pair will generate 2 results for comparison\\n")
    
    run_comparative_tests()

if __name__ == "__main__":
    main()