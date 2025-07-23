#!/usr/bin/env python3
"""
Generate updated single face comparison HTML with current test results
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

def generate_single_face_comparison():
    """Generate updated single face comparison HTML"""
    
    # Setup paths
    source_images = sorted(glob.glob("source-single-face/*.jpg"))
    target_images = sorted(glob.glob("test-results/single-face-target-images/target_*.png"))
    results_dir = "test-results/single-face-results"
    
    print(f"🎯 Generating Single Face Comparison")
    print(f"Sources: {len(source_images)}, Targets: {len(target_images)}")
    
    # Count results
    v2_results = len(glob.glob(f"{results_dir}/*_v2_result.jpg"))
    v4_results = len(glob.glob(f"{results_dir}/*_v4_result.jpg"))
    total_expected = len(source_images) * len(target_images) * 2  # V2 + V4
    
    print(f"V2 results: {v2_results}, V4 results: {v4_results}")
    print(f"Total expected: {total_expected}")
    
    # Calculate average times
    v2_total_time = 0.0
    v2_count = 0
    v4_total_time = 0.0
    v4_count = 0
    
    for result_file in glob.glob(f"{results_dir}/*_metadata.json"):
        metadata = load_metadata(result_file)
        if 'generation_time' in metadata and metadata['generation_time']:
            try:
                time_val = float(metadata['generation_time'])
                if 'v2' in result_file:
                    v2_total_time += time_val
                    v2_count += 1
                elif 'v4' in result_file:
                    v4_total_time += time_val
                    v4_count += 1
            except:
                pass
    
    avg_v2_time = v2_total_time / v2_count if v2_count > 0 else 0.0
    avg_v4_time = v4_total_time / v4_count if v4_count > 0 else 0.0
    
    # HTML template
    html_content = f"""<!DOCTYPE html>
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
                <div class="stat-number">{len(source_images) * len(target_images)}</div>
                <div class="stat-label">Combinations</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{v2_results}</div>
                <div class="stat-label">v2 Results</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{v4_results}</div>
                <div class="stat-label">v4 Results</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_v2_time:.1f}s</div>
                <div class="stat-label">Avg v2 Time</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_v4_time:.1f}s</div>
                <div class="stat-label">Avg v4 Time</div>
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
                {source_clean} - Single Face Tests ({len(target_images)} targets)
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
                <tbody>
"""
        
        # Generate each target combination
        for j, target_path in enumerate(target_images, 1):
            target_name = os.path.splitext(os.path.basename(target_path))[0]
            combo_key = f"{source_clean}_to_{target_name}"
            
            # Check for results
            v2_result_path = f"{results_dir}/{combo_key}_v2_result.jpg"
            v4_result_path = f"{results_dir}/{combo_key}_v4_result.jpg"
            v2_metadata_path = f"{results_dir}/{combo_key}_v2_metadata.json"
            v4_metadata_path = f"{results_dir}/{combo_key}_v4_metadata.json"
            
            v2_exists = os.path.exists(v2_result_path)
            v4_exists = os.path.exists(v4_result_path)
            
            # Load metadata
            v2_metadata = load_metadata(v2_metadata_path) if os.path.exists(v2_metadata_path) else {}
            v4_metadata = load_metadata(v4_metadata_path) if os.path.exists(v4_metadata_path) else {}
            
            v2_time = v2_metadata.get('generation_time', 'N/A')
            v4_time = v4_metadata.get('generation_time', 'N/A')
            
            html_content += f"""
                    <tr class="comparison-row" onclick="showDetails('single_{i:02d}_to_{j:02d}')" style="cursor: pointer;">
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
                            <div class="api-version api-v2">Face Index 0</div>
"""
            else:
                html_content += """
                            <div class="missing-result">v2 result not available</div>
"""
            
            html_content += """
                        </td>
                        <td class="image-cell">
"""
            
            if v4_exists:
                html_content += f"""
                            <img class="test-image" src="{v4_result_path}" alt="v4 Result" onclick="openModal('{v4_result_path}'); event.stopPropagation();">
                            <div class="image-label">v4 Result</div>
                            <div class="api-version api-v4">Face Index 0</div>
"""
            else:
                html_content += """
                            <div class="missing-result">v4 result not available</div>
"""
            
            html_content += """
                        </td>
                    </tr>
"""
            
            # Add details JavaScript
            html_content += f"""
                <script>
                    if (!window.detailsData) window.detailsData = {{}};
                    window.detailsData['single_{i:02d}_to_{j:02d}'] = `
                <h3>Single Face: {source_clean} → Target {j:02d}</h3>
                <div class="detail-section">
                    <h4>API v2 Details (Face Index 0)</h4>
"""
            
            if v2_exists:
                html_content += f"""
                    <div class="metadata"><div class="metadata-item">{v2_time}s</div><div class="metadata-item">CodeFormer</div><div class="metadata-item">Single face</div></div>
"""
            else:
                html_content += """
                    <div class="missing-result">No data</div>
"""
            
            html_content += """
                </div>
                <div class="detail-section">
                    <h4>API v4 Details (Face Index 0)</h4>
"""
            
            if v4_exists:
                html_content += f"""
                    <div class="metadata"><div class="metadata-item">{v4_time}s</div><div class="metadata-item">Quality mode</div><div class="metadata-item">Single face</div></div>
"""
            else:
                html_content += """
                    <div class="missing-result">No data</div>
"""
            
            html_content += """
                </div>
            `;
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
</html>
"""
    
    # Save the HTML
    output_path = "single_face_comparison.html"
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"\n✅ Updated single face comparison saved to: {output_path}")
    print(f"📊 Current status: V2={v2_results}/{len(source_images) * len(target_images)}, V4={v4_results}/{len(source_images) * len(target_images)}")
    
    return output_path

if __name__ == "__main__":
    generate_single_face_comparison()