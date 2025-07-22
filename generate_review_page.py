#!/usr/bin/env python3
"""
Generate HTML review page with actual file listings
"""

import os
import glob
import json
from datetime import datetime

def load_metadata(metadata_path):
    """Load metadata from JSON file"""
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def generate_review_html():
    """Generate HTML review page with actual results"""
    
    # Get all result files
    result_files = glob.glob("test-results/results/*_result.jpg")
    
    if not result_files:
        print("❌ No result files found. Please run face swap tests first.")
        return
    
    # Parse results
    results = []
    for result_file in result_files:
        basename = os.path.basename(result_file).replace('_result.jpg', '')
        parts = basename.split('_to_')
        
        if len(parts) == 2:
            source_id = parts[0].replace('source_', '')
            target_id = parts[1].replace('target_', '')
            
            metadata_file = result_file.replace('_result.jpg', '_metadata.json')
            metadata = load_metadata(metadata_file)
            
            results.append({
                'source_id': source_id,
                'target_id': target_id,
                'result_path': result_file,
                'source_path': f"test-results/source-images/source_{source_id}.jpg",
                'target_path': f"test-results/target-images/target_{target_id}.jpg",
                'metadata': metadata
            })
    
    # Group by source
    grouped_results = {}
    for result in results:
        source_id = result['source_id']
        if source_id not in grouped_results:
            grouped_results[source_id] = []
        grouped_results[source_id].append(result)
    
    # Sort groups and results
    for source_id in grouped_results:
        grouped_results[source_id].sort(key=lambda x: x['target_id'])
    
    # Calculate stats
    total_tests = len(results)
    source_count = len(grouped_results)
    target_count = len(grouped_results[list(grouped_results.keys())[0]]) if grouped_results else 0
    avg_time = sum(float(r['metadata'].get('generation_time', '0')) for r in results) / len(results) if results else 0
    
    print(f"Found {total_tests} results from {source_count} sources × {target_count} targets")
    
    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Swap Results Review</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f7;
            color: #1d1d1f;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        }}

        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5rem;
            font-weight: 600;
        }}

        .header p {{
            margin: 0;
            font-size: 1.1rem;
            color: #86868b;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: #007AFF;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: #86868b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .results-container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .source-group {{
            background: white;
            border-radius: 12px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        }}

        .source-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            font-size: 1.3rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .source-preview {{
            width: 60px;
            height: 45px;
            border-radius: 8px;
            object-fit: cover;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }}

        .results-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .results-table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: center;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }}

        .results-table td {{
            padding: 8px;
            text-align: center;
            border-bottom: 1px solid #f1f3f4;
            vertical-align: top;
        }}

        .results-table tr:hover {{
            background-color: #f8f9fa;
        }}

        .image-cell {{
            position: relative;
            width: 25%;
        }}

        .test-image {{
            width: 100%;
            max-width: 350px;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            cursor: pointer;
            transition: transform 0.2s ease;
        }}

        .test-image:hover {{
            transform: scale(1.02);
        }}

        .image-label {{
            font-size: 0.8rem;
            color: #86868b;
            margin-top: 4px;
            font-weight: 500;
        }}

        .metadata {{
            margin-top: 10px;
            font-size: 0.8rem;
            color: #666;
            line-height: 1.4;
        }}

        .metadata-item {{
            display: inline-block;
            background: #e3f2fd;
            padding: 2px 6px;
            border-radius: 4px;
            margin: 2px;
        }}

        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 100px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}

        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 80%;
            border-radius: 8px;
        }}

        .close {{
            position: absolute;
            top: 50px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}

        .close:hover {{
            color: #bbb;
        }}

        @media (max-width: 768px) {{
            .test-image {{
                width: 100%;
                max-width: 250px;
            }}
            
            .results-table td {{
                padding: 5px;
            }}
            
            .image-cell {{
                width: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎭 Face Swap Results Review</h1>
        <p>Interactive comparison of face swap quality across different combinations</p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_tests}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{source_count}</div>
                <div class="stat-label">Source Images</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{target_count}</div>
                <div class="stat-label">Target Images</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_time:.1f}</div>
                <div class="stat-label">Avg Time (s)</div>
            </div>
        </div>
    </div>

    <div class="results-container">'''
    
    # Generate source groups
    for source_id in sorted(grouped_results.keys()):
        source_results = grouped_results[source_id]
        source_path = f"test-results/source-images/source_{source_id}.jpg"
        
        html_content += f'''
        <div class="source-group">
            <div class="source-header">
                <img class="source-preview" src="{source_path}" alt="Source {source_id}">
                Source Family {source_id} Results ({len(source_results)} combinations)
            </div>
            
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Target Image</th>
                        <th>Source Image</th>
                        <th>Face Swap Result</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>'''
        
        for result in source_results:
            gen_time = result['metadata'].get('generation_time', 'N/A')
            request_id = result['metadata'].get('request_id', 'N/A')
            
            html_content += f'''
                    <tr>
                        <td class="image-cell">
                            <img class="test-image" src="{result['target_path']}" alt="Target {result['target_id']}" onclick="openModal('{result['target_path']}')">
                            <div class="image-label">Target {result['target_id']}</div>
                        </td>
                        <td class="image-cell">
                            <img class="test-image" src="{result['source_path']}" alt="Source {result['source_id']}" onclick="openModal('{result['source_path']}')">
                            <div class="image-label">Source {result['source_id']}</div>
                        </td>
                        <td class="image-cell">
                            <img class="test-image" src="{result['result_path']}" alt="Result {result['source_id']} → {result['target_id']}" onclick="openModal('{result['result_path']}')">
                            <div class="image-label">Face Swap Result</div>
                        </td>
                        <td>
                            <div class="metadata">
                                <div class="metadata-item">4 Faces Swapped</div>
                                <div class="metadata-item">API v2</div>
                                <div class="metadata-item">CodeFormer</div>
                                <div class="metadata-item">{gen_time}s</div>
                            </div>
                        </td>
                    </tr>'''
        
        html_content += '''
                </tbody>
            </table>
        </div>'''
    
    html_content += '''
    </div>

    <!-- Modal for enlarged images -->
    <div id="imageModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <script>
        function openModal(imageSrc) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modal.style.display = 'block';
            modalImg.src = imageSrc;
        }

        // Modal close functionality
        document.querySelector('.close').onclick = function() {
            document.getElementById('imageModal').style.display = 'none';
        }

        window.onclick = function(event) {
            const modal = document.getElementById('imageModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>'''
    
    # Write HTML file
    with open('face_swap_review.html', 'w') as f:
        f.write(html_content)
    
    print(f"✅ Generated review page: face_swap_review.html")
    print(f"📊 Page includes {total_tests} test results")
    print(f"🌐 Open face_swap_review.html in your browser to review results")

if __name__ == "__main__":
    generate_review_html()