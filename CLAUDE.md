# Face Swap Tester - Claude Notes

## How to Run Tests

### Single Face Tests (Segmind V4)
- **File:** `continue_v4_with_logging.py`
- **Description:** Most up-to-date Python file for running Segmind V4 single face tests
- **Features:** 
  - Comprehensive CSV logging
  - V4 API integration with latest parameters
  - Batch processing capabilities
  - Error handling and progress tracking
- **Usage:** Run this file to perform single face swap tests using Segmind V4 API

### Multi-Face Tests (Segmind V2 vs V4.3)
- **File:** `continue_multiface_v43_with_logging.py`
- **Description:** Main script for multi-face testing comparing V2 vs V4.3 APIs
- **Features:**
  - Contains both `perform_v2_multiface_swap_with_logging()` and `perform_v43_multiface_swap_with_logging()` functions
  - Comprehensive CSV logging for both APIs
  - Tests multiple faces (indices 0,1,2,3) simultaneously
  - Can run V2-only tests by calling V2 function separately
- **Usage:** Run this file for multi-face V2 vs V4.3 comparisons, or modify to run V2-only

### Multi-Face Tests (Segmind V2 Only)
- **File:** `continue_multiface_v2_only.py`
- **Description:** Re-runs ALL V2 multi-face tests only, ignoring existing results
- **Features:**
  - V2-only multi-face testing with comprehensive CSV logging
  - Uses face indices [0,1,2,3,4] for both source and target
  - CodeFormer face restoration with fidelity 0.8
  - Separate CSV log file: `multiface_v2_only_requests_log.csv`
  - Batch processing with configurable max_tests parameter
- **Usage:** Run this file to re-run all V2 multi-face results from scratch