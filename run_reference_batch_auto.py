#!/usr/bin/env python3
"""
Auto-run V2 batch testing on reference images (no input prompts)
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
            "test_type": "reference_batch",
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

def run_batch_in_chunks(chunk_size=5):
    """Run tests in small chunks to avoid timeouts"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("❌ API key not found")
        return
    
    # Setup
    results_dir = "test-results/reference-v2-results"
    os.makedirs(results_dir, exist_ok=True)
    
    target_images = sorted(glob.glob("reference_files/extracted-targets/target_*.png"))
    source_images = sorted(glob.glob("reference_files/extracted-sources/source_*.png"))
    
    if len(target_images) != len(source_images):
        print("❌ Mismatch in target/source counts")
        return
    
    total_tests = len(target_images)
    print(f"🎯 Reference V2 Batch Testing (Auto Mode)")
    print(f"Total tests: {total_tests}")
    print(f"Chunk size: {chunk_size}")
    
    # Find tests that still need to be done
    pending_tests = []
    for i in range(total_tests):
        target_path = target_images[i]
        source_path = source_images[i]
        
        target_name = os.path.basename(target_path).replace('.png', '')
        source_name = os.path.basename(source_path).replace('.png', '')
        combo_key = f"{source_name}_to_{target_name}"
        
        output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
        if not os.path.exists(output_path):
            pending_tests.append({
                'index': i + 1,
                'source_path': source_path,
                'target_path': target_path,
                'combo_key': combo_key,
                'output_path': output_path
            })
    
    completed_count = total_tests - len(pending_tests)
    print(f"📊 Progress: {completed_count}/{total_tests} already completed")
    print(f"⏳ Remaining: {len(pending_tests)} tests")
    
    if not pending_tests:
        print("🎉 All tests already completed!")
        return
    
    # Process in chunks
    successful = 0
    failed = 0
    
    for chunk_start in range(0, len(pending_tests), chunk_size):
        chunk = pending_tests[chunk_start:chunk_start + chunk_size]
        chunk_num = (chunk_start // chunk_size) + 1
        total_chunks = (len(pending_tests) + chunk_size - 1) // chunk_size
        
        print(f"\n🔄 Processing chunk {chunk_num}/{total_chunks} ({len(chunk)} tests)")
        
        for test in chunk:
            print(f"[{test['index']}/{total_tests}] {test['combo_key']}")
            
            metadata_path = test['output_path'].replace('_result.jpg', '_metadata.json')
            success, gen_time = perform_v2_face_swap(
                test['source_path'], 
                test['target_path'], 
                test['output_path'], 
                metadata_path
            )
            
            if success:
                successful += 1
                print(f"  ✅ Success ({gen_time}s)")
            else:
                failed += 1
                print(f"  ❌ Failed")
            
            time.sleep(1)  # Rate limiting
        
        print(f"📊 Chunk {chunk_num} complete: {successful + failed}/{completed_count + successful + failed} total")
    
    # Final summary
    final_completed = completed_count + successful
    print(f"\n🎉 Reference Batch Complete!")
    print(f"📊 Final Results:")
    print(f"   Total tests: {total_tests}")
    print(f"   Completed: {final_completed}")
    print(f"   This session: +{successful} successful, +{failed} failed")
    print(f"   Success rate: {final_completed/total_tests*100:.1f}%")
    print(f"📁 Results in: {results_dir}")

if __name__ == "__main__":
    run_batch_in_chunks(chunk_size=3)  # Small chunks to avoid timeouts