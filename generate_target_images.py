#!/usr/bin/env python3
"""
Generate additional Christmas family target images using Segmind GPT-Image API
"""

import requests
import base64
import os
import json
from datetime import datetime

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

def generate_image(prompt, output_path, api_key):
    """Generate image using Segmind GPT-Image API"""
    API_URL = "https://api.segmind.com/v1/gpt-image-1"
    
    data = {
        "prompt": prompt,
        "style": "photorealistic",
        "samples": 1,
        "scheduler": "DDIM",
        "num_inference_steps": 30,
        "guidance_scale": 8.0,
        "seed": -1,
        "img_width": 1024,
        "img_height": 1536,
        "base64": False
    }
    
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"🎨 Generating image: {os.path.basename(output_path)}")
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()
        
        # Save image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Generated: {output_path}")
        
        # Save metadata
        metadata_path = output_path.replace('.png', '_generation_metadata.json')
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "api_endpoint": API_URL,
            "generation_time": response.headers.get('X-generation-time'),
            "remaining_credits": response.headers.get('X-remaining-credits'),
            "request_id": response.headers.get('X-Request-ID'),
            "content_length": response.headers.get('Content-Length'),
            "parameters": data
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True, None
        
    except Exception as e:
        return False, str(e)

def generate_all_target_images():
    """Generate all 3 additional target images"""
    API_KEY = load_api_key()
    if not API_KEY:
        print("❌ Error: Please set REACT_APP_SEGMIND_API_KEY in .env file")
        return
    
    # Ensure target directory exists (for multi-face targets)
    os.makedirs("test-results/multiface-target-images", exist_ok=True)
    
    # Define prompts for each target image
    target_prompts = [
        {
            "filename": "target_03.png",
            "prompt": "Professional Christmas family greeting card with 4 people (2 adults, 2 children) wearing festive red and white holiday sweaters, sitting by a decorated fireplace with stockings, Christmas garland, and warm lighting. Text overlay 'Season's Greetings' in elegant gold lettering. Photorealistic style, high quality, traditional Christmas colors."
        },
        {
            "filename": "target_04.png", 
            "prompt": "Christmas family greeting card featuring 4 family members (parents and 2 kids) in matching plaid pajamas, sitting around a beautifully decorated Christmas tree with presents underneath. Cozy living room setting with twinkling lights. Text overlay 'Joy & Peace' in festive script font. Professional greeting card style, warm and inviting atmosphere."
        },
        {
            "filename": "target_05.png",
            "prompt": "Holiday family portrait greeting card with 4 people wearing elegant winter outfits (sweaters, scarves) standing in front of a snowy backdrop with Christmas lights. Text overlay 'Warmest Wishes for the Holidays' in beautiful serif font. Professional photography style, festive but sophisticated, golden hour lighting."
        },
        {
            "filename": "target_06.png",
            "prompt": "Portrait format Christmas family greeting card with 4 people (2 parents, 2 children) in festive holiday outfits. Family arranged vertically - parents sitting on couch in front, children standing behind them. Everyone wearing Santa hats and red sweaters, wrapped in Christmas lights with big smiles. Professional Christmas portrait style, all faces clearly visible, warm holiday lighting, Christmas tree in background. Text overlay 'All Wrapped Up for the Holidays!' Vertical 3:4 aspect ratio."
        },
        {
            "filename": "target_07.png",
            "prompt": "Photorealistic Christmas greeting card featuring a family of 4 people magically hanging from a mantle like Christmas stockings. Each family member wearing festive pajamas and Santa hats, dangling playfully from decorative hooks on a fireplace mantle with garland and lights. All 4 faces clearly visible, smiling and looking toward camera, professional portrait quality. Text overlay 'Hanging Around for the Holidays!' Studio photography lighting, high detail facial features, magical but realistic Christmas scene, warm cozy atmosphere."
        }
    ]
    
    print("🎄 Generating Christmas Family Target Images")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for target in target_prompts:
        output_path = f"test-results/multiface-target-images/{target['filename']}"
        
        # Skip if already exists
        if os.path.exists(output_path):
            print(f"⏭️  Skipping {target['filename']} - already exists")
            continue
        
        success, error = generate_image(target['prompt'], output_path, API_KEY)
        
        if success:
            successful += 1
        else:
            failed += 1
            print(f"❌ Failed to generate {target['filename']}: {error}")
        
        # Brief pause between generations
        import time
        time.sleep(2)
    
    print(f"\n📊 Generation Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Images saved to: test-results/multiface-target-images/")
    
    if successful > 0:
        print(f"\n🔄 Next step: Run comparative testing with all target images")

if __name__ == "__main__":
    generate_all_target_images()