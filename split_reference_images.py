#!/usr/bin/env python3
"""
Split the reference image into separate target and source images
"""

from PIL import Image
import os
import json
from datetime import datetime

def split_reference_image():
    """Split the 2-column reference image into individual target and source files"""
    
    # Load the reference image
    ref_path = "reference_files/sourc_and_targets_v2_testing.png"
    if not os.path.exists(ref_path):
        print(f"❌ Reference image not found: {ref_path}")
        return
    
    print("🖼️  Loading reference image...")
    img = Image.open(ref_path)
    width, height = img.size
    print(f"   Image size: {width} x {height}")
    
    # Create output directories
    target_dir = "reference_files/extracted-targets"
    source_dir = "reference_files/extracted-sources"
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(source_dir, exist_ok=True)
    
    # The image has a header row with "Target" and "Source" labels
    # Skip the header and calculate individual image dimensions
    header_height = 50  # Approximate header height
    
    # Calculate column width (2 columns)
    col_width = width // 2
    
    # Count the number of rows by looking at the remaining height
    usable_height = height - header_height
    
    # Estimate row height by visual inspection of the image
    # From the image, it looks like there are about 23-24 pairs
    num_pairs = 24  # Estimate
    row_height = usable_height // num_pairs
    
    print(f"   Estimated {num_pairs} image pairs")
    print(f"   Column width: {col_width}, Row height: {row_height}")
    
    extracted_count = 0
    metadata = {
        "extraction_date": datetime.now().isoformat(),
        "source_image": ref_path,
        "extraction_method": "grid_based",
        "pairs": []
    }
    
    # Extract each pair
    for i in range(num_pairs):
        y_start = header_height + (i * row_height)
        y_end = y_start + row_height
        
        # Skip if we're beyond the image bounds
        if y_end > height:
            break
        
        try:
            # Extract target image (left column)
            target_box = (0, y_start, col_width, y_end)
            target_img = img.crop(target_box)
            target_filename = f"target_{i+1:02d}.png"
            target_path = os.path.join(target_dir, target_filename)
            target_img.save(target_path)
            
            # Extract source image (right column)  
            source_box = (col_width, y_start, width, y_end)
            source_img = img.crop(source_box)
            source_filename = f"source_{i+1:02d}.png"
            source_path = os.path.join(source_dir, source_filename)
            source_img.save(source_path)
            
            print(f"   ✅ Extracted pair {i+1:2d}: {target_filename} & {source_filename}")
            
            # Add to metadata
            metadata["pairs"].append({
                "pair_number": i + 1,
                "target_file": target_filename,
                "source_file": source_filename,
                "coordinates": {
                    "target_box": target_box,
                    "source_box": source_box
                }
            })
            
            extracted_count += 1
            
        except Exception as e:
            print(f"   ❌ Error extracting pair {i+1}: {e}")
            continue
    
    # Save extraction metadata
    metadata_path = "reference_files/extraction_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Summary
    print(f"\n🎉 Extraction Complete!")
    print(f"   ✅ Extracted {extracted_count} image pairs")
    print(f"   📁 Targets saved to: {target_dir}")
    print(f"   📁 Sources saved to: {source_dir}")
    print(f"   📝 Metadata saved to: {metadata_path}")
    
    # Verify extraction
    target_files = len([f for f in os.listdir(target_dir) if f.endswith('.png')])
    source_files = len([f for f in os.listdir(source_dir) if f.endswith('.png')])
    
    print(f"\n📊 Verification:")
    print(f"   Target files: {target_files}")
    print(f"   Source files: {source_files}")
    
    if target_files == source_files == extracted_count:
        print(f"   ✅ All extractions successful!")
        print(f"\n🚀 Ready for V2 batch testing!")
        print(f"   Next: Run batch V2 tests on these {extracted_count} pairs")
    else:
        print(f"   ⚠️  File count mismatch detected")
    
    return extracted_count

def preview_extraction():
    """Show a preview of what will be extracted"""
    ref_path = "reference_files/sourc_and_targets_v2_testing.png"
    if not os.path.exists(ref_path):
        print(f"❌ Reference image not found: {ref_path}")
        return
    
    img = Image.open(ref_path)
    width, height = img.size
    
    print(f"🔍 Preview of extraction:")
    print(f"   Image dimensions: {width} x {height}")
    print(f"   Will split into 2 columns of ~{width//2} pixels each")
    print(f"   Estimated ~24 image pairs to extract")
    print(f"   Target images: Left column")
    print(f"   Source images: Right column")

if __name__ == "__main__":
    print("🔧 Reference Image Splitter")
    print("=" * 40)
    
    # Show preview first
    preview_extraction()
    
    print("\nProceeding with extraction...")
    split_reference_image()