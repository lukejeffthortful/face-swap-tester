# Face Swap API Testing Dashboard

Comprehensive testing and comparison of Segmind Face Swap APIs (v2, v4, v4.3).

## 🎯 Live Demo

**[View Dashboard](https://lukejeffthortful.github.io/face-swap-tester/)**

## 📊 Test Results

- **Single-Face Testing**: 100% complete (40/40 V2, 40/40 V4)
- **Multi-Face Testing**: 62% complete (21/13 V2/V4.3)
- **Performance**: V4 optimized 60-70% faster with cost-effective settings

## 🔬 Testing Coverage

### Single-Face Tests
- 4 source images × 10 target images = 40 combinations
- V2 vs V4 API comparison using face index 0
- Comprehensive CSV logging with 31 metadata fields
- Average response times: V2=16.2s, V4=17.8s (optimized)

### Multi-Face Tests  
- 3 family photos × 7 target combinations = 21 tests
- V2 vs V4.3 API comparison with all detected faces
- Face detection order: "big_to_small", "left_to_right", "top_to_bottom"

## 🚀 Key Features

- **Interactive Dashboard**: Compare results side-by-side
- **Performance Analytics**: Detailed timing and success rates  
- **Image Galleries**: Full-resolution result previews
- **API Debugging**: Comprehensive request/response logging
- **Parameter Optimization**: Speed vs quality tradeoffs

## 📈 Performance Insights

- **V4 Optimization**: Updated from quality to speed/cost settings
- **Success Rate**: 97.5% for V4 API calls
- **Timeout Handling**: Robust retry logic with detailed error logging
- **Rate Limiting**: 2-second delays between requests

## 🛠️ Technical Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Testing**: Python batch processing scripts
- **APIs**: Segmind Face Swap v2, v4, v4.3
- **Hosting**: GitHub Pages (free static hosting)

---

*Generated for comprehensive face swap API evaluation and comparison*