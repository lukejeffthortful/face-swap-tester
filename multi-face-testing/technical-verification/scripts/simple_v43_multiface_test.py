#!/usr/bin/env python3
"""
Simple V4.3 multi-face test - test 1 image successfully
"""

import requests
import base64
import os
import json
from datetime import datetime

def load_api_key():
    """Load API key from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('REACT_APP_SEGMIND_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return None

def test_v43_multiface():
    """Test V4.3 multi-face with one source and target"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("❌ Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return False
    
    # Use first source and first target
    source_path = "test-results/source-images/source_01.jpg"
    target_path = "test-results/multiface-target-images/target_01.png"
    output_path = "test-results/simple_v43_test_result.jpg"
    
    if not os.path.exists(source_path):
        print(f"❌ Source not found: {source_path}")
        return False
    
    if not os.path.exists(target_path):
        print(f"❌ Target not found: {target_path}")
        return False
    
    print("🧪 Testing V4.3 Multi-Face API")
    print(f"Source: {source_path}")
    print(f"Target: {target_path}")
    print(f"Output: {output_path}")
    
    try:
        # Load and encode images
        with open(source_path, 'rb') as f:
            source_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open(target_path, 'rb') as f:
            target_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # V4.3 multi-face parameters
        data = {
            "source_image": source_base64,
            "target_image": target_base64,
            "source_face_index": "0,1,2,3",
            "target_face_index": "0,1,2,3",
            "detection_face_order": "left_to_right",
            "model_type": "speed",
            "swap_type": "face"
        }
        
        headers = {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        print("📡 Making V4.3 API request...")
        start_time = datetime.now()
        
        response = requests.post(
            "https://api.segmind.com/v1/faceswap-v4.3", 
            json=data, 
            headers=headers, 
            timeout=120
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Request duration: {duration:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Save result
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Get response details
            gen_time = response.headers.get('X-generation-time', 'N/A')
            credits = response.headers.get('X-remaining-credits', 'N/A')
            request_id = response.headers.get('X-Request-ID', 'N/A')
            
            print(f"✅ SUCCESS!")
            print(f"📁 Result saved to: {output_path}")
            print(f"⚡ Generation time: {gen_time}s")
            print(f"💰 Remaining credits: {credits}")
            print(f"🆔 Request ID: {request_id}")
            
            # Save metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "source_image": os.path.basename(source_path),
                "target_image": os.path.basename(target_path),
                "output_image": os.path.basename(output_path),
                "api_version": "v4.3",
                "test_type": "simple_multiface_test",
                "source_face_index": "0,1,2,3",
                "target_face_index": "0,1,2,3",
                "detection_face_order": "big_to_small",
                "model_type": "speed",
                "swap_type": "face",
                "hardware_type": "cost",
                "request_duration_seconds": duration,
                "generation_time": gen_time,
                "remaining_credits": credits,
                "request_id": request_id,
                "success": True
            }
            
            with open(output_path.replace('.jpg', '_metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Simple V4.3 Multi-Face Test")
    print("=" * 40)
    success = test_v43_multiface()
    
    if success:
        print("\n🎉 V4.3 multi-face test completed successfully!")
    else:
        print("\n💥 V4.3 multi-face test failed!")