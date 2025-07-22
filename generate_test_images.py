#!/usr/bin/env python3
"""
Generate diverse test images for face swap testing
- 20 source images: diverse families with 4 people each
- 20 target images: Christmas cards with 4 people each
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
    """Generate 20 diverse family source images"""
    print("Generating source family images...")
    
    source_prompts = [
        # Different ethnicities and family compositions
        "Photo-realistic portrait of 4 African American family members, parents and two children, professional photography, clear faces, neutral background, family photo style, good lighting, facing camera, smiling expressions",
        
        "Photo-realistic portrait of 4 Asian family members, mother father and two teenagers, high quality professional photography, clear faces, good lighting, neutral background, family photo style, facing camera",
        
        "Photo-realistic portrait of 4 Hispanic Latino family members, diverse ages, professional family photography, clear faces, neutral white background, good lighting, facing camera, happy expressions",
        
        "Photo-realistic portrait of 4 Caucasian family members, parents and children, professional studio photography, clear faces, neutral background, family portrait style, good lighting, facing camera",
        
        "Photo-realistic portrait of 4 Middle Eastern family members, traditional family photo, professional photography, clear faces, neutral background, good lighting, facing camera, warm expressions",
        
        "Photo-realistic portrait of 4 Indian family members, parents and two children, professional photography, clear faces, neutral background, family photo style, good lighting, facing camera",
        
        "Photo-realistic portrait of 4 mixed race family members, diverse ethnic background, professional photography, clear faces, neutral background, family portrait, good lighting, facing camera",
        
        "Photo-realistic portrait of 4 elderly and young family members, grandparents and grandchildren, professional photography, clear faces, neutral background, multigenerational family photo",
        
        "Photo-realistic portrait of 4 Native American family members, traditional family portrait, professional photography, clear faces, neutral background, good lighting, facing camera",
        
        "Photo-realistic portrait of 4 Pacific Islander family members, professional family photography, clear faces, neutral background, good lighting, facing camera, happy expressions",
        
        "Photo-realistic portrait of 4 European family members, professional studio photography, clear faces, neutral white background, good lighting, facing camera, family portrait style",
        
        "Photo-realistic portrait of 4 African family members, traditional family photo, professional photography, clear faces, neutral background, good lighting, facing camera",
        
        "Photo-realistic portrait of 4 Southeast Asian family members, parents and teenagers, professional photography, clear faces, neutral background, family photo style, good lighting",
        
        "Photo-realistic portrait of 4 Brazilian family members, diverse ethnic mix, professional photography, clear faces, neutral background, good lighting, facing camera, warm smiles",
        
        "Photo-realistic portrait of 4 Nordic Scandinavian family members, professional family photography, clear faces, neutral background, good lighting, facing camera, family portrait",
        
        "Photo-realistic portrait of 4 Mediterranean family members, professional photography, clear faces, neutral background, good lighting, facing camera, happy family expressions",
        
        "Photo-realistic portrait of 4 Caribbean family members, diverse skin tones, professional photography, clear faces, neutral background, good lighting, facing camera",
        
        "Photo-realistic portrait of 4 Eastern European family members, professional studio photography, clear faces, neutral background, good lighting, facing camera, family portrait",
        
        "Photo-realistic portrait of 4 Central Asian family members, traditional family photo, professional photography, clear faces, neutral background, good lighting, facing camera",
        
        "Photo-realistic portrait of 4 multi-ethnic family members, very diverse backgrounds, professional photography, clear faces, neutral background, good lighting, facing camera, inclusive family"
    ]
    
    successful = 0
    for i, prompt in enumerate(source_prompts, 1):
        filename = f"test-results/source-images/source_{i:02d}.jpg"
        if generate_image(prompt, filename):
            successful += 1
        time.sleep(2)  # Rate limiting
    
    print(f"Source images: {successful}/20 generated successfully")
    return successful

def generate_target_images():
    """Generate 20 Christmas card target images"""
    print("\nGenerating Christmas card target images...")
    
    christmas_styles = [
        "traditional Victorian Christmas",
        "modern minimalist Christmas",
        "rustic winter wonderland",
        "elegant golden Christmas",
        "cozy fireplace Christmas",
        "snowy outdoor Christmas",
        "classic red and green Christmas",
        "winter forest Christmas",
        "vintage Christmas card",
        "luxury Christmas celebration"
    ]
    
    christmas_messages = [
        "Merry Christmas and Happy New Year!",
        "Wishing you joy, peace, and love this Christmas",
        "May your holidays be filled with wonder and joy",
        "Season's Greetings from our family to yours",
        "Christmas blessings to you and your loved ones",
        "Warmest wishes for a magical Christmas",
        "May the spirit of Christmas bring you happiness",
        "Sending you Christmas cheer and warm wishes",
        "Hope your Christmas is merry and bright",
        "Joy to the world and to your family"
    ]
    
    target_prompts = []
    for i in range(20):
        style = christmas_styles[i % len(christmas_styles)]
        message = christmas_messages[i % len(christmas_messages)]
        
        prompt = f"Photo-realistic Christmas greeting card featuring 4 people smiling at camera, {style} style, professional photography, high quality, festive atmosphere, holiday decorations, Christmas tree, warm lighting, joyful expressions, family portrait style, text overlay '{message}', Christmas ornaments, holiday setting"
        target_prompts.append(prompt)
    
    successful = 0
    for i, prompt in enumerate(target_prompts, 1):
        filename = f"test-results/target-images/target_{i:02d}.jpg"
        if generate_image(prompt, filename):
            successful += 1
        time.sleep(2)  # Rate limiting
    
    print(f"Target images: {successful}/20 generated successfully")
    return successful

def main():
    """Generate all test images"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    print("Starting batch image generation...")
    print("This will generate 40 images total (20 source + 20 target)")
    print("Estimated time: ~3-4 minutes with rate limiting\n")
    
    # Generate source images
    source_success = generate_source_images()
    
    # Generate target images  
    target_success = generate_target_images()
    
    print(f"\n🎉 Generation complete!")
    print(f"Source images: {source_success}/20")
    print(f"Target images: {target_success}/20")
    print(f"Total: {source_success + target_success}/40 images generated")
    
    if source_success == 20 and target_success == 20:
        print("\n✅ All images generated successfully!")
        print("Ready to run batch face swap tests.")
    else:
        print("\n⚠️ Some images failed to generate. Check the logs above.")

if __name__ == "__main__":
    main()