#!/usr/bin/env python3
"""
Continue single face testing - V4 only
"""

from batch_test_single_face import perform_face_swap_v4, load_api_key
import glob
import os
import time

def continue_v4_only_testing(max_tests=3):
    """Continue V4 testing only with longer timeout"""
    
    # Setup
    source_images = sorted(glob.glob("source-single-face/*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.png"))
    results_dir = "test-results/single-face-results"
    
    print(f"🎯 Continue Single Face Testing (V4 Only)")
    print(f"Sources: {len(source_images)}, Targets: {len(target_images)}")
    print(f"⏱️  Using 120s timeout for V4 API calls")
    
    # Find missing V4 tests only
    missing_v4_tests = []
    for i, source_path in enumerate(source_images, 1):
        source_clean = f"source_{i:02d}"
        
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.splitext(os.path.basename(target_path))[0]
            combo_key = f"{source_clean}_to_{target_name}"
            
            # Check V4 result only
            v4_output_path = f"{results_dir}/{combo_key}_v4_result.jpg"
            if not os.path.exists(v4_output_path):
                missing_v4_tests.append({
                    'source_path': source_path,
                    'target_path': target_path,
                    'combo_key': combo_key,
                    'output_path': v4_output_path,
                    'metadata_path': f"{results_dir}/{combo_key}_v4_metadata.json"
                })
    
    total_v4_expected = len(source_images) * len(target_images)
    completed_v4 = total_v4_expected - len(missing_v4_tests)
    
    print(f"📊 V4 progress: {completed_v4}/{total_v4_expected} ({completed_v4/total_v4_expected*100:.1f}%)")
    print(f"⏳ Missing V4 tests: {len(missing_v4_tests)}")
    
    if not missing_v4_tests:
        print("🎉 All V4 tests completed!")
        return
    
    # Run next batch of V4 tests
    tests_to_run = min(max_tests, len(missing_v4_tests))
    print(f"🚀 Running next {tests_to_run} V4 tests...")
    
    successful = 0
    for i, test in enumerate(missing_v4_tests[:tests_to_run]):
        print(f"[{i+1}/{tests_to_run}] {test['combo_key']} (V4)")
        
        success, gen_time = perform_face_swap_v4(
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
        
        time.sleep(2)  # Longer rate limiting for V4
    
    new_completed = completed_v4 + successful
    print(f"\n📊 Updated V4 progress: {new_completed}/{total_v4_expected} ({new_completed/total_v4_expected*100:.1f}%)")
    print(f"✅ This batch: {successful}/{tests_to_run} successful")
    
    if new_completed < total_v4_expected:
        print(f"⏳ Still need {total_v4_expected - new_completed} more V4 tests")
    else:
        print("🎉 All V4 tests complete! Single-face testing finished.")

if __name__ == "__main__":
    print("🔄 Continue Single Face Testing (V4 Only)")
    print("=" * 45)
    continue_v4_only_testing(max_tests=3)