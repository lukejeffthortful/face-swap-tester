# Diverse Source Images for Face Swap Testing

## Overview
This folder (`diverse-source-images/`) is designed to hold 10 diverse source images for comprehensive face swap testing using Thortful's V4 API.

## Recommended Image Mix

### Demographics (10 total images)
- **2-3 Adult Men** (different ethnicities: Caucasian, African, Asian, Hispanic, etc.)
- **2-3 Adult Women** (different ethnicities: Caucasian, African, Asian, Hispanic, etc.)
- **1-2 Children** (various ages 5-12, different ethnicities)
- **1-2 Elderly People** (60+, different ethnicities)
- **1-2 Mixed/Other** (teenagers, mixed ethnicities, etc.)

### Technical Requirements
- **Format:** JPG or PNG
- **Resolution:** Minimum 512x512 pixels (higher is better)
- **Face clarity:** Clear, frontal face shots
- **Lighting:** Good, even lighting preferred
- **Single face:** One clear face per image
- **No accessories:** Minimal glasses, hats, or face coverings

### Image Quality Guidelines
- **High quality:** Clear, sharp images
- **Various lighting:** Mix of indoor/outdoor, different lighting conditions
- **Different angles:** Mostly frontal, some slight angles
- **Natural expressions:** Mix of smiling and neutral expressions

## File Naming Convention
Suggest naming files descriptively:
- `adult_male_caucasian_01.jpg`
- `adult_female_african_01.jpg` 
- `child_asian_male_01.jpg`
- `elderly_hispanic_female_01.jpg`
- etc.

## Sources for Images
- **Stock Photo Sites:** Unsplash, Pexels, Pixabay (check licenses)
- **AI Generated:** Midjourney, Stable Diffusion, etc.
- **Personal Collections:** With proper permissions
- **Test Datasets:** Public face datasets for research

## Usage
Once you have 10 diverse images in this folder, run:
```bash
python3 thortful_test_single_face.py
```

This will test all combinations of:
- 10 diverse source images
- Target images (card templates)
- 26 different card template IDs

Expected total tests: 10 × target_images × 26 card_templates

## Results
- **Processed images:** Saved to `results/` folder
- **Detailed logs:** Saved to `logs/thortful_diverse_face_tests.csv`
- **Review interface:** Open `thortful_review.html` in browser