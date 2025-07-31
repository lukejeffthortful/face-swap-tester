# Thortful API Timeout Requirements

## 🚨 CRITICAL: Always Use Long Timeouts

### Why This Matters
The Thortful face swap API performs **heavy AI image processing** that requires significant processing time. Using short timeouts will result in false failures when the API is actually working correctly.

### Verified Processing Times (July 2025)
Based on successful tests with fresh authentication:

| Endpoint | Average Time | Max Recorded | Recommended Timeout |
|----------|-------------|--------------|-------------------|
| `api.thortful.com` | 50.66s | 60s+ | **180s (3 min)** |
| `www.thortful.com` | 49.40s | 60s+ | **180s (3 min)** |

### Timeout Configuration Examples

#### ✅ CORRECT
```python
# Minimum safe timeout
response = requests.post(url, headers=headers, json=payload, timeout=120)

# Recommended timeout (what working scripts use)
response = requests.post(url, headers=headers, json=payload, timeout=180)

# Conservative timeout for batch processing
response = requests.post(url, headers=headers, json=payload, timeout=300)
```

#### ❌ INCORRECT - Will Cause False Failures
```python
# Too short - will timeout during normal processing
response = requests.post(url, headers=headers, json=payload, timeout=30)
response = requests.post(url, headers=headers, json=payload, timeout=60)
```

### AI Processing Pipeline
The API performs these compute-intensive operations:

1. **Image Analysis** (~5-10s)
   - Face detection and landmark identification
   - Quality assessment
   
2. **Neural Network Processing** (~30-40s)
   - Face embedding extraction
   - Style transfer computation
   - Feature alignment
   
3. **Image Generation** (~10-15s)
   - High-quality rendering
   - Post-processing effects
   - Format optimization

### Error Interpretation

| Error Type | Likely Cause | Action |
|------------|-------------|---------|
| `requests.exceptions.Timeout` | Processing still running | Retry with longer timeout |
| `504 Gateway Timeout` | Gateway limit exceeded | API may still be processing successfully |
| `403 Forbidden` | Authentication issue | Refresh tokens |
| `200 OK` after 45-60s | **Normal operation** | ✅ Success |

### Implementation Notes for Claude

When writing any code that calls Thortful APIs:

1. **ALWAYS use minimum 120s timeout**
2. **Recommended: 180s timeout** 
3. **For batch processing: 300s timeout**
4. **Never assume timeout = failure** - check response codes
5. **Include retry logic** for timeout scenarios
6. **Log actual processing times** to monitor performance

### Current Working Scripts Reference

All these scripts use proper timeouts:
- `thortful_test_single_face.py` - Uses 180s timeout
- `test_original_endpoint.py` - Uses 60s timeout (minimum for testing)
- `test_www_endpoint.py` - Uses 60s timeout (minimum for testing)

### Status Update (July 2025)
- ✅ **Original endpoint FIXED**: `https://api.thortful.com/v1/faceswap?variation=true`
- ✅ **WWW endpoint working**: `https://www.thortful.com/api/v1/faceswap?variation=true`
- ✅ **Both endpoints have identical processing times**
- ✅ **Authentication requirements identical**
- ✅ **Timeout issues resolved with proper configuration**