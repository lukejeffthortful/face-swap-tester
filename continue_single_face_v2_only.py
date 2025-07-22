#!/usr/bin/env python3
"""
Continue single face testing - V2 only first
"""

from batch_test_single_face import perform_face_swap_v2, load_api_key
import glob
import os
import time

def continue_v2_only_testing(max_tests=5):
    """Continue V2 testing only"""
    
    # Setup
    source_images = sorted(glob.glob("source-single-face/*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.png"))
    results_dir = "test-results/single-face-results"
    
    print(f"🎯 Continue Single Face Testing (V2 Only)")
    print(f"Sources: {len(source_images)}, Targets: {len(target_images)}")
    
    # Find missing V2 tests only
    missing_v2_tests = []
    for i, source_path in enumerate(source_images, 1):
        source_clean = f"source_{i:02d}"
        
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.splitext(os.path.basename(target_path))[0]
            combo_key = f"{source_clean}_to_{target_name}"
            
            # Check V2 result only
            v2_output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
            if not os.path.exists(v2_output_path):
                missing_v2_tests.append({
                    'source_path': source_path,
                    'target_path': target_path,
                    'combo_key': combo_key,
                    'output_path': v2_output_path,
                    'metadata_path': f"{results_dir}/{combo_key}_v2_metadata.json"
                })
    
    total_v2_expected = len(source_images) * len(target_images)
    completed_v2 = total_v2_expected - len(missing_v2_tests)
    
    print(f"📊 V2 progress: {completed_v2}/{total_v2_expected} ({completed_v2/total_v2_expected*100:.1f}%)")
    print(f"⏳ Missing V2 tests: {len(missing_v2_tests)}")
    
    if not missing_v2_tests:
        print("🎉 All V2 tests completed!")
        return
    
    # Run next batch of V2 tests
    tests_to_run = min(max_tests, len(missing_v2_tests))
    print(f"🚀 Running next {tests_to_run} V2 tests...")
    
    successful = 0
    for i, test in enumerate(missing_v2_tests[:tests_to_run]):
        print(f"[{i+1}/{tests_to_run}] {test['combo_key']} (V2)")
        
        success, gen_time = perform_face_swap_v2(
            test['source_path'], 
            test['target_path'], 
            test['output_path'], 
            test['metadata_path']
        )
        
        if success:
            successful += 1
            print(f"  ✅ Success ({gen_time}s)")
        else:
            print(f"  ❌ Failed")
        
        time.sleep(1)
    
    new_completed = completed_v2 + successful
    print(f"\n📊 Updated V2 progress: {new_completed}/{total_v2_expected} ({new_completed/total_v2_expected*100:.1f}%)")
    print(f"✅ This batch: {successful}/{tests_to_run} successful")
    
    if new_completed < total_v2_expected:
        print(f"⏳ Still need {total_v2_expected - new_completed} more V2 tests")
    else:
        print("🎉 All V2 tests complete! Ready to start V4 tests.")

if __name__ == "__main__":
    print("🔄 Continue Single Face Testing (V2 Only)")
    print("=" * 45)
    continue_v2_only_testing(max_tests=5)