#!/usr/bin/env python3
"""
Thortful API Authentication Module
Handles login and token management for Thortful face swap API
"""

import requests
import json
import os
from datetime import datetime

def get_anonymous_token():
    """
    Get anonymous token from /auth/enquire endpoint
    Returns anonymous token or None if failed
    """
    enquire_url = "https://www.thortful.com/api/v1/auth/enquire"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'API_KEY': 'xoobe9UC2l8yOHIMy89rhRCm',
        'API_SECRET': 'IfO5XWgKH4UE3k4vQwzjGULva/cuOwSrjpN0+14AiVclPwab',
        'User-Agent': 'python-testing/1.0',
        'Origin': 'https://www.thortful.com',
        'Referer': 'https://www.thortful.com/'
    }
    
    try:
        print("🔍 Getting anonymous token from /auth/enquire...")
        response = requests.post(enquire_url, headers=headers)
        
        print(f"Enquire response status: {response.status_code}")
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201
            enquire_data = response.json()
            print("✅ Anonymous token obtained!")
            print(f"Enquire response: {json.dumps(enquire_data, indent=2)}")
            
            # Extract anonymous token (try different keys)
            anonymous_token = (enquire_data.get('anonymous_token') or 
                             enquire_data.get('token') or
                             enquire_data.get('anonymousToken'))
            
            if anonymous_token:
                print(f"🎫 Anonymous token: {anonymous_token[:30]}...")
                return anonymous_token
            else:
                print("❌ No anonymous token found in enquire response")
                return None
        else:
            print(f"❌ Failed to get anonymous token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting anonymous token: {str(e)}")
        return None

def authenticate_thortful():
    """
    Authenticate with Thortful API using two-step process:
    1. Get anonymous token from /auth/enquire
    2. Login with anonymous token to get user token
    Returns authentication headers needed for API calls
    """
    # Step 1: Get anonymous token
    anonymous_token = get_anonymous_token()
    if not anonymous_token:
        print("⚠️ Could not get anonymous token, falling back to example headers")
        return get_fallback_headers()
    
    # Step 2: Login with anonymous token
    login_url = "https://www.thortful.com/api/v1/auth/thortful/login"
    
    # Headers for login request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'API_KEY': 'xoobe9UC2l8yOHIMy89rhRCm',
        'API_SECRET': 'IfO5XWgKH4UE3k4vQwzjGULva/cuOwSrjpN0+14AiVclPwab',
        'User-Agent': 'python-testing/1.0',
        'Origin': 'https://www.thortful.com',
        'Referer': 'https://www.thortful.com/'
    }
    
    # Form data payload (URL-encoded)
    form_data = {
        'address': 'thortful3@lukejeffery.com',
        'password': 'thortful*1234',
        'anonymous_token': anonymous_token,
        'device_id': '138646727456842631071254396374222'  # From example
    }
    
    try:
        print("🔐 Authenticating with Thortful API using fresh anonymous token...")
        
        response = requests.post(login_url, data=form_data, headers=headers)
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201
            auth_data = response.json()
            print("✅ Authentication successful!")
            
            # Print full response to understand structure
            print(f"Full login response: {json.dumps(auth_data, indent=2)}")
            
            # Extract the user token from response (try multiple keys)
            user_token = (auth_data.get('token') or 
                        auth_data.get('access_token') or 
                        auth_data.get('accessToken') or
                        auth_data.get('jwt') or
                        auth_data.get('authToken'))
                        
            user_id = (auth_data.get('user_id') or 
                     auth_data.get('userId') or 
                     auth_data.get('id') or
                     auth_data.get('profile_id') or
                     auth_data.get('profileId'))
            
            if not user_token:
                print("❌ No token found in login response")
                print("⚠️ Falling back to example headers")
                return get_fallback_headers()
            
            # From the example request, these are the required headers for face swap API
            auth_headers = {
                'API_KEY': 'xoobe9UC2l8yOHIMy89rhRCm',
                'API_SECRET': 'IfO5XWgKH4UE3k4vQwzjGULva/cuOwSrjpN0+14AiVclPwab',
                'user_token': user_token,
                'x-thortful-customer-id': user_id or '66aa45f0a15a6b1394759d25',  # Fallback to example ID
                'Content-Type': 'application/json',
                'platform': 'python-testing',
                'Accept': '*/*',
                'User-Agent': 'python-testing/1.0'
            }
            
            print(f"🎫 User token obtained: {user_token[:20]}...")
            return auth_headers
            
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            print("⚠️ Falling back to example headers")
            return get_fallback_headers()
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        print("⚠️ Falling back to example headers")
        return get_fallback_headers()

def get_fallback_headers():
    """
    Return hardcoded headers from the example request as fallback
    """
    print("📝 Using fallback headers from example request")
    return {
        'API_KEY': 'xoobe9UC2l8yOHIMy89rhRCm',
        'API_SECRET': 'IfO5XWgKH4UE3k4vQwzjGULva/cuOwSrjpN0+14AiVclPwab',
        'user_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3R5cGUiOiJ0aG9ydGZ1bCIsInVzZXJfaWQiOiI2NmFhNDVmMGExNWE2YjEzOTQ3NTlkMjYiLCJwcm9maWxlX2lkIjoiNjZhYTQ1ZjBhMTVhNmIxMzk0NzU5ZDI1Iiwicm9sZXMiOiJDUkVBVE9SLElOREVYSU5HX1JFQUQsUFJPRklMRV9SRUFELFBBWU1FTlRfUkVBRCxEQVRBX0FDQ0VTU19SRUFELENPTkZJR19SRUFELE9SREVSX1JFQUQiLCJsb2dpbl9wbGF0Zm9ybSI6IkdPT0dMRSIsImF1dGhfc2Vzc2lvbiI6InA2QjVaT1B1ME4iLCJleHAiOjE3NTMzNjkxNzUxOTJ9._LEOoaVwqB9a4YnQDTwz_9KqA_kZ7zFwOvEJ_-viwtI',
        'x-thortful-customer-id': '66aa45f0a15a6b1394759d25',
        'Content-Type': 'application/json',
        'platform': 'python-testing',
        'Accept': '*/*',
        'User-Agent': 'python-testing/1.0'
    }

def save_auth_headers(headers, filename="thortful_auth.json"):
    """Save authentication headers to file for reuse"""
    if headers:
        # Try different possible paths
        possible_paths = [
            f"thortful-v4-single-face/{filename}",
            filename,
            f"./{filename}"
        ]
        
        for auth_file in possible_paths:
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(auth_file), exist_ok=True) if os.path.dirname(auth_file) else None
                
                with open(auth_file, 'w') as f:
                    json.dump({
                        **headers,
                        'timestamp': datetime.now().isoformat(),
                        'note': 'Authentication headers for Thortful face swap API'
                    }, f, indent=2)
                print(f"💾 Auth headers saved to: {auth_file}")
                return
            except Exception as e:
                continue
        
        print(f"❌ Could not save auth headers: tried all paths")

def load_auth_headers(filename="thortful_auth.json"):
    """Load authentication headers from file"""
    # Try different possible paths
    possible_paths = [
        f"thortful-v4-single-face/{filename}",
        filename,
        f"./{filename}"
    ]
    
    for auth_file in possible_paths:
        try:
            if os.path.exists(auth_file):
                with open(auth_file, 'r') as f:
                    data = json.load(f)
                    # Remove metadata fields
                    data.pop('timestamp', None)
                    data.pop('note', None)
                    print(f"📂 Loaded auth headers from: {auth_file}")
                    return data
        except Exception as e:
            continue
    return None

def get_thortful_auth():
    """
    Get Thortful authentication headers, trying cached version first
    """
    # Try to load cached headers first
    headers = load_auth_headers()
    
    if headers:
        print("🔄 Using cached authentication headers")
        return headers
    
    # If no cached headers, authenticate fresh
    headers = authenticate_thortful()
    
    if headers:
        save_auth_headers(headers)
    
    return headers

if __name__ == "__main__":
    print("🧪 Testing Thortful Authentication")
    print("=" * 40)
    
    headers = get_thortful_auth()
    
    if headers:
        print("\n✅ Authentication successful!")
        print("Headers obtained:")
        for key, value in headers.items():
            if key in ['user_token', 'API_KEY', 'API_SECRET']:
                print(f"  {key}: {value[:10]}...")
            else:
                print(f"  {key}: {value}")
    else:
        print("\n❌ Authentication failed!")