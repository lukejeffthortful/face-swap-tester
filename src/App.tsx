import React, { useState } from 'react';
import { SegmindAPI, convertFileToBase64, generateRandomChristmasImages, loadExampleImages, saveTestResults } from './api';
import { TestResult } from './types';
import './App.css';

function App() {
  const apiKey = process.env.REACT_APP_SEGMIND_API_KEY || '';
  const [sourceImage, setSourceImage] = useState<File | null>(null);
  const [targetImage, setTargetImage] = useState<File | null>(null);
  const [results, setResults] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [imageMode, setImageMode] = useState<'upload' | 'random' | 'example'>('upload');

  const handleFileUpload = (file: File, type: 'source' | 'target') => {
    if (type === 'source') {
      setSourceImage(file);
    } else {
      setTargetImage(file);
    }
  };

  const runTest = async (version: 'v2' | 'v4.3', sourceFaceIndex?: number, targetFaceIndex?: number) => {
    if (!apiKey) {
      alert('Please ensure API key is set in .env file');
      return;
    }

    if (imageMode === 'upload' && (!sourceImage || !targetImage)) {
      alert('Please provide both images');
      return;
    }

    setLoading(true);
    const api = new SegmindAPI(apiKey);
    
    try {
      let sourceBase64: string;
      let targetBase64: string;
      let sourceImageUrl: string;
      let targetImageUrl: string;

      if (imageMode === 'random') {
        const generatedImages = await generateRandomChristmasImages(api);
        sourceBase64 = generatedImages.sourceImage;
        targetBase64 = generatedImages.targetImage;
        sourceImageUrl = generatedImages.sourceImage;
        targetImageUrl = generatedImages.targetImage;
      } else if (imageMode === 'example') {
        const exampleImages = await loadExampleImages();
        sourceBase64 = exampleImages.sourceImage;
        targetBase64 = exampleImages.targetImage;
        // For display purposes, we need data URLs
        sourceImageUrl = `data:image/jpeg;base64,${exampleImages.sourceImage}`;
        targetImageUrl = `data:image/png;base64,${exampleImages.targetImage}`;
      } else {
        sourceBase64 = await convertFileToBase64(sourceImage!);
        targetBase64 = await convertFileToBase64(targetImage!);
        // For display purposes, we need data URLs
        sourceImageUrl = `data:${sourceImage!.type};base64,${sourceBase64}`;
        targetImageUrl = `data:${targetImage!.type};base64,${targetBase64}`;
      }

      const requestStartTime = performance.now();
      let result;
      if (version === 'v2') {
        result = await api.faceSwapV2({
          source_img: sourceBase64,
          target_img: targetBase64,
          source_faces_index: sourceFaceIndex ?? 0,
          input_faces_index: targetFaceIndex ?? 0,
          face_restore: "codeformer-v0.1.0.pth"
        });
      } else {
        result = await api.faceSwapV4({
          source_image: sourceBase64,
          target_image: targetBase64,
          source_face_index: sourceFaceIndex ?? 0,
          target_face_index: targetFaceIndex ?? 0,
          detection_face_order: "big_to_small"
        });
      }
      const requestEndTime = performance.now();
      const requestTime = Math.round(requestEndTime - requestStartTime);

      // Debug: log the result structure
      console.log('API Response:', result);

      // Handle result image - could be URL or base64 depending on API response
      let resultImageUrl = '';
      if (result.image && typeof result.image === 'string') {
        if (result.image.startsWith('http')) {
          // It's a URL - use directly
          resultImageUrl = result.image;
        } else if (result.image.startsWith('data:')) {
          // It's already a data URL
          resultImageUrl = result.image;
        } else {
          // It's raw base64 - add data URL prefix
          resultImageUrl = `data:image/png;base64,${result.image}`;
        }
      } else {
        console.error('No image data in API response:', result);
      }

      const testResult: TestResult = {
        version,
        result: {
          ...result,
          image: resultImageUrl // Store formatted image URL for display
        },
        timestamp: Date.now(),
        sourceImage: sourceImageUrl,
        targetImage: targetImageUrl,
        isRandomGenerated: imageMode === 'random',
        requestTime,
        sourceFaceIndex,
        targetFaceIndex,
        imageMode
      };

      // Auto-save results to downloads folder
      if (result.image && typeof result.image === 'string') {
        try {
          let originalBase64 = '';
          
          if (result.image.startsWith('http')) {
            // Convert URL to base64 for saving
            const response = await fetch(result.image);
            const blob = await response.blob();
            const base64 = await new Promise<string>((resolve) => {
              const reader = new FileReader();
              reader.onload = () => {
                const result = reader.result as string;
                resolve(result.split(',')[1]);
              };
              reader.readAsDataURL(blob);
            });
            originalBase64 = base64;
          } else if (result.image.startsWith('data:')) {
            // Strip data URL prefix
            originalBase64 = result.image.split(',')[1];
          } else {
            // Already base64
            originalBase64 = result.image;
          }
          
          await saveTestResults(testResult, sourceBase64, targetBase64, originalBase64);
        } catch (error) {
          console.error('Failed to save test results:', error);
        }
      } else {
        console.warn('Skipping save - no valid image data');
      }

      setResults(prev => [...prev, testResult]);
    } catch (error) {
      const testResult: TestResult = {
        version,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: Date.now(),
        isRandomGenerated: imageMode === 'random',
        sourceFaceIndex,
        targetFaceIndex,
        imageMode
      };
      setResults(prev => [...prev, testResult]);
    } finally {
      setLoading(false);
    }
  };

  const runExampleTests = async () => {
    setLoading(true);
    for (let faceIndex = 0; faceIndex < 4; faceIndex++) {
      await runTest('v2', faceIndex, faceIndex);
      await runTest('v4.3', faceIndex, faceIndex);
    }
    setLoading(false);
  };

  const runComparison = async () => {
    await runTest('v2');
    await runTest('v4.3');
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Face Swap API Tester</h1>
        <p>Compare Segmind Face Swap v2 vs v4.3</p>
      </header>

      <main className="App-main">
        <section className="upload-section">
          <h2>Image Selection</h2>
          <div className="image-mode-selection">
            <div className="form-group">
              <label>
                <input
                  type="radio"
                  name="imageMode"
                  value="upload"
                  checked={imageMode === 'upload'}
                  onChange={(e) => setImageMode('upload')}
                />
                Upload your own images
              </label>
            </div>

            <div className="form-group">
              <label>
                <input
                  type="radio"
                  name="imageMode"
                  value="example"
                  checked={imageMode === 'example'}
                  onChange={(e) => setImageMode('example')}
                />
                Use example test images (4 faces each)
              </label>
            </div>

            <div className="form-group">
              <label>
                <input
                  type="radio"
                  name="imageMode"
                  value="random"
                  checked={imageMode === 'random'}
                  onChange={(e) => setImageMode('random')}
                />
                Generate random Christmas images (4 people)
              </label>
            </div>
          </div>

          {imageMode === 'upload' && (
            <div className="upload-grid">
              <div className="upload-item">
                <label htmlFor="source-upload">Source Image (Your face):</label>
                <input
                  id="source-upload"
                  type="file"
                  accept="image/*"
                  onChange={(e) => e.target.files && handleFileUpload(e.target.files[0], 'source')}
                />
                {sourceImage && (
                  <div className="image-preview">
                    <img src={URL.createObjectURL(sourceImage)} alt="Source" />
                    <p>{sourceImage.name}</p>
                  </div>
                )}
              </div>

              <div className="upload-item">
                <label htmlFor="target-upload">Target Image (Face to swap with):</label>
                <input
                  id="target-upload"
                  type="file"
                  accept="image/*"
                  onChange={(e) => e.target.files && handleFileUpload(e.target.files[0], 'target')}
                />
                {targetImage && (
                  <div className="image-preview">
                    <img src={URL.createObjectURL(targetImage)} alt="Target" />
                    <p>{targetImage.name}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {imageMode === 'example' && (
            <div className="example-info">
              <p>🧪 Test suite will use example images:</p>
              <ul>
                <li>Source: input1.jpg (4 faces)</li>
                <li>Target: target1.png (4 faces)</li>
                <li>Will test all face mappings: 0→0, 1→1, 2→2, 3→3</li>
                <li>Tests both v2 and v4.3 APIs for each face pair</li>
              </ul>
            </div>
          )}

          {imageMode === 'random' && (
            <div className="random-info">
              <p>✨ Random images will be generated automatically:</p>
              <ul>
                <li>Target: Christmas greeting card with 4 people in festive setting</li>
                <li>Source: Family portrait with 4 people for face swapping</li>
                <li>Various Christmas themes and messages</li>
              </ul>
            </div>
          )}
        </section>

        <section className="controls-section">
          <h2>Test Controls</h2>
          <div className="button-group">
            {imageMode === 'example' ? (
              <button 
                onClick={runExampleTests} 
                disabled={loading}
                className="primary"
              >
                Run Complete Test Suite (8 tests)
              </button>
            ) : (
              <>
                <button 
                  onClick={() => runTest('v2')} 
                  disabled={loading || (imageMode === 'upload' && (!sourceImage || !targetImage))}
                >
                  Test v2 Only
                </button>
                <button 
                  onClick={() => runTest('v4.3')} 
                  disabled={loading || (imageMode === 'upload' && (!sourceImage || !targetImage))}
                >
                  Test v4.3 Only
                </button>
                <button 
                  onClick={runComparison} 
                  disabled={loading || (imageMode === 'upload' && (!sourceImage || !targetImage))}
                  className="primary"
                >
                  Compare Both APIs
                </button>
              </>
            )}
            <button onClick={clearResults} disabled={results.length === 0}>
              Clear Results
            </button>
          </div>
          {loading && <p className="loading">Processing...</p>}
        </section>

        <section className="results-section">
          <h2>Results</h2>
          {results.length === 0 ? (
            <p>No results yet. Upload images and run a test.</p>
          ) : (
            <div className="results-grid">
              {results.map((result, index) => (
                <div key={index} className="result-item">
                  <h3>
                    Face Swap {result.version}
                    {result.sourceFaceIndex !== undefined && result.targetFaceIndex !== undefined && (
                      <span className="face-indices"> (Face {result.sourceFaceIndex}→{result.targetFaceIndex})</span>
                    )}
                  </h3>
                  <p className="timestamp">
                    {new Date(result.timestamp).toLocaleString()}
                  </p>
                  {result.imageMode === 'random' && (
                    <p className="generation-badge">🎄 Random Generated</p>
                  )}
                  {result.imageMode === 'example' && (
                    <p className="generation-badge example">🧪 Example Test</p>
                  )}
                  
                  {result.error ? (
                    <div className="error">
                      <p>Error: {result.error}</p>
                    </div>
                  ) : result.result ? (
                    <div className="success">
                      <div className="image-comparison">
                        <div className="comparison-column">
                          <h4>Target Image</h4>
                          <img src={result.targetImage} alt="Target" />
                          <p>Original greeting card</p>
                        </div>
                        
                        <div className="comparison-column">
                          <h4>Source Image</h4>
                          <img src={result.sourceImage} alt="Source" />
                          <p>Family faces to swap</p>
                        </div>
                        
                        <div className="comparison-column">
                          <h4>Result</h4>
                          <img src={result.result.image} alt={`Result ${result.version}`} />
                          <p>Face swapped result</p>
                        </div>
                      </div>
                      
                      <div className="result-metrics">
                        {result.result.cost && <span>Cost: ${result.result.cost}</span>}
                        {result.result.inference_time && <span>API Time: {result.result.inference_time}s</span>}
                        {result.requestTime && <span>Total Request: {result.requestTime}ms</span>}
                      </div>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;