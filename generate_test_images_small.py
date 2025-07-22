#!/usr/bin/env python3
"""
Generate small test set: 3 source + 3 target images for testing
"""

import requests
import base64
import os
import json
from datetime import datetime
import time

def load_api_key():
    """Load API key from .env file or environment variable"""
    api_key = os.getenv('REACT_APP_SEGMIND_API_KEY')
    if api_key:
        return api_key
    
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('REACT_APP_SEGMIND_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return None

def generate_image(prompt, filename):
    """Generate image using SDXL API"""
    API_KEY = load_api_key()
    API_URL = "https://api.segmind.com/v1/sdxl1.0-txt2img"
    
    data = {
        "prompt": prompt,
        "negative_prompt": "blurry, low quality, distorted faces, cartoon, anime, drawing, sketch, watermark, text, logo",
        "width": 1024,
        "height": 768,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "seed": -1,  # Random seed
        "base64": False
    }
    
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Generating: {filename}")
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()
        
        # Save image
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Saved: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating {filename}: {e}")
        return False

def generate_source_images():
    """Generate 3 diverse family source images"""
    print("Generating 3 source family images...")
    
    source_prompts = [
        "Photo-realistic portrait of 4 African American family members, parents and two children, professional photography, clear faces, neutral background, family photo style, good lighting, facing camera, smiling expressions",
        
        "Photo-realistic portrait of 4 Asian family members, mother father and two teenagers, high quality professional photography, clear faces, good lighting, neutral background, family photo style, facing camera",
        
        "Photo-realistic portrait of 4 Caucasian family members, parents and children, professional studio photography, clear faces, neutral background, family portrait style, good lighting, facing camera"
    ]
    
    successful = 0
    for i, prompt in enumerate(source_prompts, 1):
        filename = f"test-results/source-images/source_{i:02d}.jpg"
        if generate_image(prompt, filename):
            successful += 1
        time.sleep(2)  # Rate limiting
    
    print(f"Source images: {successful}/3 generated successfully")
    return successful

def generate_target_images():
    """Generate 3 Christmas card target images"""
    print("\nGenerating 3 Christmas card target images...")
    
    target_prompts = [
        "Photo-realistic Christmas greeting card featuring 4 people smiling at camera, traditional Victorian Christmas style, professional photography, high quality, festive atmosphere, holiday decorations, Christmas tree, warm lighting, joyful expressions, family portrait style, text overlay 'Merry Christmas and Happy New Year!', Christmas ornaments, holiday setting",
        
        "Photo-realistic Christmas greeting card featuring 4 people smiling at camera, modern minimalist Christmas style, professional photography, high quality, festive atmosphere, holiday decorations, Christmas tree, warm lighting, joyful expressions, family portrait style, text overlay 'Season\\'s Greetings from our family to yours', Christmas ornaments, holiday setting",
        
        "Photo-realistic Christmas greeting card featuring 4 people smiling at camera, rustic winter wonderland style, professional photography, high quality, festive atmosphere, holiday decorations, Christmas tree, warm lighting, joyful expressions, family portrait style, text overlay 'Warmest wishes for a magical Christmas', Christmas ornaments, holiday setting"
    ]
    
    successful = 0
    for i, prompt in enumerate(target_prompts, 1):
        filename = f"test-results/target-images/target_{i:02d}.jpg"
        if generate_image(prompt, filename):
            successful += 1
        time.sleep(2)  # Rate limiting
    
    print(f"Target images: {successful}/3 generated successfully")
    return successful

def main():
    """Generate test images"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    print("Starting small batch image generation...")
    print("This will generate 6 images total (3 source + 3 target)")
    print("Estimated time: ~1 minute with rate limiting\n")
    
    # Generate source images
    source_success = generate_source_images()
    
    # Generate target images  
    target_success = generate_target_images()
    
    print(f"\n🎉 Generation complete!")
    print(f"Source images: {source_success}/3")
    print(f"Target images: {target_success}/3")
    print(f"Total: {source_success + target_success}/6 images generated")
    
    if source_success == 3 and target_success == 3:
        print("\n✅ All images generated successfully!")
        print("Ready to run batch face swap tests (3×3 = 9 combinations).")
    else:
        print("\n⚠️ Some images failed to generate. Check the logs above.")

if __name__ == "__main__":
    main()