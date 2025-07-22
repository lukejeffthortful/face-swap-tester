#!/usr/bin/env python3
"""
Download top 10 most swapped Thortful face swap cards as target images
"""

import requests
import os
import json
import csv
from datetime import datetime

def parse_csv_file():
    """Parse the CSV file to get product IDs and swap counts"""
    csv_file = "reference_files/Data Table - Most Completed Swaps of a Face Swap Card.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return []
    
    cards = []
    with open(csv_file, 'r') as f:
        lines = f.readlines()
        
        # Skip header rows and find data
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or 'product_id' in line or 'Most Completed Swaps' in line:
                continue
                
            # Parse lines that look like: "	67816ae75990fc276575cd07","	587.0"
            if line.startswith('"') and '","' in line:
                try:
                    # Split by ","
                    parts = line.split('","')
                    if len(parts) >= 2:
                        # Extract product ID (remove leading quote and tab)
                        product_id = parts[0].strip('"').strip('\t').strip()
                        # Extract swap count (remove trailing quote and tab)
                        swap_count_str = parts[1].strip('"').strip('\t').strip()
                        
                        swap_count = float(swap_count_str)
                        
                        if product_id and len(product_id) == 24:  # MongoDB ObjectId length
                            cards.append({
                                'product_id': product_id,
                                'swap_count': int(swap_count),
                                'rank': len(cards) + 1
                            })
                            print(f"  Parsed: {product_id} -> {int(swap_count)} swaps")
                            
                except (ValueError, IndexError) as e:
                    print(f"  Skipping line {i}: {e}")
                    continue
    
    return sorted(cards, key=lambda x: x['swap_count'], reverse=True)

def download_card_image(product_id, output_path):
    """Download a Thortful card image using the product ID"""
    # URL format: https://images.thortful.com/cdn-cgi/image/width=600,format=auto,quality=90/card/{id}/{id}_medium.jpg?version=1
    url = f"https://images.thortful.com/cdn-cgi/image/width=600,format=auto,quality=90/card/{product_id}/{product_id}_medium.jpg?version=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"  Downloading: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if we got an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"    ❌ Not an image (content-type: {content_type})")
            return False
        
        # Save the image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"    ✅ Saved: {output_path} ({len(response.content)} bytes)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Download failed: {e}")
        return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def download_top_targets():
    """Download top 10 most swapped cards as target images"""
    print("🎯 Downloading Top 10 Thortful Face Swap Targets")
    print("=" * 50)
    
    # Parse CSV file
    cards = parse_csv_file()
    if not cards:
        print("❌ No cards found in CSV file")
        return
    
    print(f"Found {len(cards)} cards in CSV file")
    print(f"Top card has {cards[0]['swap_count']} swaps")
    
    # Create target images directory
    target_dir = "test-results/target-images"
    os.makedirs(target_dir, exist_ok=True)
    
    # Download top 10
    top_10 = cards[:10]
    successful_downloads = 0
    
    print(f"\nDownloading top 10 cards:")
    
    for i, card in enumerate(top_10, 1):
        product_id = card['product_id']
        swap_count = card['swap_count']
        
        print(f"\n[{i}/10] Rank {card['rank']}: {product_id} ({swap_count} swaps)")
        
        # Create filename
        filename = f"target_{i:02d}.png"
        output_path = os.path.join(target_dir, filename)
        
        # Download image
        success = download_card_image(product_id, output_path)
        if success:
            successful_downloads += 1
            
            # Save metadata
            metadata = {
                "source": "thortful",
                "product_id": product_id,
                "rank": card['rank'],
                "swap_count": swap_count,
                "download_date": datetime.now().isoformat(),
                "filename": filename,
                "url": f"https://images.thortful.com/cdn-cgi/image/width=600,format=auto,quality=90/card/{product_id}/{product_id}_medium.jpg?version=1"
            }
            
            metadata_path = output_path.replace('.png', '_generation_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # Small delay between downloads
        import time
        time.sleep(1)
    
    # Summary
    print(f"\n🎉 Download Complete!")
    print(f"✅ Successfully downloaded: {successful_downloads}/10 images")
    print(f"📁 Saved to: {target_dir}")
    print(f"📊 Images are numbered target_01.png to target_10.png")
    print(f"📝 Metadata files saved alongside each image")
    
    if successful_downloads > 0:
        print(f"\n🚀 Ready for face swap testing!")
        print(f"   - Run batch_test_single_face.py for V2 vs V4 single face comparison")
        print(f"   - Run batch_test_face_swap_comparison.py for V2 vs V4.3 multi-face comparison")
    
    # Show top 10 list
    print(f"\n📋 Top 10 Most Swapped Cards:")
    for i, card in enumerate(top_10, 1):
        status = "✅" if os.path.exists(os.path.join(target_dir, f"target_{i:02d}.png")) else "❌"
        print(f"   {i:2d}. {status} {card['product_id']} ({card['swap_count']} swaps)")

def main():
    """Main function"""
    download_top_targets()

if __name__ == "__main__":
    main()