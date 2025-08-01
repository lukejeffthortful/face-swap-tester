
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

4. The detailed test results are in: v4_api_debug_report_20250722_154145.json

## Key Issues Observed
- Request timeouts after 120 seconds
- Inconsistent response times (some succeed in 1-3s, others timeout)
- Success rate: 50.0%

## Test Environment
- Python 3.9.6
- requests library version: 2.31.0
- Test date: 2025-07-22 15:41:45

## Files Provided
1. v4_api_debug_report_20250722_154145.json - Complete debug log with request/response details
2. debug_results/ - Any successful response images for verification
3. Source images in source-single-face/ folder
4. Target images in test-results/target-images/ folder

Please investigate the timeout issues and inconsistent performance.
