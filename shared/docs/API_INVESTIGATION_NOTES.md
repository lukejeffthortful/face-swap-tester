# Face Swap API Investigation Notes

## Testing Strategy
- **Multi-face testing**: V2 vs V4.3 (endpoint: `/v1/faceswap-v4.3`)
- **Single-face testing**: V2 vs V4 (endpoint: `/v1/faceswap-v4`)

## Multi-Face Issue Summary
V4.3 API appears to only swap 1 face instead of multiple faces, unlike V2 which handles multi-face swapping correctly.

## Key Findings

### API Status (as of 2025-07-22)
- **V4.3 API is currently down** - returning "Internal Server Error" (HTTP 400) even with minimal parameters
- **V2 API is working** - successfully processes requests and returns image data

### Parameter Differences Between V2 and V4.3

**V2 API Parameters:**
```javascript
{
  source_img: string,
  target_img: string, 
  source_faces_index: number,  // Face index in source image
  input_faces_index: number,   // Face index in target image  
  face_restore: string,
  base64: boolean
}
```

**V4.3 API Parameters:**
```javascript
{
  source_image: string,
  target_image: string,
  source_face_index: number,   // Face index in source image
  target_face_index: number,   // Face index in target image
  detection_face_order: string, // "left_to_right", "top_to_bottom", "big_to_small"
  model_type: string,          // "speed", "quality"
  swap_type: string,           // "head", "face"
  style_type: string           // "normal", "style"
}
```

### Response Format Differences
- **V2**: Returns binary JPEG data when `base64: false`, JSON with base64 when `base64: true`
- **V4.3**: Expected to return JSON with image URL or base64 data

### Multi-Face Support - CONFIRMED ✓
**V4.3 DOES support multi-face indexing** according to official docs at https://www.segmind.com/models/faceswap-v4.3

**Official V4.3 Parameters:**
- `source_face_index` (optional, default: 0) - "Index of the face to use from the source image (0-based)"
- `target_face_index` (optional, default: 0) - "Index of the face to replace in the target image (0-based)" 
- `detection_face_order` (optional, default: "left_to_right") - Options: "left_to_right", "top_to_bottom", "big_to_small"

### Current Implementation Issues - FIXED ✓
1. **FIXED**: Added `detection_face_order: "big_to_small"` to match V2's behavior
2. **Face index parameters correctly implemented** - Need to test when API is back up
3. **Updated all test scripts** to use "big_to_small" detection order

### Changes Made
- Updated React App.tsx to include `detection_face_order: "big_to_small"` in V4.3 calls
- Updated debug_face_indices.py to use "big_to_small" detection order
- Updated simple_face_test.py to use "big_to_small" detection order

## Next Steps

### Multi-Face Testing (when V4.3 API is back up)
1. Test V4.3 with minimal parameters first
2. Test face index parameters individually  
3. Compare face detection with different `detection_face_order` values
4. Verify if V4.3 truly supports multi-face swapping or only single face
5. Check if current React app implementation matches actual V4.3 API spec

### Single-Face Testing (V2 vs V4) - READY ✓
1. Run `batch_test_single_face.py` to test all combinations with face index 0
2. Generate comparison page with `generate_single_face_review.py`
3. Compare single-face quality and performance between V2 and V4

## Files Created for Testing
- `debug_face_indices.py` - Comprehensive face index testing (V4.3)
- `simple_face_test.py` - Basic API functionality verification (V4.3)
- `batch_test_single_face.py` - Single face V2 vs V4 batch testing ✓
- `generate_single_face_review.py` - Single face comparison page generator ✓
- `download_top_thortful_targets.py` - Downloads top 10 Thortful cards ✓
- `generate_main_review.py` - Main navigation page between test types ✓

## Notes
- **V4.3**: Multi-face endpoint confirmed by user, currently down
- **V4**: Single-face endpoint for comparison testing
- Single-face testing system ready to run when needed
- Results will be saved to `test-results/single-face-results/`

## Single-Face Test Images - READY ✓

### Source Images (4 images)
Located in `source-single-face/`:
1. `1443_v9_bc.jpg`
2. `2cb6cd0f-2d06-11e6-bce7-6ff134176666.jpg` 
3. `Cheryl_Cole_Cannes_2014 (1).jpg`
4. `MV5BMTkyNjY1NDg3NF5BMl5BanBnXkFtZTgwNjA2MTg0MzE@._V1_.jpg`

### Target Images (10 images)
Downloaded top 10 most swapped Thortful face swap cards:
1. **target_01.png** - 587 swaps (ID: 67816ae75990fc276575cd07)
2. **target_02.png** - 330 swaps (ID: 6855c0b6ebba0773538e8a15)
3. **target_03.png** - 308 swaps (ID: 66facc0a21fd6d6f34901ae6)
4. **target_04.png** - 232 swaps (ID: 66e01c85ded8e0212043629d)
5. **target_05.png** - 229 swaps (ID: 68097dd5b46c0a5b4e3543f8)
6. **target_06.png** - 217 swaps (ID: 68497934ad723e68b9792266)
7. **target_07.png** - 209 swaps (ID: 67d219a67d3f9803484845be)
8. **target_08.png** - 192 swaps (ID: 680b65d36010d4505cbac642)
9. **target_09.png** - 179 swaps (ID: 6854af2294654d25b467e33b)
10. **target_10.png** - 169 swaps (ID: 680b635ab4259a1b1933d009)

**Total combinations**: 4 sources × 10 targets = 40 combinations  
**Total tests**: 40 × 2 APIs (V2 + V4) = 80 tests  
**Estimated time**: ~5 minutes