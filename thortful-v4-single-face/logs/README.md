# Logs Directory

## Main Log File
- **`main_test_results.csv`** - Primary log file for all face swap test results
  - Contains timestamps, source/target info, performance metrics, and results
  - Used by the main test script: `run_thortful_face_swap_tests.py`
  - Format: CSV with headers for easy analysis

## Archive
Historical logs and debug files are organized in subdirectories:

### `archive/testing/`
- Previous test result CSV files
- Backup copies of corrected results
- Legacy test logs

### `archive/debug/`
- Debug session logs and JSON files
- Error logs from debugging sessions
- Timeout analysis data
- Script status logs

## Usage
- The main script automatically writes to `main_test_results.csv`
- Archive files are kept for reference but not actively used
- Log files include comprehensive metadata for analysis and troubleshooting