"""
Common utilities for face swap testing suite
"""
import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional

def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def save_result_metadata(result_path: str, metadata: Dict[str, Any]) -> None:
    """Save metadata for a test result"""
    metadata_path = result_path.replace('.jpg', '_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def load_result_metadata(result_path: str) -> Optional[Dict[str, Any]]:
    """Load metadata for a test result"""
    metadata_path = result_path.replace('.jpg', '_metadata.json')
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return None

def log_test_result(log_file: str, test_data: Dict[str, Any]) -> None:
    """Log a test result to CSV file"""
    ensure_directory_exists(os.path.dirname(log_file))
    
    file_exists = os.path.exists(log_file)
    
    with open(log_file, 'a', newline='') as csvfile:
        if test_data:
            fieldnames = test_data.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(test_data)

def generate_timestamp() -> str:
    """Generate a timestamp string for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_project_root() -> str:
    """Get the project root directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_shared_auth_path() -> str:
    """Get path to shared authentication file"""
    return os.path.join(get_project_root(), 'shared', 'auth', 'thortful_auth.json')

def format_test_duration(duration_seconds: float) -> str:
    """Format test duration in a human readable way"""
    if duration_seconds < 60:
        return f"{duration_seconds:.1f}s"
    elif duration_seconds < 3600:
        minutes = duration_seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = duration_seconds / 3600
        return f"{hours:.1f}h"

def parse_result_filename(filename: str) -> Dict[str, str]:
    """Parse information from result filename"""
    parts = filename.replace('.jpg', '').split('_')
    
    result = {}
    if 'to' in parts:
        to_index = parts.index('to')
        result['source'] = '_'.join(parts[:to_index])
        result['target'] = '_'.join(parts[to_index+1:])
    
    if 'v2' in filename:
        result['api_version'] = 'v2'
    elif 'v4' in filename:
        result['api_version'] = 'v4'
    elif 'v43' in filename:
        result['api_version'] = 'v43'
    
    return result