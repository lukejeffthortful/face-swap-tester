#!/usr/bin/env python3
"""
Generate multi-face comparison HTML with V2 vs V4.3 results
"""

import os
import json
import glob

def load_metadata(metadata_path):
    """Load metadata from JSON file"""
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def generate_multiface_comparison():
    """Generate multi-face comparison HTML"""
    
    # Setup paths for multi-face testing
    source_images = sorted(glob.glob("test-results/source-images/source_*.jpg"))
    target_images = sorted(glob.glob("test-results/multiface-target-images/target_*.png"))
    results_dir = "test-results/results"  # Both V2 and V4.3 results are here
    
    print(f"🎯 Generating Multi-Face Comparison")
    print(f"Sources: {len(source_images)}, Targets: {len(target_images)}")
    
    # Count results
    v2_results = len(glob.glob(f"{results_dir}/*_v2_result.jpg"))
    v43_results = len(glob.glob(f"{results_dir}/*_v43_result.jpg"))
    total_expected = len(source_images) * len(target_images) * 2  # V2 + V4.3
    
    print(f"V2 results: {v2_results}, V4.3 results: {v43_results}")
    print(f"Total expected: {total_expected}")
    
    # Calculate average times
    v2_total_time = 0.0
    v2_count = 0
    v43_total_time = 0.0
    v43_count = 0
    
    for result_file in glob.glob(f"{results_dir}/*_metadata.json"):
        metadata = load_metadata(result_file)
        if 'generation_time' in metadata and metadata['generation_time']:
            try:
                time_val = float(metadata['generation_time'])
                if '_v2_' in result_file:
                    v2_total_time += time_val
                    v2_count += 1
                elif '_v43_' in result_file:
                    v43_total_time += time_val
                    v43_count += 1
            except:
                pass
    
    avg_v2_time = v2_total_time / v2_count if v2_count > 0 else 0.0
    avg_v43_time = v43_total_time / v43_count if v43_count > 0 else 0.0
    
    # HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Face Swap Comparison (v2 vs v4.3)</title>
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
            background: linear-gradient(135deg, #34c759, #30d158);
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
            max-width: 1800px;
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
            background: linear-gradient(135deg, #34c759 0%, #30d158 100%);
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
            vertical-align: top;
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
            max-width: 200px;
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

        .api-v43 {{
            background: #e8f5e8;
            color: #2e7d32;
        }}

        .face-order-label {{
            font-size: 0.65rem;
            padding: 1px 4px;
            border-radius: 3px;
            margin-top: 1px;
            display: block;
            background: #f0f0f0;
            color: #666;
        }}

        .comparison-row {{
            border-left: 4px solid #34c759;
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
            right: -450px;
            width: 450px;
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
            border-left: 4px solid #34c759;
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

        .multi-face-indicator {{
            background: #e8f5e8;
            color: #2e7d32;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 8px;
        }}

        @media (max-width: 1200px) {{
            .image-cell {{
                width: 33.33%;
            }}
        }}

        @media (max-width: 900px) {{
            .image-cell {{
                width: 50%;
            }}
        }}

        @media (max-width: 768px) {{
            .test-image {{
                width: 100%;
                max-width: 150px;
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
        <h1>🎯 Multi-Face Swap Comparison</h1>
        <div class="test-type-badge">Multi-Face (0,1,2,3)</div>
        <p>Head-to-head comparison: Segmind v2 vs v4.3 (multi-face swapping)</p>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(source_images) * len(target_images)}</div>
                <div class="stat-label">Combinations</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{v2_results}</div>
                <div class="stat-label">v2 Results</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{v43_results}</div>
                <div class="stat-label">v4.3 Results</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_v2_time:.1f}s</div>
                <div class="stat-label">Avg v2 Time</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_v43_time:.1f}s</div>
                <div class="stat-label">Avg v4.3 Time</div>
            </div>
        </div>
    </div>

    <div class="results-container">
"""
    
    # Generate each source group
    for i, source_path in enumerate(source_images, 1):
        source_filename = os.path.basename(source_path)
        source_clean = f"source_{i:02d}"
        
        html_content += f"""
        <div class="source-group">
            <div class="source-header">
                <img class="source-preview" src="{source_path}" alt="{source_clean}">
                {source_clean} - Multi-Face Tests ({len(target_images)} targets)
            </div>
            
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Target Image</th>
                        <th>Source Image</th>
                        <th>v2 Result<span class="multi-face-indicator">All Faces</span></th>
                        <th>v4.3 Result<span class="multi-face-indicator">All Faces</span></th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Generate each target combination
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.splitext(os.path.basename(target_path))[0]
            combo_key = f"{source_clean}_to_{target_name}"
            
            # Check for results
            v2_result_path = f"{results_dir}/{combo_key}_v2_result.jpg"
            v2_metadata_path = f"{results_dir}/{combo_key}_v2_metadata.json"
            
            # V4.3 result (simplified)
            v43_result_path = f"{results_dir}/{combo_key}_v43_result.jpg"
            v43_metadata_path = f"{results_dir}/{combo_key}_v43_metadata.json"
            
            v2_exists = os.path.exists(v2_result_path)
            v43_exists = os.path.exists(v43_result_path)
            
            # Load metadata
            v2_meta = load_metadata(v2_metadata_path) if os.path.exists(v2_metadata_path) else {}
            v2_time = v2_meta.get('generation_time', 'N/A')
            v43_meta = load_metadata(v43_metadata_path) if os.path.exists(v43_metadata_path) else {}
            v43_time = v43_meta.get('generation_time', 'N/A')
            
            html_content += f"""
                    <tr class="comparison-row" onclick="showDetails('multi_{i:02d}_to_{j:02d}')" style="cursor: pointer;">
                        <td class="image-cell">
                            <img class="test-image" src="{target_path}" alt="Target {j:02d}" onclick="openModal('{target_path}'); event.stopPropagation();">
                            <div class="image-label">Target {j:02d}</div>
                        </td>
                        <td class="image-cell">
                            <img class="test-image" src="{source_path}" alt="{source_clean}" onclick="openModal('{source_path}'); event.stopPropagation();">
                            <div class="image-label">{source_clean}</div>
                        </td>
                        <td class="image-cell">
"""
            
            if v2_exists:
                html_content += f"""
                            <img class="test-image" src="{v2_result_path}" alt="v2 Result" onclick="openModal('{v2_result_path}'); event.stopPropagation();">
                            <div class="image-label">v2 Result</div>
                            <div class="api-version api-v2">Multi-Face</div>
"""
            else:
                html_content += """
                            <div class="missing-result">v2 result not available</div>
"""
            
            html_content += """
                        </td>
"""
            
            # Add single V4.3 result
            html_content += """
                        <td class="image-cell">
"""
            
            if v43_exists:
                html_content += f"""
                            <img class="test-image" src="{v43_result_path}" alt="v4.3 Result" onclick="openModal('{v43_result_path}'); event.stopPropagation();">
                            <div class="image-label">v4.3 Result</div>
                            <div class="api-version api-v43">Multi-Face</div>
"""
            else:
                html_content += """
                            <div class="missing-result">v4.3 result not available</div>
"""
            
            html_content += """
                        </td>
"""
            
            html_content += """
                    </tr>
"""
            
            # Add details JavaScript
            details_content = f"""
                <h3>Multi-Face: {source_clean} → Target {j:02d}</h3>
                <div class="detail-section">
                    <h4>API v2 Details (Multi-Face)</h4>
"""
            
            if v2_exists:
                details_content += f"""
                    <div class="metadata"><div class="metadata-item">{v2_time}s</div><div class="metadata-item">CodeFormer</div><div class="metadata-item">Multi-face</div></div>
"""
            else:
                details_content += """
                    <div class="missing-result">No data</div>
"""
            
            details_content += """
                </div>
"""
            
            # Add details for V4.3
            details_content += f"""
                <div class="detail-section">
                    <h4>API v4.3 Details (Multi-Face)</h4>
"""
            
            if v43_exists:
                details_content += f"""
                    <div class="metadata"><div class="metadata-item">{v43_time}s</div><div class="metadata-item">Quality mode</div><div class="metadata-item">Multi-face</div></div>
"""
            else:
                details_content += """
                    <div class="missing-result">No data</div>
"""
            
            details_content += """
                </div>
"""
            
            html_content += f"""
                <script>
                    if (!window.detailsData) window.detailsData = {{}};
                    window.detailsData['multi_{i:02d}_to_{j:02d}'] = `{details_content}`;
                </script>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
"""
    
    # Add footer and JavaScript
    html_content += """
    </div>

    <!-- Details Sidebar -->
    <div id="detailsSidebar" class="details-sidebar">
        <div class="sidebar-header">
            <h3>Multi-Face Details</h3>
            <button class="sidebar-close" onclick="closeSidebar()">&times;</button>
        </div>
        <div id="sidebarContent" class="sidebar-content">
            <p>Click on any row to see detailed multi-face comparison information</p>
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
</html>
"""
    
    # Save the HTML
    output_path = "multiface_comparison.html"
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"\n✅ Multi-face comparison saved to: {output_path}")
    print(f"📊 Current status: V2={v2_results}/{len(source_images) * len(target_images)}, V4.3={v43_results}/{len(source_images) * len(target_images)}")
    
    return output_path

if __name__ == "__main__":
    generate_multiface_comparison()