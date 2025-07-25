#!/usr/bin/env python3
"""
Thortful Single Face V4 Testing Script

Tests single face swapping using Thortful.com's face swap API
Results logged to CSV and reviewed via web interface
"""

import sys
import os
sys.path.append('..')

import requests
import json
import base64
import csv
import time
import subprocess
from datetime import datetime
from pathlib import Path
from thortful_auth import get_thortful_auth

# Configuration
API_ENDPOINT = "https://api.thortful.com/v1/faceswap?variation=true"
SOURCE_DIR = Path("diverse-source-images")
TARGET_DIR = Path("target-images")
RESULTS_DIR = Path("results")
LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "thortful_diverse_face_tests.csv"

# List of card IDs to test against
CARD_IDS = [
    "67816ae75990fc276575cd07",
    "6855c0b6ebba0773538e8a15",
    "66facc0a21fd6d6f34901ae6",
    "66e01c85ded8e0212043629d",
    "67d219a67d3f9803484845be",
    "68497934ad723e68b9792266",
    "680b65d36010d4505cbac642",
    "6854af2294654d25b467e33b",
    "68097dd5b46c0a5b4e3543f8",
    "680b635ab4259a1b1933d009",
    "67a5f37990a11d443906b288",
    "6855c9e992228930bed19c3f",
    "68470d697fd84e35a7c920ea",
    "67c6da4db6fbc326d4bcaafb",
    "680b651fe5a5d97911059508",
    "6806c1a93e7fe4028a4b7cb0",
    "6815e812b4259a1b1933d422",
    "68470f0a7ecd4e71abd58c2a",
    "6806ad073175fb6967ec2768",
    "6820935e0e882b1e7d33c35a",
    "66e450c1e69c5e3a7f18b418",
    "66ea83ce2975504ebe65683b",
    "67a22d9106eb6b5e764650bc",
    "68097b1dbb56f6239add6126",
    "678e67f42c87c917d7245ad0",
    "67c5d88150ca0b7dedab7d56"
]

def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in [SOURCE_DIR, TARGET_DIR, RESULTS_DIR, LOGS_DIR]:
        directory.mkdir(exist_ok=True)

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_csv_header():
    """Create CSV log file with headers if it doesn't exist"""
    if not LOG_FILE.exists():
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'timestamp',
                'source_image', 
                'target_image',
                'card_id',
                'result_image',
                'api_version',
                'test_type',
                'success',
                'generation_time_seconds',
                'request_time_seconds', 
                'error_message',
                'notes'
            ])

def run_single_face_swap(source_path, target_path, card_id, auth_headers):
    """
    Perform single face swap using Thortful API
    Returns result data dictionary
    """
    start_time = time.time()
    
    try:
        # Encode images to base64
        print(f"📸 Encoding source image: {source_path.name}")
        source_base64 = encode_image_to_base64(source_path)
        
        print(f"📸 Encoding target image: {target_path.name}")
        target_base64 = encode_image_to_base64(target_path)
        
        # Prepare request payload based on Thortful API structure
        # Try both camelCase and snake_case to ensure compatibility
        payload = {
            "source_image": source_base64,
            "targetCardId": card_id,      # camelCase version
            "target_card_id": card_id     # snake_case version (fallback)
        }
        
        print(f"🚀 Sending request to Thortful API...")
        print(f"   Source: {source_path.name}")
        print(f"   Target: {target_path.name}")
        print(f"   Card ID: {card_id}")
        print(f"   Payload keys: {list(payload.keys())}")
        print(f"   targetCardId: {payload.get('targetCardId', 'NOT_FOUND')}")
        
        # Make API request (increased timeout for V4 processing)
        response = requests.post(
            API_ENDPOINT,
            headers=auth_headers,
            json=payload,
            timeout=300
        )
        
        request_time = time.time() - start_time
        
        if response.status_code == 200:
            result_data = response.json()
            print(f"✅ Success! Processing took {request_time:.2f}s")
            
            # Print full API response for cost analysis
            print(f"📊 Full API Response: {json.dumps(result_data, indent=2)}")
            
            # Save result image if present in response
            result_filename = f"{source_path.stem}_to_{target_path.stem}_card_{card_id[:8]}_thortful_v4.jpg"
            result_path = RESULTS_DIR / result_filename
            
            # Handle different response formats
            if 'image' in result_data:
                # Save the result image
                result_image_data = base64.b64decode(result_data['image'])
                with open(result_path, 'wb') as f:
                    f.write(result_image_data)
                print(f"💾 Result saved: {result_filename}")
            elif 'result_url' in result_data:
                # Download from URL
                img_response = requests.get(result_data['result_url'])
                with open(result_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"💾 Result downloaded: {result_filename}")
            else:
                print("⚠️ No image data found in response")
                result_filename = "no_image_returned"
            
            return {
                'success': True,
                'result_image': result_filename,
                'generation_time': result_data.get('generation_time', 'unknown'),
                'request_time': f"{request_time:.3f}",
                'error_message': '',
                'raw_response': result_data
            }
            
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return {
                'success': False,
                'result_image': 'error',
                'generation_time': 'error',
                'request_time': f"{request_time:.3f}",
                'error_message': f"HTTP {response.status_code}: {response.text}",
                'raw_response': {}
            }
            
    except Exception as e:
        request_time = time.time() - start_time
        print(f"❌ Exception: {str(e)}")
        return {
            'success': False,
            'result_image': 'exception',
            'generation_time': 'exception',
            'request_time': f"{request_time:.3f}",
            'error_message': str(e),
            'raw_response': {}
        }

def log_test_result(source_path, target_path, card_id, result_data):
    """Log test result to CSV file"""
    timestamp = datetime.now().isoformat()
    
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp,
            source_path.name,
            target_path.name,
            card_id,
            result_data['result_image'],
            'v4-thortful',
            'single_face',
            result_data['success'],
            result_data['generation_time'],
            result_data['request_time'],
            result_data['error_message'],
            f'Thortful API diverse face test - Card {card_id[:8]}'
        ])

def commit_to_github(test_count, total_tests, success_count):
    """Commit results to GitHub and push to origin"""
    try:
        print(f"📤 Committing results to GitHub after {test_count} tests...")
        
        # Add all new files
        subprocess.run(['git', 'add', '.'], check=True, cwd='.')
        
        # Create commit message
        commit_msg = f"""Diverse face testing progress: {test_count}/{total_tests} tests completed

- Tests completed: {test_count}
- Successful: {success_count}
- Success rate: {success_count/test_count*100:.1f}%
- Results available at: https://lukejeffthortful.github.io/face-swap-tester/thortful-v4-single-face/

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, cwd='.')
        
        # Push to GitHub
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, cwd='.')
        
        print(f"✅ Successfully pushed to GitHub! Public URL: https://lukejeffthortful.github.io/face-swap-tester/thortful-v4-single-face/")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ GitHub commit failed: {e}")
        print("Continuing with testing...")
    except Exception as e:
        print(f"⚠️ Unexpected error during GitHub commit: {e}")
        print("Continuing with testing...")

def run_test_batch():
    """Run tests on all source/target image combinations"""
    ensure_directories()
    create_csv_header()
    
    # Get authentication
    print("🔐 Getting Thortful authentication...")
    auth_headers = get_thortful_auth()
    if not auth_headers:
        print("❌ Failed to get authentication headers")
        return
    
    # Get source and target images
    source_images = list(SOURCE_DIR.glob('*.jpg')) + list(SOURCE_DIR.glob('*.png'))
    target_images = list(TARGET_DIR.glob('*.jpg')) + list(TARGET_DIR.glob('*.png'))
    
    if not source_images:
        print(f"❌ No source images found in {SOURCE_DIR}")
        print(f"   Please add diverse source images (.jpg, .png) to test")
        return
        
    if not target_images:
        print(f"❌ No target images found in {TARGET_DIR}")
        print(f"   Please add target images (.jpg, .png) to test")
        return
    
    print(f"📊 Found {len(source_images)} source images and {len(target_images)} target images")
    print(f"🎯 Testing against {len(CARD_IDS)} card templates")
    total_tests = len(source_images) * len(target_images) * len(CARD_IDS)
    print(f"🔄 Running {total_tests} tests...")
    
    test_count = 0
    success_count = 0
    
    for source_path in source_images:
        for target_path in target_images:
            for card_id in CARD_IDS:
                test_count += 1
                print(f"\n=== Test {test_count}/{total_tests} ===")
                
                # Run the test
                result_data = run_single_face_swap(source_path, target_path, card_id, auth_headers)
                
                # Log the result
                log_test_result(source_path, target_path, card_id, result_data)
                
                if result_data['success']:
                    success_count += 1
                
                # Commit to GitHub every 5 results
                if test_count % 5 == 0:
                    commit_to_github(test_count, total_tests, success_count)
                
                # Brief pause between requests
                time.sleep(1)
    
    print(f"\n✅ Testing complete!")
    print(f"📊 Results: {success_count}/{test_count} successful")
    print(f"📋 Detailed logs saved to: {LOG_FILE}")
    print(f"🖼️  Result images saved to: {RESULTS_DIR}")
    
    # Final commit to GitHub
    commit_to_github(test_count, total_tests, success_count)

def main():
    """Main function"""
    print("🧪 Thortful Diverse Face V4 Testing")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--single':
            # Single test mode
            if len(sys.argv) < 4:
                print("Usage: python thortful_test_single_face.py --single <source_image> <target_image> [card_id]")
                return
            
            source_path = Path(sys.argv[2])
            target_path = Path(sys.argv[3])
            card_id = sys.argv[4] if len(sys.argv) > 4 else CARD_IDS[0]  # Use first card ID as default
            
            if not source_path.exists():
                print(f"❌ Source image not found: {source_path}")
                return
                
            if not target_path.exists():
                print(f"❌ Target image not found: {target_path}")
                return
            
            ensure_directories()
            create_csv_header()
            
            # Get authentication
            auth_headers = get_thortful_auth()
            if not auth_headers:
                print("❌ Failed to get authentication headers")
                return
            
            # Run single test
            result_data = run_single_face_swap(source_path, target_path, card_id, auth_headers)
            log_test_result(source_path, target_path, card_id, result_data)
            
            print(f"\n✅ Single test complete!")
            if result_data['success']:
                print(f"🖼️  Result saved: {result_data['result_image']}")
            else:
                print(f"❌ Test failed: {result_data['error_message']}")
        else:
            print("Usage: python thortful_test_single_face.py [--single <source> <target>]")
    else:
        # Batch test mode
        run_test_batch()

if __name__ == "__main__":
    main()