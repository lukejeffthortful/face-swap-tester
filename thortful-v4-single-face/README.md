# Thortful Single Face V4 Testing

This directory contains a complete testing infrastructure for single face swapping using Thortful.com's face swap API (V4).

## Directory Structure

```
thortful-v4-single-face/
├── source-images/          # Source face images for testing
├── target-images/          # Target images to swap faces into  
├── results/                # Generated face swap results
├── logs/                   # CSV test logs and metadata
├── thortful_test_single_face.py    # Main testing script
├── thortful_review.html    # Web-based results viewer
├── serve_review.py         # HTTP server for review page
└── README.md              # This file
```

## Setup

### 1. Authentication Setup

The authentication is handled by the parent directory's `thortful_auth.py` module. It will:
- Try to authenticate with the provided credentials
- Fall back to using hardcoded headers from the example request if authentication fails
- Cache authentication tokens for reuse

### 2. Add Test Images

Add source and target images to test:

```bash
# Add source images (faces to swap FROM)
cp your_source_images/* source-images/

# Add target images (images to swap faces INTO)  
cp your_target_images/* target-images/
```

Supported formats: `.jpg`, `.png`

## Running Tests

### Single Test
Test a specific source/target combination:

```bash
python3 thortful_test_single_face.py --single source-images/source_01.jpg target-images/target_01.png
```

### Batch Testing
Test all source/target combinations:

```bash
python3 thortful_test_single_face.py
```

This will:
- Process all images in `source-images/` and `target-images/`
- Generate results for every source/target combination
- Save results to `results/` directory
- Log all test data to `logs/thortful_single_face_tests.csv`

## Viewing Results

### Web Interface
Start the web-based review interface:

```bash
python3 serve_review.py
```

This will:
- Start an HTTP server on port 8080
- Open the review page in your browser automatically
- Provide a dashboard with:
  - Test statistics and success rates
  - Filterable results grid
  - Side-by-side image comparisons
  - Performance metrics
  - Error details

### Manual Review
- **Images**: Check the `results/` directory for generated images
- **Logs**: View `logs/thortful_single_face_tests.csv` for detailed test data

## API Details

### Thortful Face Swap API V4
- **Endpoint**: `https://api.thortful.com/v1/faceswap?variation=false`
- **Method**: POST
- **Authentication**: API_KEY, API_SECRET, user_token, x-thortful-customer-id headers
- **Payload**: JSON with base64-encoded source and target images

### Test Parameters
- **API Version**: V4 (Thortful)
- **Test Type**: single_face
- **Face Restore**: Enabled
- **Upscale**: Disabled

## Log Format

The CSV log contains these columns:
- `timestamp`: Test execution time
- `source_image`: Source image filename
- `target_image`: Target image filename  
- `result_image`: Generated result filename
- `api_version`: v4-thortful
- `test_type`: single_face
- `success`: True/False
- `generation_time_seconds`: API processing time
- `request_time_seconds`: Total request time
- `error_message`: Error details (if any)
- `notes`: Additional metadata

## Troubleshooting

### Authentication Issues
- 401/403 errors usually indicate expired or invalid tokens
- The system will fall back to hardcoded headers from the example request
- Check `thortful_auth.json` for cached authentication data

### Image Issues
- Ensure images are in supported formats (.jpg, .png)
- Large images may take longer to process
- Check image file permissions

### API Issues
- The token from the example request may expire over time
- Rate limiting may apply to API requests
- Network connectivity issues can cause timeouts

## Example Workflow

1. **Setup images**:
   ```bash
   cp ../test-results/source-images/source_01.jpg source-images/
   cp ../test-results/single-face-target-images/target_01.png target-images/
   ```

2. **Run single test**:
   ```bash
   python3 thortful_test_single_face.py --single source-images/source_01.jpg target-images/target_01.png
   ```

3. **Start review server**:
   ```bash
   python3 serve_review.py
   ```

4. **View results**: Open http://localhost:8080/thortful_review.html

## Integration

This testing setup is designed to complement the main face swap testing infrastructure in the parent directory, providing:
- Isolated testing environment for Thortful API
- Consistent logging format for cross-API comparisons
- Web-based review interface matching other test suites
- Automated batch testing capabilities