#!/usr/bin/env python3
"""
Run single face testing in batches with progress tracking
"""

import os
import glob
import subprocess
import time
from batch_test_single_face import perform_face_swap_v2, perform_face_swap_v4, load_api_key

def get_current_progress():
    """Check current test progress"""
    v2_files = glob.glob("test-results/single-face-results/*_v2_result.jpg")
    v4_files = glob.glob("test-results/single-face-results/*_v4_result.jpg")
    
    v2_count = len(v2_files)
    v4_count = len(v4_files)
    total_tests = v2_count + v4_count
    
    return {
        'v2_completed': v2_count,
        'v4_completed': v4_count,
        'total_completed': total_tests,
        'target_total': 80  # 40 combinations × 2 APIs
    }

def get_missing_tests():
    """Find which specific tests are missing"""
    source_images = sorted(glob.glob("source-single-face/*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.png"))
    
    missing_tests = []
    
    for i, source_path in enumerate(source_images, 1):
        source_clean = f"source_{i:02d}"
        
        for j, target_path in enumerate(target_images, 1):
            target_name = f"target_{j:02d}"
            combo_key = f"{source_clean}_to_{target_name}"
            
            # Check if V2 test exists
            v2_result = f"test-results/single-face-results/{combo_key}_v2_result.jpg"
            if not os.path.exists(v2_result):
                missing_tests.append({
                    'combo': combo_key,
                    'api': 'v2',
                    'source_path': source_path,
                    'target_path': target_path
                })
            
            # Check if V4 test exists  
            v4_result = f"test-results/single-face-results/{combo_key}_v4_result.jpg"
            if not os.path.exists(v4_result):
                missing_tests.append({
                    'combo': combo_key,
                    'api': 'v4',
                    'source_path': source_path,
                    'target_path': target_path
                })
    
    return missing_tests

def run_single_test(test_info):
    """Run a single test"""
    combo = test_info['combo']
    api = test_info['api']
    source_path = test_info['source_path']
    target_path = test_info['target_path']
    
    output_path = f"test-results/single-face-results/{combo}_{api}_result.jpg"
    metadata_path = f"test-results/single-face-results/{combo}_{api}_metadata.json"
    
    print(f"  Running {combo} with {api.upper()} API...")
    
    try:
        if api == 'v2':
            success, gen_time = perform_face_swap_v2(source_path, target_path, output_path, metadata_path)
        else:  # v4
            success, gen_time = perform_face_swap_v4(source_path, target_path, output_path, metadata_path)
        
        if success:
            print(f"    ✅ Success ({gen_time}s)")
            return True
        else:
            print(f"    ❌ Failed")
            return False
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def run_batch_with_progress(batch_size=5):
    """Run tests in batches with progress tracking"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("❌ API key not found")
        return
    
    # Create results directory
    os.makedirs("test-results/single-face-results", exist_ok=True)
    
    while True:
        # Check current progress
        progress = get_current_progress()
        missing_tests = get_missing_tests()
        
        print(f"\n📊 Current Progress: {progress['total_completed']}/{progress['target_total']} tests completed")
        print(f"   V2: {progress['v2_completed']}/40, V4: {progress['v4_completed']}/40")
        print(f"   Missing: {len(missing_tests)} tests")
        
        if not missing_tests:
            print("\n🎉 All tests completed!")
            break
        
        # Run next batch
        batch = missing_tests[:batch_size]
        print(f"\n🚀 Running batch of {len(batch)} tests...")
        
        successful = 0
        for test in batch:
            if run_single_test(test):
                successful += 1
            time.sleep(1)  # Rate limiting
        
        print(f"\n✅ Batch complete: {successful}/{len(batch)} successful")
        
        # Check if we should continue
        if successful == 0:
            print("❌ No successful tests in this batch. Stopping.")
            break
        
        # Small break between batches
        time.sleep(2)
    
    # Final progress check
    final_progress = get_current_progress()
    print(f"\n🏁 Final Results: {final_progress['total_completed']}/{final_progress['target_total']} tests completed")
    
    if final_progress['total_completed'] >= final_progress['target_total']:
        print("🎉 All single face tests completed successfully!")
        print("📄 Run generate_single_face_review.py to create the comparison page")
    else:
        print(f"⏸️  Partial completion: {final_progress['total_completed']} tests done")

if __name__ == "__main__":
    print("🔄 Single Face Testing - Batch Progress Mode")
    print("=" * 50)
    run_batch_with_progress(batch_size=5)