# Multi-Face Testing Suite

## Overview
This directory contains all multi-face swap testing functionality with support for multiple face detection and API version comparisons:

- **Batch Tests**: V2 vs V4.3 API comparisons with comprehensive face index testing
- **Technical Verification**: V2 API verification with multiple face indices

## Directory Structure

```
multi-face-testing/
├── batch-tests/
│   ├── logs/                  # CSV comparison logs (V2 vs V4.3)
│   ├── results/               # Side-by-side API comparison images
│   ├── scripts/               # Batch comparison scripts
│   ├── source-images/         # Multi-face source images
│   ├── target-images/         # Multi-face target templates
│   └── review.html           # Web interface for API comparisons
└── technical-verification/
    ├── logs/                  # CSV V2-only verification logs
    ├── results/               # V2 API verification results
    ├── scripts/               # V2 verification scripts
    └── review.html           # Web interface for verification results
```

## Key Scripts

### Batch Tests (V2 vs V4.3 Comparison)
- **`continue_multiface_v43_with_logging.py`**: Main script for V2 vs V4.3 API comparison
  - Tests both APIs on same source/target combinations
  - Comprehensive CSV logging for both versions
  - Side-by-side result comparison

### Technical Verification (V2 Only)
- **`continue_multiface_v2_only.py`**: V2-only multi-face testing
  - Face indices: [0,1,2,3,4] for comprehensive face detection
  - CodeFormer face restoration (fidelity 0.8)
  - Dedicated V2 result logging
- **`simple_v43_multiface_test.py`**: Simple V4.3 API test for verification

## Face Detection Features

### Multiple Face Indices
- **Source faces**: [0,1,2,3,4] - Detects up to 5 faces in source image
- **Target faces**: [0,1,2,3,4] - Replaces up to 5 faces in target image
- **Dynamic mapping**: Automatically maps detected faces between source and target

### API Differences
- **V2 API**: Uses face indices array, supports CodeFormer restoration
- **V4.3 API**: Enhanced face detection with improved quality
- **Comparison**: Side-by-side results show quality and detection differences

## Usage

### Running V2 vs V4.3 Comparison
```bash
cd multi-face-testing/batch-tests/scripts
python3 continue_multiface_v43_with_logging.py
```

### Running V2-Only Verification
```bash
cd multi-face-testing/technical-verification/scripts
python3 continue_multiface_v2_only.py
```

### Viewing Results
- **Batch Tests**: Open `batch-tests/review.html` for V2 vs V4.3 comparisons
- **Technical Verification**: Open `technical-verification/review.html` for V2 verification results

## Configuration

### Face Detection Parameters
```python
face_indices = [0, 1, 2, 3, 4]  # Multiple face detection
source_face_indices = [0, 1, 2, 3, 4]
target_face_indices = [0, 1, 2, 3, 4]
fidelity = 0.8  # CodeFormer restoration quality
```

### API Endpoints
- **V2**: Segmind V2 multi-face endpoint
- **V4.3**: Segmind V4.3 enhanced multi-face endpoint

## Log Files
- **V2 vs V4.3**: `logs/multiface_v43_requests_log.csv`
- **V2 Only**: `logs/multiface_v2_only_requests_log.csv`
- All logs include face indices, processing times, and API version details

## Authentication
Uses shared authentication from `../../shared/auth/thortful_auth.py` for consistent API access across all multi-face tests.