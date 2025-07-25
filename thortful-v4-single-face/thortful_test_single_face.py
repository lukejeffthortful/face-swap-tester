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

# List of card IDs to test against - mapping to target template names
CARD_TARGETS = {
    "67816ae75990fc276575cd07": "card_template_01",
    "6855c0b6ebba0773538e8a15": "card_template_02", 
    "66facc0a21fd6d6f34901ae6": "card_template_03",
    "66e01c85ded8e0212043629d": "card_template_04",
    "67d219a67d3f9803484845be": "card_template_05",
    "68497934ad723e68b9792266": "card_template_06",
    "680b65d36010d4505cbac642": "card_template_07",
    "6854af2294654d25b467e33b": "card_template_08",
    "68097dd5b46c0a5b4e3543f8": "card_template_09",
    "680b635ab4259a1b1933d009": "card_template_10",
    "67a5f37990a11d443906b288": "card_template_11",
    "6855c9e992228930bed19c3f": "card_template_12",
    "68470d697fd84e35a7c920ea": "card_template_13",
    "67c6da4db6fbc326d4bcaafb": "card_template_14",
    "680b651fe5a5d97911059508": "card_template_15",
    "6806c1a93e7fe4028a4b7cb0": "card_template_16",
    "6815e812b4259a1b1933d422": "card_template_17",
    "68470f0a7ecd4e71abd58c2a": "card_template_18",
    "6806ad073175fb6967ec2768": "card_template_19",
    "6820935e0e882b1e7d33c35a": "card_template_20",
    "66e450c1e69c5e3a7f18b418": "card_template_21",
    "66ea83ce2975504ebe65683b": "card_template_22",
    "67a22d9106eb6b5e764650bc": "card_template_23",
    "68097b1dbb56f6239add6126": "card_template_24",
    "678e67f42c87c917d7245ad0": "card_template_25",
    "67c5d88150ca0b7dedab7d56": "card_template_26"
}

CARD_IDS = list(CARD_TARGETS.keys())

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

def run_single_face_swap(source_path, target_path, card_id, auth_headers, max_retries=3):
    """
    Perform single face swap using Thortful API with retry logic for 504 errors
    Returns result data dictionary
    """
    start_time = time.time()
    last_error = None
    
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
        
        # Retry logic for 504 Gateway Timeout errors
        response = None
        for attempt in range(max_retries):
            try:
                # Make API request (timeout set to 180s to work with gateway limits)
                response = requests.post(
                    API_ENDPOINT,
                    headers=auth_headers,
                    json=payload,
                    timeout=180  # Reduced from 300s to work better with gateway
                )
                break  # Success, exit retry loop
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout on attempt {attempt + 1}: {str(e)}"
                print(f"⚠️ Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print(f"   Retrying in 10 seconds...")
                    time.sleep(10)
                continue
            except Exception as e:
                last_error = str(e)
                print(f"⚠️ Error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    print(f"   Retrying in 10 seconds...")
                    time.sleep(10)
                continue
        
        if response is None:
            # All retries failed
            request_time = time.time() - start_time
            print(f"❌ All {max_retries} attempts failed")
            return {
                'success': False,
                'result_image': 'timeout_error',
                'generation_time': 'timeout_error',
                'request_time': f"{request_time:.3f}",
                'error_message': f"Failed after {max_retries} attempts: {last_error}",
                'raw_response': {}
            }
        
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
            
            # Extract generation time from various possible fields
            generation_time = 'unknown'
            possible_time_fields = ['generation_time', 'processing_time', 'duration', 'time_taken', 'elapsed_time']
            for field in possible_time_fields:
                if field in result_data and result_data[field] not in [None, '', 'unknown']:
                    generation_time = result_data[field]
                    break
            
            # If no specific generation time, use request time as fallback
            if generation_time == 'unknown':
                generation_time = f"{request_time:.3f}"
            
            return {
                'success': True,
                'result_image': result_filename,
                'generation_time': generation_time,
                'request_time': f"{request_time:.3f}",
                'error_message': '',
                'raw_response': result_data
            }
            
        else:
            # Handle 504 Gateway Timeout specifically with retry
            if response.status_code == 504:
                print(f"❌ Gateway Timeout (504) - This is common with V4 processing")
                # For 504 errors, we could retry but the gateway timeout suggests the process is taking too long
                return {
                    'success': False,
                    'result_image': 'gateway_timeout',
                    'generation_time': 'gateway_timeout',
                    'request_time': f"{request_time:.3f}",
                    'error_message': f"Gateway Timeout (504) - V4 processing exceeded gateway limit (~60s)",
                    'raw_response': {}
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
    
    # Get the proper target template name from card_id
    target_template = CARD_TARGETS.get(card_id, f"card_template_{card_id[:8]}")
    
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            timestamp,
            source_path.name,
            target_template,  # Use the card template name instead of target_path.name
            card_id,
            result_data['result_image'],
            'v4-thortful',
            'single_face',
            result_data['success'],
            result_data['generation_time'],
            result_data['request_time'],
            result_data['error_message'],
            f'Thortful API diverse face test - {target_template}'
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

def send_notification(message, is_error=False):
    """Send notification about script status"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "🚨 ERROR" if is_error else "ℹ️ INFO"
    full_message = f"{status} [{timestamp}] {message}"
    
    print(full_message)
    
    # Write to notification file for monitoring
    notification_file = LOGS_DIR / "script_status.log"
    with open(notification_file, 'a', encoding='utf-8') as f:
        f.write(f"{full_message}\n")
    
    # If this is an error, also write to separate error log
    if is_error:
        error_file = LOGS_DIR / "errors.log"
        with open(error_file, 'a', encoding='utf-8') as f:
            f.write(f"{full_message}\n")

def run_test_batch():
    """Run tests on all source/target image combinations with auto-restart capabilities"""
    max_failures = 10  # Maximum consecutive failures before stopping
    consecutive_failures = 0
    
    try:
        send_notification("🚀 Starting comprehensive face swap testing...")
        
        ensure_directories()
        create_csv_header()
        
        # Get authentication
        print("🔐 Getting Thortful authentication...")
        auth_headers = get_thortful_auth()
        if not auth_headers:
            send_notification("Failed to get authentication headers", is_error=True)
            return
        
        # Get source and target images
        source_images = list(SOURCE_DIR.glob('*.jpg')) + list(SOURCE_DIR.glob('*.png'))
        target_images = list(TARGET_DIR.glob('*.jpg')) + list(TARGET_DIR.glob('*.png'))
        
        if not source_images:
            send_notification(f"No source images found in {SOURCE_DIR}", is_error=True)
            return
            
        if not target_images:
            send_notification(f"No target images found in {TARGET_DIR}", is_error=True)
            return
        
        print(f"📊 Found {len(source_images)} source images and {len(target_images)} target images")
        print(f"🎯 Testing against {len(CARD_IDS)} card templates")
        total_tests = len(source_images) * len(target_images) * len(CARD_IDS)
        print(f"🔄 Running {total_tests} tests...")
        
        send_notification(f"Testing {total_tests} combinations ({len(source_images)} sources × {len(target_images)} targets × {len(CARD_IDS)} cards)")
        
        test_count = 0
        success_count = 0
        
        for source_path in source_images:
            for target_path in target_images:
                for card_id in CARD_IDS:
                    test_count += 1
                    print(f"\n=== Test {test_count}/{total_tests} ===")
                    
                    try:
                        # Run the test
                        result_data = run_single_face_swap(source_path, target_path, card_id, auth_headers)
                        
                        # Log the result
                        log_test_result(source_path, target_path, card_id, result_data)
                        
                        if result_data['success']:
                            success_count += 1
                            consecutive_failures = 0  # Reset failure counter on success
                            
                            # Log every 10th success
                            if success_count % 10 == 0:
                                send_notification(f"Progress: {success_count} successful tests completed ({test_count}/{total_tests} total)")
                        else:
                            consecutive_failures += 1
                            
                            # Check if we've hit too many consecutive failures
                            if consecutive_failures >= max_failures:
                                error_msg = f"❌ {max_failures} consecutive failures. Stopping to prevent infinite loop."
                                send_notification(error_msg, is_error=True)
                                send_notification(f"Last error: {result_data.get('error_message', 'Unknown error')}", is_error=True)
                                return
                        
                        # Commit to GitHub every 2 results
                        if test_count % 2 == 0:
                            try:
                                commit_to_github(test_count, total_tests, success_count)
                            except Exception as e:
                                send_notification(f"GitHub commit failed: {e}", is_error=True)
                        
                        # Brief pause between requests
                        time.sleep(1)
                        
                    except KeyboardInterrupt:
                        send_notification("❌ Script interrupted by user", is_error=True)
                        break
                    except Exception as e:
                        consecutive_failures += 1
                        send_notification(f"Unexpected error in test {test_count}: {e}", is_error=True)
                        
                        if consecutive_failures >= max_failures:
                            send_notification(f"❌ Too many consecutive errors. Stopping.", is_error=True)
                            return
                        
                        # Continue with next test after error
                        time.sleep(5)
        
        send_notification(f"✅ Testing completed! Results: {success_count}/{test_count} successful")
        print(f"\n✅ Testing complete!")
        print(f"📊 Results: {success_count}/{test_count} successful")
        print(f"📋 Detailed logs saved to: {LOG_FILE}")
        print(f"🖼️  Result images saved to: {RESULTS_DIR}")
        
        # Final commit to GitHub
        try:
            commit_to_github(test_count, total_tests, success_count)
            send_notification(f"Final results committed to GitHub: {success_count}/{test_count} successful")
        except Exception as e:
            send_notification(f"Final GitHub commit failed: {e}", is_error=True)
            
    except Exception as e:
        send_notification(f"❌ Critical error in run_test_batch: {e}", is_error=True)
        raise

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