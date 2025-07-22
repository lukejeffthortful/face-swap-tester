#!/usr/bin/env python3
"""
Continue V2 batch testing in small chunks
"""

from batch_test_retest_v2 import perform_v2_face_swap, load_api_key
import glob
import os
import time

def continue_testing(max_tests=5):
    """Continue testing with a maximum number of tests"""
    
    # Setup
    source_dir = "test-results/re-test-v2/source_images"
    target_dir = "test-results/re-test-v2/target_images" 
    results_dir = "test-results/re-test-v2-results"
    
    source_images = sorted([f for f in glob.glob(f"{source_dir}/*") 
                           if os.path.splitext(f.lower())[1] in {'.jpg', '.jpeg', '.png', '.gif'}])
    target_images = sorted([f for f in glob.glob(f"{target_dir}/*") 
                           if os.path.splitext(f.lower())[1] in {'.jpg', '.jpeg', '.png', '.gif'}])
    
    # Find missing tests
    missing_tests = []
    for i, source_path in enumerate(source_images):
        source_clean = f"src_{i+1:02d}"
        
        for j, target_path in enumerate(target_images):
            target_clean = f"tgt_{j+1:02d}"
            combo_key = f"{source_clean}_to_{target_clean}"
            
            output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
            if not os.path.exists(output_path):
                missing_tests.append({
                    'source_path': source_path,
                    'target_path': target_path,
                    'combo_key': combo_key,
                    'output_path': output_path
                })
    
    completed = 49 - len(missing_tests)
    print(f"📊 Current progress: {completed}/49 ({completed/49*100:.1f}%)")
    print(f"⏳ Missing: {len(missing_tests)} tests")
    
    if not missing_tests:
        print("🎉 All tests completed!")
        return
    
    # Run next batch
    tests_to_run = min(max_tests, len(missing_tests))
    print(f"🚀 Running next {tests_to_run} tests...")
    
    successful = 0
    for i, test in enumerate(missing_tests[:tests_to_run]):
        print(f"[{i+1}/{tests_to_run}] {test['combo_key']}")
        
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
            print(f"  ❌ Failed")
        
        time.sleep(1)
    
    new_completed = completed + successful
    print(f"\n📊 Updated progress: {new_completed}/49 ({new_completed/49*100:.1f}%)")
    print(f"✅ This batch: {successful}/{tests_to_run} successful")
    
    if new_completed < 49:
        print(f"⏳ Still need {49 - new_completed} more tests")

if __name__ == "__main__":
    print("🔄 Continue Re-test V2 Batch")
    print("=" * 30)
    continue_testing(max_tests=3)  # Small batch to avoid timeouts