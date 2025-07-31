# Face Swap Tester - Claude Notes

## ⚠️ CRITICAL: Authentication Management

### Token Refresh Protocol
**ALWAYS refresh authentication tokens before running tests!**

1. **Check token status:** `cd /path/to/project && python3 thortful_auth.py`
2. **Force refresh:** Delete auth files first, then regenerate:
   ```bash
   rm thortful-v4-single-face/thortful_auth.json
   python3 thortful_auth.py
   ```
3. **Tokens expire frequently** - 403 errors usually indicate expired tokens

### Thortful API Authentication & Timeouts
- **Auth file:** `thortful-v4-single-face/thortful_auth.json`
- **Auth script:** `thortful_auth.py` (in project root)
- **Working endpoints:** 
  - `https://www.thortful.com/api/v1/faceswap?variation=true` ✅
  - `https://api.thortful.com/v1/faceswap?variation=true` ✅ (FIXED - now working!)
- **⚠️ CRITICAL TIMEOUT REQUIREMENTS:**
  - **Minimum timeout:** 120 seconds (2 minutes)
  - **Recommended timeout:** 180 seconds (3 minutes) 
  - **Processing time:** ~50 seconds average for single face swaps
  - **Reason:** Heavy AI image processing workload requires extended processing time
  - **Never use timeouts < 60s** - will cause false timeout errors

### Authentication Headers Required:
```json
{
  "API_KEY": "xoobe9UC2l8yOHIMy89rhRCm",
  "API_SECRET": "IfO5XWgKH4UE3k4vQwzjGULva/cuOwSrjpN0+14AiVclPwab",
  "user_token": "[FRESH_TOKEN_FROM_LOGIN]",
  "x-thortful-customer-id": "[USER_PROFILE_ID]",
  "Content-Type": "application/json",
  "platform": "python-testing",
  "Accept": "*/*",
  "User-Agent": "python-testing/1.0"
}
```

## How to Run Tests

### Thortful Single Face Tests (V4)
- **Main file:** `thortful-v4-single-face/thortful_test_single_face.py`
- **Auth file:** `thortful_auth.py` (project root)
- **Working endpoint:** `https://www.thortful.com/api/v1/faceswap?variation=true`
- **Features:**
  - Fresh token authentication with automatic refresh
  - Comprehensive CSV logging
  - V4 API integration with retry logic for timeouts
  - Batch processing with GitHub auto-commit
  - Web review interface at `thortful_review.html`
- **Usage:**
  ```bash
  # Single test
  python3 thortful_test_single_face.py --single diverse-source-images/diverse_face_01.jpg target-images/target_01.png [card_id]
  
  # Full batch test
  python3 thortful_test_single_face.py
  ```
- **⚠️ IMPORTANT:** All requests use 180s timeout due to heavy AI processing requirements

### Endpoint Testing Scripts
- **test_original_endpoint.py** - Test original API endpoint with proper timeouts
- **test_www_endpoint.py** - Test WWW endpoint with proper timeouts
- **test_both_endpoints.py** - Compare both endpoints (may timeout if run together)
- **Quick auth refresh:** `python3 thortful_auth.py`

## 🚨 AI Processing Timeout Guidelines

### Why Long Timeouts Are Required
Thortful's face swap API performs **heavy AI image processing** that requires significant compute time:
- **Face detection and analysis**
- **Neural network inference** 
- **Image generation and post-processing**
- **Quality assurance checks**

### Timeout Configuration Rules
```python
# ✅ CORRECT - Use generous timeouts
response = requests.post(url, timeout=180)  # 3 minutes
response = requests.post(url, timeout=120)  # 2 minutes minimum

# ❌ WRONG - Will cause false timeout errors
response = requests.post(url, timeout=30)   # Too short!
response = requests.post(url, timeout=60)   # Still risky
```

### Expected Processing Times
- **Single face swap:** 45-60 seconds average
- **Complex images:** Up to 90+ seconds
- **Network latency:** Additional 5-10 seconds
- **Safety margin:** Always add 60+ seconds buffer

### Error Handling
- **Timeout errors ≠ API failures** - Often means processing is just slow
- **504 Gateway Timeout** - Processing exceeded gateway limits, but API may still be working
- **Always retry once** on timeout before marking as failed

### Legacy Segmind Tests
#### Single Face Tests (Segmind V4)
- **File:** `continue_v4_with_logging.py`
- **Description:** Most up-to-date Python file for running Segmind V4 single face tests
- **Features:** 
  - Comprehensive CSV logging
  - V4 API integration with latest parameters
  - Batch processing capabilities
  - Error handling and progress tracking
- **Usage:** Run this file to perform single face swap tests using Segmind V4 API

#### Multi-Face Tests (Segmind V2 vs V4.3)
- **File:** `continue_multiface_v43_with_logging.py`
- **Description:** Main script for multi-face testing comparing V2 vs V4.3 APIs
- **Features:**
  - Contains both `perform_v2_multiface_swap_with_logging()` and `perform_v43_multiface_swap_with_logging()` functions
  - Comprehensive CSV logging for both APIs
  - Tests multiple faces (indices 0,1,2,3) simultaneously
  - Can run V2-only tests by calling V2 function separately
- **Usage:** Run this file for multi-face V2 vs V4.3 comparisons, or modify to run V2-only

#### Multi-Face Tests (Segmind V2 Only)
- **File:** `continue_multiface_v2_only.py`
- **Description:** Re-runs ALL V2 multi-face tests only, ignoring existing results
- **Features:**
  - V2-only multi-face testing with comprehensive CSV logging
  - Uses face indices [0,1,2,3,4] for both source and target
  - CodeFormer face restoration with fidelity 0.8
  - Separate CSV log file: `multiface_v2_only_requests_log.csv`
  - Batch processing with configurable max_tests parameter
- **Usage:** Run this file to re-run all V2 multi-face results from scratch