#!/usr/bin/env python3
"""
Batch test single face swaps: V2 vs V4 comparison
Tests with source_face_index=0 and target_face_index=0 only
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

def perform_face_swap_v2(source_path, target_path, output_path, metadata_path):
    """Perform V2 face swap with single face (index 0)"""
    API_KEY = load_api_key()
    API_URL = "https://api.segmind.com/v1/faceswap-v2"
    
    source_base64 = image_file_to_base64(source_path)
    target_base64 = image_file_to_base64(target_path)
    
    data = {
        "source_img": source_base64,
        "target_img": target_base64,
        "input_faces_index": 0,      # Single face only
        "source_faces_index": 0,     # Single face only
        "face_restore": "codeformer-v0.1.0.pth",
        "base64": False
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=data, headers=headers, timeout=120)
        request_time = time.time() - start_time
        
        response.raise_for_status()
        
        # Save result image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        # Save metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "source_image": os.path.basename(source_path),
            "target_image": os.path.basename(target_path),
            "output_image": os.path.basename(output_path),
            "api_version": "v2",
            "api_endpoint": "faceswap-v2",
            "test_type": "single_face",
            "source_faces_index": 0,
            "input_faces_index": 0,
            "face_restore": "codeformer-v0.1.0.pth",
            "generation_time": response.headers.get('X-generation-time'),
            "remaining_credits": response.headers.get('X-remaining-credits'),
            "request_id": response.headers.get('X-Request-ID'),
            "request_time": f"{request_time:.2f}",
            "content_length": response.headers.get('Content-Length')
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True, metadata.get('generation_time', 'N/A')
        
    except Exception as e:
        print(f"❌ V2 Error: {e}")
        return False, None

def perform_face_swap_v4(source_path, target_path, output_path, metadata_path):
    """Perform V4 face swap with single face (index 0)"""
    API_KEY = load_api_key()
    API_URL = "https://api.segmind.com/v1/faceswap-v4"  # V4 endpoint for single face
    
    source_base64 = image_file_to_base64(source_path)
    target_base64 = image_file_to_base64(target_path)
    
    data = {
        "source_image": source_base64,
        "target_image": target_base64,
        "source_face_index": 0,      # Single face only
        "target_face_index": 0,      # Single face only
        "detection_face_order": "big_to_small",  # Match V2 detection order
        "model_type": "quality",
        "swap_type": "face"
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=data, headers=headers, timeout=120)
        request_time = time.time() - start_time
        
        response.raise_for_status()
        
        # V4 returns binary image data directly (like V2)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        # Save metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "source_image": os.path.basename(source_path),
            "target_image": os.path.basename(target_path),
            "output_image": os.path.basename(output_path),
            "api_version": "v4",
            "api_endpoint": "faceswap-v4",
            "test_type": "single_face",
            "source_face_index": 0,
            "target_face_index": 0,
            "detection_face_order": "big_to_small",
            "model_type": "quality",
            "swap_type": "face",
            "generation_time": response.headers.get('X-generation-time'),
            "cost": None,  # V4 doesn't seem to return cost in headers
            "request_time": f"{request_time:.2f}",
            "image_format": "binary_jpeg",
            "remaining_credits": response.headers.get('X-remaining-credits'),
            "request_id": response.headers.get('X-Request-ID')
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True, metadata.get('generation_time', 'N/A')
        
    except Exception as e:
        print(f"❌ V4 Error: {e}")
        return False, None

def run_single_face_batch_tests():
    """Run single face swap tests comparing V2 vs V4"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    # Create single-face results directory
    os.makedirs("test-results/single-face-results", exist_ok=True)
    
    # Get all source and target images
    source_images = sorted(glob.glob("source-single-face/*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.png"))
    
    print(f"🎯 Single Face Testing: V2 vs V4")
    print(f"Found {len(source_images)} source images")
    print(f"Found {len(target_images)} target images")
    print(f"Total combinations to test: {len(source_images) * len(target_images)} × 2 APIs = {len(source_images) * len(target_images) * 2} tests")
    
    if not source_images or not target_images:
        print("❌ No source or target images found. Run generate_test_images.py first.")
        return
    
    print(f"\nEstimated time: ~{(len(source_images) * len(target_images) * 2 * 4) // 60} minutes")
    input("Press Enter to start single face batch testing...")
    
    total_combinations = len(source_images) * len(target_images)
    total_tests = total_combinations * 2  # V2 and V4
    successful_tests = 0
    failed_tests = 0
    
    start_time = time.time()
    test_counter = 0
    
    for i, source_path in enumerate(source_images, 1):
        source_filename = os.path.basename(source_path)
        source_name = os.path.splitext(source_filename)[0]  # Remove extension
        source_clean = f"source_{i:02d}"  # Create clean source name
        
        for j, target_path in enumerate(target_images, 1):
            target_filename = os.path.basename(target_path)
            target_name = os.path.splitext(target_filename)[0]  # Remove extension  
            
            combo_key = f"{source_clean}_to_{target_name}"
            current_combo = (i-1) * len(target_images) + j
            
            print(f"\n[{current_combo}/{total_combinations}] Testing: {source_clean} → {target_name}")
            
            # Test V2
            test_counter += 1
            print(f"  [{test_counter}/{total_tests}] V2 API...")
            v2_output_path = f"test-results/single-face-results/{combo_key}_v2_result.jpg"
            v2_metadata_path = f"test-results/single-face-results/{combo_key}_v2_metadata.json"
            
            v2_success, v2_time = perform_face_swap_v2(source_path, target_path, v2_output_path, v2_metadata_path)
            if v2_success:
                successful_tests += 1
                print(f"    ✅ V2 Success ({v2_time}s)")
            else:
                failed_tests += 1
                print(f"    ❌ V2 Failed")
            
            # Test V4
            test_counter += 1
            print(f"  [{test_counter}/{total_tests}] V4 API...")
            v4_output_path = f"test-results/single-face-results/{combo_key}_v4_result.jpg"
            v4_metadata_path = f"test-results/single-face-results/{combo_key}_v4_metadata.json"
            
            v4_success, v4_time = perform_face_swap_v4(source_path, target_path, v4_output_path, v4_metadata_path)
            if v4_success:
                successful_tests += 1
                print(f"    ✅ V4 Success ({v4_time}s)")
            else:
                failed_tests += 1
                print(f"    ❌ V4 Failed")
            
            # Progress update every 5 combinations
            if current_combo % 5 == 0:
                elapsed = time.time() - start_time
                avg_time_per_combo = elapsed / current_combo
                remaining_combos = total_combinations - current_combo
                eta_seconds = remaining_combos * avg_time_per_combo
                eta_minutes = eta_seconds / 60
                
                print(f"\n📊 Progress: {current_combo}/{total_combinations} combinations ({current_combo/total_combinations*100:.1f}%)")
                print(f"⏱️  ETA: {eta_minutes:.1f} minutes")
                print(f"✅ Success rate: {successful_tests/test_counter*100:.1f}% ({successful_tests}/{test_counter} tests)")
            
            # Rate limiting - small delay between requests
            time.sleep(1)
    
    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\n🎉 Single Face Batch Testing Complete!")
    print(f"📊 Results Summary:")
    print(f"   Total combinations: {total_combinations}")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful tests: {successful_tests}")
    print(f"   Failed tests: {failed_tests}")
    print(f"   Success rate: {successful_tests/total_tests*100:.1f}%")
    print(f"   Total elapsed time: {elapsed_total/60:.1f} minutes")
    print(f"\n📁 Results saved to: test-results/single-face-results/")
    print(f"   - Result images: {successful_tests} files")
    print(f"   - Metadata files: {successful_tests} files")
    print(f"\n🔍 Next step: Run generate_single_face_review.py to create comparison page")

def main():
    """Main function"""
    print("🎯 Single Face Swap Testing: V2 vs V4")
    print("=====================================")
    print("This will test V2 vs V4 APIs with single face swapping only.")
    print("Both APIs will use face index 0 (first/biggest face).")
    print("Results will be saved separately from multi-face tests.\n")
    
    run_single_face_batch_tests()

if __name__ == "__main__":
    main()