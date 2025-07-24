#!/usr/bin/env python3
"""
Re-run specific V2 multi-face tests that had incorrect results
"""

import csv
import os
import time
import json
import requests
import base64
from datetime import datetime
from batch_test_single_face import load_api_key

def get_file_size_kb(file_path):
    """Get file size in KB"""
    try:
        return round(os.path.getsize(file_path) / 1024, 2)
    except:
        return 0

def perform_v2_multiface_swap(source_path, target_path, output_path, metadata_path, combo_key):
    """Perform V2 multi-face swap for specific problematic combinations"""
    
    print(f"  🔄 Running V2 test: {combo_key}")
    
    try:
        API_KEY = load_api_key()
        API_URL = "https://api.segmind.com/v1/faceswap-v2"
        
        # Encode images
        with open(source_path, 'rb') as f:
            source_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open(target_path, 'rb') as f:
            target_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        data = {
            "source_img": source_base64,
            "target_img": target_base64,
            "source_faces_index": [0, 1, 2, 3, 4],
            "target_faces_index": [0, 1, 2, 3, 4],
            "face_restore": "codeformer-v0.1.0.pth",
            "base64": False
        }
        
        headers = {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Make request
        start_time = time.time()
        response = requests.post(API_URL, json=data, headers=headers, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            # Success - save files
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
                "test_type": "multi_face",
                "source_faces_index": [0, 1, 2, 3, 4],
                "target_faces_index": [0, 1, 2, 3, 4],
                "face_restore": "codeformer-v0.1.0.pth",
                "base64": False,
                "generation_time": response.headers.get('X-generation-time'),
                "remaining_credits": response.headers.get('X-remaining-credits'),
                "request_id": response.headers.get('X-Request-ID'),
                "request_time": f"{end_time - start_time:.3f}",
                "note": "Re-run due to incorrect target matching"
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"  ✅ Success ({response.headers.get('X-generation-time')}s)")
            return True
        else:
            print(f"  ❌ Failed: HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def rerun_specific_v2_tests():
    """Re-run specific problematic V2 multi-face combinations"""
    
    # Define the problematic combinations
    problematic_tests = [
        # source_02 + targets 04, 05, 07
        ("test-results/source-images/source_02.jpg", "test-results/multiface-target-images/target_04.png", "source_02_to_target_04"),
        ("test-results/source-images/source_02.jpg", "test-results/multiface-target-images/target_05.png", "source_02_to_target_05"),
        ("test-results/source-images/source_02.jpg", "test-results/multiface-target-images/target_07.png", "source_02_to_target_07"),
        # source_03 + targets 05, 06, 07
        ("test-results/source-images/source_03.jpg", "test-results/multiface-target-images/target_05.png", "source_03_to_target_05"),
        ("test-results/source-images/source_03.jpg", "test-results/multiface-target-images/target_06.png", "source_03_to_target_06"),
        ("test-results/source-images/source_03.jpg", "test-results/multiface-target-images/target_07.png", "source_03_to_target_07"),
    ]
    
    results_dir = "test-results/results"
    
    print(f"🎯 Re-running {len(problematic_tests)} specific V2 multi-face tests")
    print("=" * 60)
    
    successful = 0
    for i, (source_path, target_path, combo_key) in enumerate(problematic_tests, 1):
        print(f"\n[{i}/{len(problematic_tests)}] {combo_key}")
        
        # Check if source files exist
        if not os.path.exists(source_path):
            print(f"  ❌ Source not found: {source_path}")
            continue
        if not os.path.exists(target_path):
            print(f"  ❌ Target not found: {target_path}")
            continue
            
        output_path = f"{results_dir}/{combo_key}_v2_result.jpg"
        metadata_path = f"{results_dir}/{combo_key}_v2_metadata.json"
        
        success = perform_v2_multiface_swap(
            source_path, target_path, output_path, metadata_path, combo_key
        )
        
        if success:
            successful += 1
        
        time.sleep(3)  # Rate limiting
    
    print(f"\n📊 Re-run completed: {successful}/{len(problematic_tests)} successful")
    
    if successful == len(problematic_tests):
        print("🎉 All problematic V2 tests successfully re-run!")
    else:
        print(f"⚠️  {len(problematic_tests) - successful} tests still failed")

if __name__ == "__main__":
    print("🔄 Re-running Specific Problematic V2 Multi-Face Tests")
    print("=" * 60)
    rerun_specific_v2_tests()