#!/usr/bin/env python3
"""
Batch test the extracted reference images using V2 API only
Tests each source-target pair as single face swaps
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
        response = requests.post(API_URL, json=data, headers=headers)
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
        print(f"❌ V2 Error: {e}")
        return False, None

def run_reference_batch_tests():
    """Run V2 batch tests on extracted reference images"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    # Create results directory
    results_dir = "test-results/reference-v2-results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Get all extracted pairs
    target_dir = "reference_files/extracted-targets"
    source_dir = "reference_files/extracted-sources"
    
    if not os.path.exists(target_dir) or not os.path.exists(source_dir):
        print("❌ Extracted images not found. Run split_reference_images.py first.")
        return
    
    target_images = sorted(glob.glob(f"{target_dir}/target_*.png"))
    source_images = sorted(glob.glob(f"{source_dir}/source_*.png"))
    
    print(f"🎯 Reference V2 Batch Testing")
    print(f"Found {len(target_images)} target images")
    print(f"Found {len(source_images)} source images")
    
    if len(target_images) != len(source_images):
        print("❌ Target and source image counts don't match!")
        return
    
    total_tests = len(target_images)
    print(f"Total tests to run: {total_tests}")
    print(f"Estimated time: ~{(total_tests * 4) // 60} minutes")
    
    # Check for existing results
    existing_results = glob.glob(f"{results_dir}/*_v2_result.jpg")
    if existing_results:
        print(f"⚠️  Found {len(existing_results)} existing results")
        response = input("Continue from where we left off? (y/n): ").lower()
        if response != 'y':
            return
    
    input("Press Enter to start batch testing...")
    
    successful_tests = 0
    failed_tests = 0
    total_time = 0
    
    start_time = time.time()
    
    # Test each pair
    for i in range(len(target_images)):
        target_path = target_images[i]
        source_path = source_images[i]
        
        # Extract pair number from filename
        target_name = os.path.basename(target_path).replace('.png', '')
        source_name = os.path.basename(source_path).replace('.png', '')
        
        combo_key = f"{source_name}_to_{target_name}"
        
        # Check if already done
        output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
        if os.path.exists(output_path):
            print(f"[{i+1}/{total_tests}] ⏭️  Skipping {combo_key} (already exists)")
            successful_tests += 1
            continue
        
        print(f"\n[{i+1}/{total_tests}] Testing: {combo_key}")
        print(f"  Source: {os.path.basename(source_path)}")
        print(f"  Target: {os.path.basename(target_path)}")
        
        metadata_path = f"{results_dir}/{combo_key}_v2_metadata.json"
        
        success, gen_time = perform_v2_face_swap(source_path, target_path, output_path, metadata_path)
        
        if success:
            successful_tests += 1
            print(f"  ✅ Success ({gen_time}s)")
            if gen_time and gen_time != 'N/A':
                try:
                    total_time += float(gen_time)
                except:
                    pass
        else:
            failed_tests += 1
            print(f"  ❌ Failed")
        
        # Progress update every 5 tests
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start_time
            avg_time_per_test = elapsed / (i + 1)
            remaining_tests = total_tests - (i + 1)
            eta_seconds = remaining_tests * avg_time_per_test
            eta_minutes = eta_seconds / 60
            
            print(f"\n📊 Progress: {i+1}/{total_tests} ({(i+1)/total_tests*100:.1f}%)")
            print(f"⏱️  ETA: {eta_minutes:.1f} minutes")
            print(f"✅ Success rate: {successful_tests/(i+1)*100:.1f}%")
        
        # Rate limiting
        time.sleep(1)
    
    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\n🎉 Reference Batch Testing Complete!")
    print(f"📊 Results Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {successful_tests/total_tests*100:.1f}%")
    print(f"   Total elapsed time: {elapsed_total/60:.1f} minutes")
    if total_time > 0:
        print(f"   Average API generation time: {total_time/successful_tests:.2f}s")
    print(f"\n📁 Results saved to: {results_dir}")
    print(f"   {successful_tests} result images")
    print(f"   {successful_tests} metadata files")
    
    # Generate review page
    print(f"\n🔍 Next steps:")
    print(f"   - Results saved in separate folder for reference testing")
    print(f"   - Create custom review page for these results if needed")

def check_progress():
    """Check current progress of reference batch testing"""
    results_dir = "test-results/reference-v2-results"
    if not os.path.exists(results_dir):
        print("No reference testing results found yet.")
        return
    
    existing_results = glob.glob(f"{results_dir}/*_v2_result.jpg")
    target_images = glob.glob("reference_files/extracted-targets/target_*.png")
    
    total_expected = len(target_images)
    completed = len(existing_results)
    
    print(f"📊 Reference V2 Testing Progress:")
    print(f"   Completed: {completed}/{total_expected} ({completed/total_expected*100:.1f}%)")
    print(f"   Remaining: {total_expected - completed}")

def main():
    """Main function"""
    print("🎯 Reference Image V2 Batch Testing")
    print("=" * 40)
    print("This will test the extracted reference image pairs using V2 API.")
    print("Each source-target pair will be tested with single face swapping.\n")
    
    # Show current progress
    check_progress()
    print()
    
    run_reference_batch_tests()

if __name__ == "__main__":
    main()