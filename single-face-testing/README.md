# Single Face Testing Suite

## Overview
This directory contains all single face swap testing functionality, organized into two main categories:

- **Batch Tests**: Large-scale testing with diverse faces and comprehensive logging
- **Technical Verification**: Quick verification tests for API functionality and system health

## Directory Structure

```
single-face-testing/
├── batch-tests/
│   ├── logs/                  # CSV test result logs
│   ├── results/               # Generated face swap images
│   ├── scripts/               # Test execution scripts
│   ├── source-images/         # Source face images for testing
│   ├── target-images/         # Target card templates
│   └── review.html           # Web interface for viewing results
└── technical-verification/
    ├── logs/                  # CSV verification logs  
    ├── results/               # Verification result images
    ├── scripts/               # Verification scripts
    ├── source-images/         # Test source images
    ├── target-images/         # Test target images
    └── review.html           # Web interface for viewing results
```

## Key Scripts

### Batch Tests
- **`thortful_test_single_face.py`**: Main Thortful V4 API batch testing script
- **`run_batch_tests.py`**: Automated batch test runner with progress tracking

### Technical Verification  
- **`verify_single_test.py`**: Quick API verification test
- **`continue_v4_with_logging.py`**: Legacy V4 testing with comprehensive logging
- **`batch_test_single_face.py`**: Legacy batch testing script

## Usage

### Running Batch Tests
```bash
cd single-face-testing/batch-tests/scripts
python3 thortful_test_single_face.py
```

### Running Technical Verification
```bash
cd single-face-testing/technical-verification/scripts  
python3 verify_single_test.py
```

### Viewing Results
Open the respective `review.html` files in a web browser to view interactive results with performance metrics and image comparisons.

## Authentication
All scripts use shared authentication from `../../shared/auth/thortful_auth.py`. Ensure tokens are refreshed before running tests.

## Log Files
- Results are logged in CSV format in the respective `logs/` directories
- Images are saved in the respective `results/` directories
- All logs include timestamps, performance metrics, and error details