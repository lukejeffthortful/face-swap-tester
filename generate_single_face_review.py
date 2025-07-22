#!/usr/bin/env python3
"""
Generate HTML review page comparing V2 vs V4 single face swap results
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

def generate_single_face_review_html():
    """Generate HTML review page comparing V2 vs V4 single face results"""
    
    # Get all result files for both versions
    v2_files = glob.glob("test-results/single-face-results/*_v2_result.jpg")
    v4_files = glob.glob("test-results/single-face-results/*_v4_result.jpg")
    
    if not v2_files and not v4_files:
        print("❌ No single face result files found. Please run batch_test_single_face.py first.")
        return
    
    # Parse and organize results
    combinations = {}
    
    # Process v2 results
    for result_file in v2_files:
        basename = os.path.basename(result_file).replace('_v2_result.jpg', '')
        parts = basename.split('_to_')
        
        if len(parts) == 2:
            source_part = parts[0]  # e.g., "source_01"
            target_part = parts[1]  # e.g., "target_01"
            
            # Extract IDs
            source_id = source_part.replace('source_', '') if 'source_' in source_part else source_part
            target_id = target_part.replace('target_', '') if 'target_' in target_part else target_part
            
            combo_key = f"{source_id}_to_{target_id}"
            
            if combo_key not in combinations:
                # Find the original source image
                source_images = glob.glob("source-single-face/*.jpg")
                source_path = ""
                if len(source_images) >= int(source_id):
                    source_path = sorted(source_images)[int(source_id) - 1]
                
                # Target path
                target_path = f"test-results/target-images/{target_part}.png"
                
                combinations[combo_key] = {
                    'source_id': source_id,
                    'target_id': target_id,
                    'source_path': source_path,
                    'target_path': target_path
                }
            
            metadata_file = result_file.replace('_result.jpg', '_metadata.json')
            metadata = load_metadata(metadata_file)
            
            combinations[combo_key]['v2'] = {
                'result_path': result_file,
                'metadata': metadata
            }
    
    # Process v4 results
    for result_file in v4_files:
        basename = os.path.basename(result_file).replace('_v4_result.jpg', '')
        parts = basename.split('_to_')
        
        if len(parts) == 2:
            source_part = parts[0]  # e.g., "source_01"
            target_part = parts[1]  # e.g., "target_01"
            
            # Extract IDs
            source_id = source_part.replace('source_', '') if 'source_' in source_part else source_part
            target_id = target_part.replace('target_', '') if 'target_' in target_part else target_part
            
            combo_key = f"{source_id}_to_{target_id}"
            
            if combo_key not in combinations:
                # Find the original source image
                source_images = glob.glob("source-single-face/*.jpg")
                source_path = ""
                if len(source_images) >= int(source_id):
                    source_path = sorted(source_images)[int(source_id) - 1]
                
                # Target path
                target_path = f"test-results/target-images/{target_part}.png"
                
                combinations[combo_key] = {
                    'source_id': source_id,
                    'target_id': target_id,
                    'source_path': source_path,
                    'target_path': target_path
                }
            
            metadata_file = result_file.replace('_result.jpg', '_metadata.json')
            metadata = load_metadata(metadata_file)
            
            combinations[combo_key]['v4'] = {
                'result_path': result_file,
                'metadata': metadata
            }
    
    # Group by source
    grouped_results = {}
    for combo_key, combo_data in combinations.items():
        source_id = combo_data['source_id']
        if source_id not in grouped_results:
            grouped_results[source_id] = []
        grouped_results[source_id].append(combo_data)
    
    # Sort groups and results
    for source_id in grouped_results:
        grouped_results[source_id].sort(key=lambda x: x['target_id'])
    
    # Calculate stats
    total_combinations = len(combinations)
    v2_count = len([c for c in combinations.values() if 'v2' in c])
    v4_count = len([c for c in combinations.values() if 'v4' in c])
    source_count = len(grouped_results)
    
    avg_time_v2 = 0
    avg_time_v4 = 0
    
    if v2_count > 0:
        v2_times = [float(c['v2']['metadata'].get('generation_time', '0')) for c in combinations.values() if 'v2' in c and c['v2']['metadata'].get('generation_time', '0') != 'N/A']
        avg_time_v2 = sum(v2_times) / len(v2_times) if v2_times else 0
    
    if v4_count > 0:
        v4_times = [float(c['v4']['metadata'].get('generation_time', '0')) for c in combinations.values() if 'v4' in c and c['v4']['metadata'].get('generation_time', '0') != 'N/A']
        avg_time_v4 = sum(v4_times) / len(v4_times) if v4_times else 0
    
    print(f"Found {total_combinations} combinations")
    print(f"v2 results: {v2_count}, v4 results: {v4_count}")
    
    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Single Face Swap Comparison (v2 vs v4)</title>
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

        .test-type-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 10px;
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
            max-width: 1600px;
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
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
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
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            font-size: 0.9rem;
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
            max-width: 280px;
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
            font-size: 0.75rem;
            color: #86868b;
            margin-top: 4px;
            font-weight: 500;
        }}

        .api-version {{
            font-size: 0.7rem;
            padding: 2px 6px;
            border-radius: 4px;
            margin-top: 2px;
            display: inline-block;
            font-weight: 600;
        }}

        .api-v2 {{
            background: #e3f2fd;
            color: #1976d2;
        }}

        .api-v4 {{
            background: #fff3e0;
            color: #f57c00;
        }}

        .comparison-row {{
            border-left: 4px solid #ff6b6b;
        }}

        .metadata {{
            margin-top: 8px;
            font-size: 0.75rem;
            color: #666;
            line-height: 1.3;
        }}

        .metadata-item {{
            display: inline-block;
            background: #f0f0f0;
            padding: 1px 4px;
            border-radius: 3px;
            margin: 1px;
            font-size: 0.7rem;
        }}

        .missing-result {{
            color: #d32f2f;
            font-style: italic;
            padding: 20px;
            background: #ffebee;
            border-radius: 6px;
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

        .details-sidebar {{
            position: fixed;
            top: 0;
            right: -400px;
            width: 400px;
            height: 100vh;
            background: white;
            box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
            z-index: 1001;
            transition: right 0.3s ease;
            overflow-y: auto;
        }}

        .details-sidebar.open {{
            right: 0;
        }}

        .sidebar-header {{
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .sidebar-header h3 {{
            margin: 0;
            font-size: 1.2rem;
            color: #495057;
        }}

        .sidebar-close {{
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6c757d;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }}

        .sidebar-close:hover {{
            background: #e9ecef;
            color: #495057;
        }}

        .sidebar-content {{
            padding: 20px;
        }}

        .comparison-row:hover {{
            background-color: #f8f9fa;
            border-left: 4px solid #ff6b6b;
        }}

        .detail-section {{
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            background: #f8f9fa;
        }}

        .detail-section h4 {{
            margin: 0 0 10px 0;
            font-size: 1rem;
            color: #495057;
            font-weight: 600;
        }}

        .single-face-indicator {{
            background: #fff3e0;
            color: #f57c00;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 8px;
        }}

        @media (max-width: 1200px) {{
            .image-cell {{
                width: 50%;
            }}
        }}

        @media (max-width: 768px) {{
            .test-image {{
                width: 100%;
                max-width: 200px;
            }}
            
            .results-table td {{
                padding: 4px;
            }}
            
            .image-cell {{
                width: auto;
            }}
            
            .results-table th {{
                padding: 8px 4px;
                font-size: 0.8rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Single Face Swap Comparison</h1>
        <div class="test-type-badge">Face Index 0 Only</div>
        <p>Head-to-head comparison: Segmind v2 vs v4 (single face swapping)</p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_combinations}</div>
                <div class="stat-label">Combinations</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{v2_count}</div>
                <div class="stat-label">v2 Results</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{v4_count}</div>
                <div class="stat-label">v4 Results</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_time_v2:.1f}s</div>
                <div class="stat-label">Avg v2 Time</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_time_v4:.1f}s</div>
                <div class="stat-label">Avg v4 Time</div>
            </div>
        </div>
    </div>

    <div class="results-container">'''
    
    # Generate source groups
    for source_id in sorted(grouped_results.keys()):
        source_results = grouped_results[source_id]
        # Get the actual source image path from the first result
        source_path = source_results[0]['source_path'] if source_results else ""
        
        html_content += f'''
        <div class="source-group">
            <div class="source-header">
                <img class="source-preview" src="{source_path}" alt="Source {source_id}">
                Source Image {source_id} - Single Face Tests ({len(source_results)} targets)
            </div>
            
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Target Image</th>
                        <th>Source Image</th>
                        <th>v2 Result<span class="single-face-indicator">Face 0</span></th>
                        <th>v4 Result<span class="single-face-indicator">Face 0</span></th>
                    </tr>
                </thead>
                <tbody>'''
        
        for result in source_results:
            combo_id = f"single_{result['source_id']}_to_{result['target_id']}"
            v2_time = result['v2']['metadata'].get('generation_time', 'N/A') if 'v2' in result else 'N/A'
            v4_time = result['v4']['metadata'].get('generation_time', 'N/A') if 'v4' in result else 'N/A'
            
            html_content += f'''
                    <tr class="comparison-row" onclick="showDetails('{combo_id}')" style="cursor: pointer;">
                        <td class="image-cell">
                            <img class="test-image" src="{result['target_path']}" alt="Target {result['target_id']}" onclick="openModal('{result['target_path']}'); event.stopPropagation();">
                            <div class="image-label">Target {result['target_id']}</div>
                        </td>
                        <td class="image-cell">
                            <img class="test-image" src="{result['source_path']}" alt="Source {result['source_id']}" onclick="openModal('{result['source_path']}'); event.stopPropagation();">
                            <div class="image-label">Source {result['source_id']}</div>
                        </td>'''
            
            # v2 result
            if 'v2' in result:
                html_content += f'''
                        <td class="image-cell">
                            <img class="test-image" src="{result['v2']['result_path']}" alt="v2 Result" onclick="openModal('{result['v2']['result_path']}'); event.stopPropagation();">
                            <div class="image-label">v2 Result</div>
                            <div class="api-version api-v2">Face Index 0</div>
                        </td>'''
            else:
                html_content += '''
                        <td class="image-cell">
                            <div class="missing-result">v2 result not available</div>
                        </td>'''
            
            # v4 result
            if 'v4' in result:
                html_content += f'''
                        <td class="image-cell">
                            <img class="test-image" src="{result['v4']['result_path']}" alt="v4 Result" onclick="openModal('{result['v4']['result_path']}'); event.stopPropagation();">
                            <div class="image-label">v4 Result</div>
                            <div class="api-version api-v4">Face Index 0</div>
                        </td>'''
            else:
                html_content += '''
                        <td class="image-cell">
                            <div class="missing-result">v4 result not available</div>
                        </td>'''
            
            html_content += '''
                    </tr>'''
            
            # Store details data for sidebar
            details_data = f'''
                <h3>Single Face: Source {result['source_id']} → Target {result['target_id']}</h3>
                <div class="detail-section">
                    <h4>API v2 Details (Face Index 0)</h4>
                    {'<div class="metadata"><div class="metadata-item">' + str(v2_time) + 's</div><div class="metadata-item">CodeFormer</div><div class="metadata-item">Single face</div></div>' if 'v2' in result else '<div class="missing-result">No data</div>'}
                </div>
                <div class="detail-section">
                    <h4>API v4 Details (Face Index 0)</h4>
                    {'<div class="metadata"><div class="metadata-item">' + str(v4_time) + 's</div><div class="metadata-item">Quality mode</div><div class="metadata-item">Single face</div><div class="metadata-item">big_to_small</div></div>' if 'v4' in result else '<div class="missing-result">No data</div>'}
                </div>
            '''
            
            # Add to details storage for sidebar
            html_content += f'''
                <script>
                    if (!window.detailsData) window.detailsData = {{}};
                    window.detailsData['{combo_id}'] = `{details_data}`;
                </script>'''
        
        html_content += '''
                </tbody>
            </table>
        </div>'''
    
    html_content += '''
    </div>

    <!-- Details Sidebar -->
    <div id="detailsSidebar" class="details-sidebar">
        <div class="sidebar-header">
            <h3>Single Face Details</h3>
            <button class="sidebar-close" onclick="closeSidebar()">&times;</button>
        </div>
        <div id="sidebarContent" class="sidebar-content">
            <p>Click on any row to see detailed single face comparison information</p>
        </div>
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

        function showDetails(comboId) {
            const sidebar = document.getElementById('detailsSidebar');
            const content = document.getElementById('sidebarContent');
            
            if (window.detailsData && window.detailsData[comboId]) {
                content.innerHTML = window.detailsData[comboId];
                sidebar.classList.add('open');
            }
        }

        function closeSidebar() {
            const sidebar = document.getElementById('detailsSidebar');
            sidebar.classList.remove('open');
        }

        // Modal close functionality
        document.querySelector('.close').onclick = function() {
            document.getElementById('imageModal').style.display = 'none';
        }

        window.onclick = function(event) {
            const modal = document.getElementById('imageModal');
            const sidebar = document.getElementById('detailsSidebar');
            
            if (event.target === modal) {
                modal.style.display = 'none';
            }
            
            // Close sidebar when clicking outside
            if (event.target === sidebar) {
                closeSidebar();
            }
        }
    </script>
</body>
</html>'''
    
    # Write HTML file
    with open('single_face_comparison.html', 'w') as f:
        f.write(html_content)
    
    print(f"✅ Generated single face comparison page: single_face_comparison.html")
    print(f"📊 Page includes {total_combinations} combination comparisons")
    print(f"🌐 Open single_face_comparison.html in your browser to compare v2 vs v4 single face results")

if __name__ == "__main__":
    generate_single_face_review_html()