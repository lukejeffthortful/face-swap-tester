#!/usr/bin/env python3
"""
Debug V4 API issues and create detailed error report for developers
"""

import requests
import base64
import os
import json
from datetime import datetime
import time
import glob
import traceback
import sys

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
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def get_image_info(image_path):
    """Get basic image information"""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "file_size_bytes": get_file_size(image_path)
            }
    except Exception as e:
        return {
            "error": str(e),
            "file_size_bytes": get_file_size(image_path)
        }

def debug_v4_api_call(source_path, target_path, test_name, log_data):
    """Perform detailed V4 API call with comprehensive logging"""
    API_KEY = load_api_key()
    API_URL = "https://api.segmind.com/v1/faceswap-v4"
    
    print(f"🔍 Debug Test: {test_name}")
    
    # Prepare test data
    test_info = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "source_image": {
            "path": source_path,
            "filename": os.path.basename(source_path),
            "info": get_image_info(source_path)
        },
        "target_image": {
            "path": target_path,
            "filename": os.path.basename(target_path),
            "info": get_image_info(target_path)
        },
        "api_details": {
            "url": API_URL,
            "method": "POST",
            "timeout": 120
        }
    }
    
    try:
        # Encode images
        print(f"  📸 Encoding source: {os.path.basename(source_path)}")
        source_base64 = image_file_to_base64(source_path)
        source_base64_size = len(source_base64)
        
        print(f"  📸 Encoding target: {os.path.basename(target_path)}")
        target_base64 = image_file_to_base64(target_path)
        target_base64_size = len(target_base64)
        
        test_info["encoding"] = {
            "source_base64_length": source_base64_size,
            "target_base64_length": target_base64_size,
            "total_payload_size_approx": source_base64_size + target_base64_size
        }
        
        # Prepare request data
        data = {
            "source_image": source_base64,
            "target_image": target_base64,
            "source_face_index": 0,
            "target_face_index": 0,
            "detection_face_order": "big_to_small",
            "model_type": "quality",
            "swap_type": "face"
        }
        
        headers = {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        test_info["request_payload"] = {
            "source_face_index": 0,
            "target_face_index": 0,
            "detection_face_order": "big_to_small",
            "model_type": "quality",
            "swap_type": "face",
            "headers_sent": {k: v if k != 'x-api-key' else '[REDACTED]' for k, v in headers.items()}
        }
        
        print(f"  🚀 Making API request...")
        print(f"     Payload size: ~{(source_base64_size + target_base64_size) / 1024 / 1024:.1f}MB")
        
        # Make the request with detailed timing
        request_start = time.time()
        try:
            response = requests.post(API_URL, json=data, headers=headers, timeout=120)
            request_duration = time.time() - request_start
            
            test_info["response"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "request_duration_seconds": round(request_duration, 3),
                "content_length": len(response.content),
                "content_type": response.headers.get('Content-Type', 'unknown')
            }
            
            print(f"  ✅ Response received: {response.status_code} ({request_duration:.3f}s)")
            print(f"     Content-Length: {len(response.content)} bytes")
            print(f"     Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            # Check if response is successful
            if response.status_code == 200:
                # Try to determine response type
                content_type = response.headers.get('Content-Type', '')
                
                if 'image' in content_type or content_type == 'application/octet-stream':
                    # Binary image response (expected)
                    test_info["response"]["type"] = "binary_image"
                    test_info["response"]["success"] = True
                    print(f"  ✅ Received binary image data")
                    
                    # Save the result for inspection
                    output_path = f"debug_results/{test_name}_result.jpg"
                    os.makedirs("debug_results", exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    test_info["response"]["saved_to"] = output_path
                    
                elif 'json' in content_type:
                    # JSON response (might be error or different format)
                    try:
                        json_response = response.json()
                        test_info["response"]["type"] = "json"
                        test_info["response"]["json_content"] = json_response
                        print(f"  ⚠️  Received JSON response instead of binary image")
                        print(f"     JSON: {json_response}")
                    except:
                        test_info["response"]["type"] = "json_parse_error"
                        test_info["response"]["raw_content"] = response.text[:500]
                        print(f"  ❌ Failed to parse JSON response")
                else:
                    # Unknown response type
                    test_info["response"]["type"] = "unknown"
                    test_info["response"]["raw_content_preview"] = response.text[:500]
                    print(f"  ⚠️  Unknown response content type")
                    
            else:
                # HTTP error
                test_info["response"]["success"] = False
                test_info["response"]["error_text"] = response.text
                print(f"  ❌ HTTP Error: {response.status_code}")
                print(f"     Error: {response.text}")
                
                # Try to parse error as JSON
                try:
                    error_json = response.json()
                    test_info["response"]["error_json"] = error_json
                except:
                    pass
                    
        except requests.exceptions.Timeout:
            test_info["error"] = {
                "type": "timeout",
                "message": "Request timed out after 120 seconds",
                "duration": 120
            }
            print(f"  ❌ Request timed out after 120 seconds")
            
        except requests.exceptions.ConnectionError as e:
            test_info["error"] = {
                "type": "connection_error",
                "message": str(e)
            }
            print(f"  ❌ Connection error: {e}")
            
        except Exception as e:
            test_info["error"] = {
                "type": "unexpected_error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"  ❌ Unexpected error: {e}")
            
    except Exception as e:
        test_info["error"] = {
            "type": "setup_error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        print(f"  ❌ Setup error: {e}")
    
    # Add to log data
    log_data["tests"].append(test_info)
    return test_info

def create_developer_report():
    """Create comprehensive report for API developers"""
    print("🔍 V4 API Debug Report Generator")
    print("=" * 50)
    
    # Initialize log data
    log_data = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "purpose": "Debug V4 API issues for developer investigation",
            "python_version": sys.version,
            "requests_version": requests.__version__
        },
        "api_endpoint": "https://api.segmind.com/v1/faceswap-v4",
        "issue_summary": "V4 API calls timing out or failing during single-face testing",
        "test_configuration": {
            "timeout": 120,
            "source_face_index": 0,
            "target_face_index": 0,
            "detection_face_order": "big_to_small",
            "model_type": "quality",
            "swap_type": "face"
        },
        "tests": []
    }
    
    # Get test images
    source_images = sorted(glob.glob("source-single-face/*.jpg"))[:2]  # Test first 2 sources
    target_images = sorted(glob.glob("test-results/target-images/target_*.png"))[:3]  # Test first 3 targets
    
    print(f"🎯 Testing {len(source_images)} sources × {len(target_images)} targets = {len(source_images) * len(target_images)} combinations")
    
    # Run debug tests
    test_counter = 0
    for i, source_path in enumerate(source_images, 1):
        for j, target_path in enumerate(target_images, 1):
            test_counter += 1
            test_name = f"debug_test_{test_counter:02d}_source{i}_target{j}"
            
            print(f"\n[{test_counter}/{len(source_images) * len(target_images)}] {test_name}")
            debug_v4_api_call(source_path, target_path, test_name, log_data)
            
            # Small delay between tests
            time.sleep(1)
    
    # Generate summary
    successful_tests = len([t for t in log_data["tests"] if t.get("response", {}).get("success")])
    failed_tests = len(log_data["tests"]) - successful_tests
    
    log_data["summary"] = {
        "total_tests": len(log_data["tests"]),
        "successful": successful_tests,
        "failed": failed_tests,
        "success_rate": f"{successful_tests/len(log_data['tests'])*100:.1f}%" if log_data["tests"] else "0%"
    }
    
    # Save comprehensive report
    report_path = f"v4_api_debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n📊 Debug Summary:")
    print(f"   Total tests: {len(log_data['tests'])}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success rate: {log_data['summary']['success_rate']}")
    print(f"\n📁 Detailed report saved to: {report_path}")
    
    # Create developer instructions
    instructions = f"""
# V4 API Debug Report - Developer Instructions

## Issue Summary
The V4 faceswap API is experiencing timeouts and failures during automated testing.

## Reproduction Steps
1. Use the test images in this repository:
   - Source images: source-single-face/*.jpg 
   - Target images: test-results/target-images/target_*.png

2. API Endpoint: https://api.segmind.com/v1/faceswap-v4

3. Request Configuration:
   - source_face_index: 0
   - target_face_index: 0  
   - detection_face_order: "big_to_small"
   - model_type: "quality"
   - swap_type: "face"
   - timeout: 120 seconds

4. The detailed test results are in: {report_path}

## Key Issues Observed
- Request timeouts after 120 seconds
- Inconsistent response times (some succeed in 1-3s, others timeout)
- Success rate: {log_data['summary']['success_rate']}

## Test Environment
- Python {sys.version.split()[0]}
- requests library version: {requests.__version__}
- Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Files Provided
1. {report_path} - Complete debug log with request/response details
2. debug_results/ - Any successful response images for verification
3. Source images in source-single-face/ folder
4. Target images in test-results/target-images/ folder

Please investigate the timeout issues and inconsistent performance.
"""
    
    instructions_path = f"v4_api_debug_instructions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(instructions_path, 'w') as f:
        f.write(instructions)
    
    print(f"📋 Developer instructions saved to: {instructions_path}")
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review {report_path} for detailed error logs")
    print(f"   2. Share {instructions_path} and {report_path} with API developers")
    print(f"   3. Include source/target image samples for reproduction")
    
    return report_path, instructions_path

if __name__ == "__main__":
    create_developer_report()