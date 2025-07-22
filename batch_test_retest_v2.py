#!/usr/bin/env python3
"""
Batch test V2 API using the pre-separated images in test-results/re-test-v2/
Tests all source-target combinations
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

def perform_v2_face_swap(source_path, target_path, output_path, metadata_path):
    """Perform V2 face swap with single face (index 0)"""
    API_KEY = load_api_key()
    API_URL = "https://api.segmind.com/v1/faceswap-v2"
    
    source_base64 = image_file_to_base64(source_path)
    target_base64 = image_file_to_base64(target_path)
    
    data = {
        "source_img": source_base64,
        "target_img": target_base64,
        "input_faces_index": 0,
        "source_faces_index": 0,
        "face_restore": "codeformer-v0.1.0.pth",
        "base64": False
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=data, headers=headers, timeout=60)
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
            "test_type": "retest_batch",
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
        print(f"❌ Error: {e}")
        return False, None

def run_retest_batch():
    """Run V2 batch testing on re-test images"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("❌ API key not found")
        return
    
    # Setup paths
    source_dir = "test-results/re-test-v2/source_images"
    target_dir = "test-results/re-test-v2/target_images" 
    results_dir = "test-results/re-test-v2-results"
    
    # Check directories exist
    if not os.path.exists(source_dir) or not os.path.exists(target_dir):
        print("❌ Source or target directories not found")
        print(f"Looking for: {source_dir} and {target_dir}")
        return
    
    os.makedirs(results_dir, exist_ok=True)
    
    # Get all images
    source_images = sorted(glob.glob(f"{source_dir}/*"))
    target_images = sorted(glob.glob(f"{target_dir}/*"))
    
    # Filter out non-image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    source_images = [f for f in source_images if os.path.splitext(f.lower())[1] in image_extensions]
    target_images = [f for f in target_images if os.path.splitext(f.lower())[1] in image_extensions]
    
    print(f"🎯 Re-test V2 Batch Testing")
    print(f"Found {len(source_images)} source images")
    print(f"Found {len(target_images)} target images")
    print(f"Total combinations: {len(source_images)} × {len(target_images)} = {len(source_images) * len(target_images)}")
    
    if not source_images or not target_images:
        print("❌ No valid image files found")
        return
    
    # Check existing results
    existing_results = glob.glob(f"{results_dir}/*_result.jpg")
    print(f"📊 Found {len(existing_results)} existing results")
    
    total_combinations = len(source_images) * len(target_images)
    print(f"⏳ Estimated time: ~{total_combinations * 4 // 60} minutes")
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    # Test all combinations
    test_counter = 0
    for i, source_path in enumerate(source_images):
        source_name = os.path.splitext(os.path.basename(source_path))[0]
        source_clean = f"src_{i+1:02d}"  # Clean naming
        
        for j, target_path in enumerate(target_images):
            target_name = os.path.splitext(os.path.basename(target_path))[0] 
            target_clean = f"tgt_{j+1:02d}"  # Clean naming
            
            test_counter += 1
            combo_key = f"{source_clean}_to_{target_clean}"
            
            # Check if already done
            output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
            if os.path.exists(output_path):
                print(f"[{test_counter}/{total_combinations}] ⏭️  {combo_key} (exists)")
                successful += 1
                continue
            
            print(f"\n[{test_counter}/{total_combinations}] Testing: {combo_key}")
            print(f"  Source: {os.path.basename(source_path)}")
            print(f"  Target: {os.path.basename(target_path)}")
            
            metadata_path = f"{results_dir}/{combo_key}_v2_metadata.json"
            
            success, gen_time = perform_v2_face_swap(source_path, target_path, output_path, metadata_path)
            
            if success:
                successful += 1
                print(f"  ✅ Success ({gen_time}s)")
            else:
                failed += 1
                print(f"  ❌ Failed")
            
            # Progress update every 5 tests
            if test_counter % 5 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / test_counter
                remaining = total_combinations - test_counter
                eta_minutes = (remaining * avg_time) / 60
                
                print(f"\n📊 Progress: {test_counter}/{total_combinations} ({test_counter/total_combinations*100:.1f}%)")
                print(f"⏱️  ETA: {eta_minutes:.1f} minutes")
                print(f"✅ Success rate: {successful/test_counter*100:.1f}%")
            
            time.sleep(1)  # Rate limiting
    
    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\n🎉 Re-test V2 Batch Complete!")
    print(f"📊 Final Results:")
    print(f"   Total combinations: {total_combinations}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Success rate: {successful/total_combinations*100:.1f}%")
    print(f"   Total time: {elapsed_total/60:.1f} minutes")
    print(f"📁 Results saved to: {results_dir}")

def check_progress():
    """Check current progress"""
    results_dir = "test-results/re-test-v2-results"
    if not os.path.exists(results_dir):
        print("No results found yet")
        return
    
    results = glob.glob(f"{results_dir}/*_result.jpg")
    source_dir = "test-results/re-test-v2/source_images"
    target_dir = "test-results/re-test-v2/target_images"
    
    source_count = len([f for f in glob.glob(f"{source_dir}/*") if os.path.splitext(f.lower())[1] in {'.jpg', '.jpeg', '.png', '.gif'}])
    target_count = len([f for f in glob.glob(f"{target_dir}/*") if os.path.splitext(f.lower())[1] in {'.jpg', '.jpeg', '.png', '.gif'}])
    
    expected_total = source_count * target_count
    completed = len(results)
    
    print(f"📊 Re-test V2 Progress:")
    print(f"   Completed: {completed}/{expected_total} ({completed/expected_total*100:.1f}%)")
    print(f"   Sources: {source_count}, Targets: {target_count}")

if __name__ == "__main__":
    print("🎯 Re-test V2 Batch Testing")
    print("=" * 40)
    print("Testing all combinations from test-results/re-test-v2/")
    print()
    
    check_progress()
    print()
    run_retest_batch()