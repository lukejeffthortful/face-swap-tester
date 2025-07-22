#!/usr/bin/env python3
"""
Batch test face swaps using generated source and target images
Tests all combinations: 20 source × 20 target = 400 face swaps
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

def perform_face_swap(source_path, target_path, output_path, metadata_path):
    """Perform face swap between source and target images"""
    API_KEY = load_api_key()
    API_URL = "https://api.segmind.com/v1/faceswap-v2"
    
    # Convert images to base64
    source_base64 = image_file_to_base64(source_path)
    target_base64 = image_file_to_base64(target_path)
    
    # Prepare API request
    data = {
        "source_img": source_base64,
        "target_img": target_base64,
        "input_faces_index": "0,1,2,3",  # All 4 faces in target
        "source_faces_index": "0,1,2,3",  # All 4 faces in source
        "face_restore": "codeformer-v0.1.0.pth",
        "base64": False
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
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
            "source_faces_index": "0,1,2,3",
            "input_faces_index": "0,1,2,3",
            "face_restore": "codeformer-v0.1.0.pth",
            "generation_time": response.headers.get('X-generation-time'),
            "remaining_credits": response.headers.get('X-remaining-credits'),
            "request_id": response.headers.get('X-Request-ID'),
            "image_metadata": response.headers.get('X-output-metadata'),
            "content_length": response.headers.get('Content-Length')
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True, metadata.get('generation_time', 'N/A')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def run_batch_tests():
    """Run all face swap combinations"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    # Get all source and target images
    source_images = sorted(glob.glob("test-results/source-images/source_*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.jpg"))
    
    print(f"Found {len(source_images)} source images")
    print(f"Found {len(target_images)} target images")
    print(f"Total combinations to test: {len(source_images) * len(target_images)}")
    
    if not source_images or not target_images:
        print("❌ No source or target images found. Run generate_test_images.py first.")
        return
    
    print(f"\\nEstimated time: ~{(len(source_images) * len(target_images) * 4) // 60} minutes")
    input("Press Enter to start batch testing...")
    
    total_tests = len(source_images) * len(target_images)
    successful_tests = 0
    failed_tests = 0
    total_time = 0
    
    start_time = time.time()
    
    for i, source_path in enumerate(source_images, 1):
        source_name = os.path.basename(source_path).replace('.jpg', '')
        
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.basename(target_path).replace('.jpg', '')
            
            # Create output filenames
            output_name = f"{source_name}_to_{target_name}"
            output_path = f"test-results/results/{output_name}_result.jpg"
            metadata_path = f"test-results/results/{output_name}_metadata.json"
            
            current_test = (i-1) * len(target_images) + j
            print(f"\\n[{current_test}/{total_tests}] Testing: {source_name} → {target_name}")
            
            success, gen_time = perform_face_swap(source_path, target_path, output_path, metadata_path)
            
            if success:
                successful_tests += 1
                print(f"✅ Success ({gen_time}s)")
                if gen_time and gen_time != 'N/A':
                    total_time += float(gen_time)
            else:
                failed_tests += 1
                print(f"❌ Failed")
            
            # Progress update every 10 tests
            if current_test % 10 == 0:
                elapsed = time.time() - start_time
                avg_time_per_test = elapsed / current_test
                remaining_tests = total_tests - current_test
                eta_seconds = remaining_tests * avg_time_per_test
                eta_minutes = eta_seconds / 60
                
                print(f"\\n📊 Progress: {current_test}/{total_tests} ({current_test/total_tests*100:.1f}%)")
                print(f"⏱️  ETA: {eta_minutes:.1f} minutes")
                print(f"✅ Success rate: {successful_tests/current_test*100:.1f}%")
            
            # Rate limiting - small delay between requests
            time.sleep(1)
    
    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\\n🎉 Batch testing complete!")
    print(f"📊 Results Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {successful_tests/total_tests*100:.1f}%")
    print(f"   Total elapsed time: {elapsed_total/60:.1f} minutes")
    if total_time > 0:
        print(f"   Average API generation time: {total_time/successful_tests:.2f}s")
    print(f"\\n📁 Results saved to: test-results/results/")
    print(f"   {successful_tests} result images")
    print(f"   {successful_tests} metadata files")

def main():
    """Main function"""
    print("🚀 Batch Face Swap Testing")
    print("==========================")
    print("This will test all combinations of source and target images.")
    print("Each test swaps all 4 faces simultaneously.\\n")
    
    run_batch_tests()

if __name__ == "__main__":
    main()