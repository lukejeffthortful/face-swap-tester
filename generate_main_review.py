#!/usr/bin/env python3
"""
Generate main review page with navigation between single-face and multi-face results
"""

import os
import glob

def generate_main_review_html():
    """Generate main review page with links to both test types"""
    
    # Check what results are available
    multi_face_v2 = glob.glob("test-results/results/*_v2_result.jpg")
    multi_face_v4 = glob.glob("test-results/results/*_v4_result.jpg")
    single_face_v2 = glob.glob("test-results/single-face-results/*_v2_result.jpg")
    single_face_v4 = glob.glob("test-results/single-face-results/*_v4_result.jpg")
    
    multi_face_available = len(multi_face_v2) > 0 or len(multi_face_v4) > 0
    single_face_available = len(single_face_v2) > 0 or len(single_face_v4) > 0
    
    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Swap API Test Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1d1d1f;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .container {{
            max-width: 800px;
            width: 100%;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}

        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header p {{
            margin: 0;
            font-size: 1.2rem;
            color: #86868b;
        }}

        .test-options {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }}

        .test-card {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .test-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }}

        .test-card.available {{
            cursor: pointer;
        }}

        .test-card.unavailable {{
            opacity: 0.6;
            cursor: not-allowed;
        }}

        .test-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        .test-card.single-face::before {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        }}

        .test-icon {{
            font-size: 4rem;
            margin-bottom: 20px;
        }}

        .test-card h2 {{
            margin: 0 0 10px 0;
            font-size: 1.8rem;
            font-weight: 600;
            color: #1d1d1f;
        }}

        .test-description {{
            font-size: 1rem;
            color: #86868b;
            margin-bottom: 20px;
            line-height: 1.5;
        }}

        .test-stats {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #007AFF;
        }}

        .stat-label {{
            font-size: 0.8rem;
            color: #86868b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .test-button {{
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s ease;
        }}

        .test-button.single-face {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        }}

        .test-button:hover {{
            transform: scale(1.05);
        }}

        .test-button.disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }}

        .status-badge {{
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .status-available {{
            background: #d4edda;
            color: #155724;
        }}

        .status-unavailable {{
            background: #f8d7da;
            color: #721c24;
        }}

        .info-section {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }}

        .info-section h3 {{
            margin: 0 0 15px 0;
            font-size: 1.4rem;
            font-weight: 600;
            color: #1d1d1f;
        }}

        .info-list {{
            list-style: none;
            padding: 0;
        }}

        .info-list li {{
            margin-bottom: 10px;
            padding-left: 20px;
            position: relative;
        }}

        .info-list li::before {{
            content: '•';
            color: #667eea;
            font-weight: 600;
            position: absolute;
            left: 0;
        }}

        @media (max-width: 768px) {{
            .test-options {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .test-card {{
                padding: 20px;
            }}
            
            .test-stats {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚔️ Face Swap API Testing</h1>
            <p>Compare different face swap API versions and configurations</p>
        </div>

        <div class="test-options">
            <div class="test-card {'available' if multi_face_available else 'unavailable'}" {'onclick="window.location.href=\'face_swap_comparison.html\'"' if multi_face_available else ''}>
                <div class="status-badge {'status-available' if multi_face_available else 'status-unavailable'}">
                    {'Available' if multi_face_available else 'No Data'}
                </div>
                <div class="test-icon">👨‍👩‍👧‍👦</div>
                <h2>Multi-Face Testing</h2>
                <div class="test-description">
                    Compare V2 vs V4.3 APIs swapping all 4 faces simultaneously. 
                    Tests face detection order and multi-face capabilities.
                </div>
                <div class="test-stats">
                    <div class="stat">
                        <div class="stat-number">{len(multi_face_v2)}</div>
                        <div class="stat-label">V2 Results</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(multi_face_v4)}</div>
                        <div class="stat-label">V4.3 Results</div>
                    </div>
                </div>
                <a href="{'face_swap_comparison.html' if multi_face_available else '#'}" 
                   class="test-button {'disabled' if not multi_face_available else ''}">
                    {'View Results' if multi_face_available else 'No Data Available'}
                </a>
            </div>

            <div class="test-card single-face {'available' if single_face_available else 'unavailable'}" {'onclick="window.location.href=\'single_face_comparison.html\'"' if single_face_available else ''}>
                <div class="status-badge {'status-available' if single_face_available else 'status-unavailable'}">
                    {'Available' if single_face_available else 'No Data'}
                </div>
                <div class="test-icon">🎯</div>
                <h2>Single Face Testing</h2>
                <div class="test-description">
                    Compare V2 vs V4 APIs swapping only the primary face (index 0). 
                    Head-to-head performance and quality comparison.
                </div>
                <div class="test-stats">
                    <div class="stat">
                        <div class="stat-number">{len(single_face_v2)}</div>
                        <div class="stat-label">V2 Results</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(single_face_v4)}</div>
                        <div class="stat-label">V4 Results</div>
                    </div>
                </div>
                <a href="{'single_face_comparison.html' if single_face_available else '#'}" 
                   class="test-button single-face {'disabled' if not single_face_available else ''}">
                    {'View Results' if single_face_available else 'No Data Available'}
                </a>
            </div>
        </div>

        <div class="info-section">
            <h3>🔬 Testing Information</h3>
            <ul class="info-list">
                <li><strong>Multi-Face:</strong> V2 vs V4.3 - Tests all 4 faces with face detection order matching</li>
                <li><strong>Single Face:</strong> V2 vs V4 - Tests only face index 0 for direct performance comparison</li>
                <li><strong>Images:</strong> Both tests use the same source and target image sets</li>
                <li><strong>Metrics:</strong> Generation time, cost, and quality are tracked for each API</li>
                <li><strong>Results:</strong> Saved separately in different folders for easy comparison</li>
            </ul>
        </div>
    </div>
</body>
</html>'''
    
    # Write HTML file
    with open('face_swap_test_results.html', 'w') as f:
        f.write(html_content)
    
    print(f"✅ Generated main review page: face_swap_test_results.html")
    print(f"📊 Multi-face results: {'Available' if multi_face_available else 'Not available'}")
    print(f"🎯 Single-face results: {'Available' if single_face_available else 'Not available'}")
    print(f"🌐 Open face_swap_test_results.html to navigate between test types")

if __name__ == "__main__":
    generate_main_review_html()