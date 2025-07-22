#!/usr/bin/env python3
"""
Continue single face testing in small chunks (auto-run, no prompts)
"""

from batch_test_single_face import perform_face_swap_v2, perform_face_swap_v4, load_api_key
import glob
import os
import time

def continue_single_face_testing(max_tests=1):
    """Continue single face testing with a maximum number of tests per batch"""
    
    # Setup
    source_images = sorted(glob.glob("source-single-face/*.jpg"))
    target_images = sorted(glob.glob("test-results/target-images/target_*.png"))
    results_dir = "test-results/single-face-results"
    
    print(f"🎯 Continue Single Face Testing (V2 vs V4)")
    print(f"Sources: {len(source_images)}, Targets: {len(target_images)}")
    
    # Find missing tests
    missing_tests = []
    for i, source_path in enumerate(source_images, 1):
        source_clean = f"source_{i:02d}"
        
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.splitext(os.path.basename(target_path))[0]
            combo_key = f"{source_clean}_to_{target_name}"
            
            # Check V2 result
            v2_output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
            if not os.path.exists(v2_output_path):
                missing_tests.append({
                    'source_path': source_path,
                    'target_path': target_path,
                    'combo_key': combo_key,
                    'api': 'v2',
                    'output_path': v2_output_path,
                    'metadata_path': f"{results_dir}/{combo_key}_v2_metadata.json"
                })
            
            # Check V4 result
            v4_output_path = f"{results_dir}/{combo_key}_v4_result.jpg"
            if not os.path.exists(v4_output_path):
                missing_tests.append({
                    'source_path': source_path,
                    'target_path': target_path,
                    'combo_key': combo_key,
                    'api': 'v4',
                    'output_path': v4_output_path,
                    'metadata_path': f"{results_dir}/{combo_key}_v4_metadata.json"
                })
    
    total_expected = len(source_images) * len(target_images) * 2  # V2 + V4
    completed = total_expected - len(missing_tests)
    
    print(f"📊 Current progress: {completed}/{total_expected} ({completed/total_expected*100:.1f}%)")
    print(f"⏳ Missing: {len(missing_tests)} tests")
    
    if not missing_tests:
        print("🎉 All single face tests completed!")
        return
    
    # Run next batch
    tests_to_run = min(max_tests, len(missing_tests))
    print(f"🚀 Running next {tests_to_run} tests...")
    
    successful = 0
    for i, test in enumerate(missing_tests[:tests_to_run]):
        print(f"[{i+1}/{tests_to_run}] {test['combo_key']} ({test['api'].upper()})")
        
        if test['api'] == 'v2':
            success, gen_time = perform_face_swap_v2(
                test['source_path'], 
                test['target_path'], 
                test['output_path'], 
                test['metadata_path']
            )
        else:  # v4
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
        
        time.sleep(2)  # Longer rate limiting
    
    new_completed = completed + successful
    print(f"\n📊 Updated progress: {new_completed}/{total_expected} ({new_completed/total_expected*100:.1f}%)")
    print(f"✅ This batch: {successful}/{tests_to_run} successful")
    
    if new_completed < total_expected:
        print(f"⏳ Still need {total_expected - new_completed} more tests")

if __name__ == "__main__":
    print("🔄 Continue Single Face Testing")
    print("=" * 35)
    continue_single_face_testing(max_tests=1)  # Run 1 test per batch