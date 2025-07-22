import axios from 'axios';
import { FaceSwapV2Request, FaceSwapV4Request, ApiResponse, ImageGenerationRequest, GeneratedImagePair } from './types';

const SEGMIND_BASE_URL = 'https://api.segmind.com/v1';

export class SegmindAPI {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  private getHeaders() {
    return {
      'x-api-key': this.apiKey,
      'Content-Type': 'application/json'
    };
  }

  async faceSwapV2(request: FaceSwapV2Request): Promise<ApiResponse> {
    try {
      // Add the base64 parameter to match the working example
      const requestWithBase64 = {
        ...request,
        base64: false // This tells API to return URL instead of base64
      };

      console.log('Face Swap V2 Request:', {
        url: `${SEGMIND_BASE_URL}/faceswap-v2`,
        headers: this.getHeaders(),
        requestSize: JSON.stringify(requestWithBase64).length,
        params: requestWithBase64
      });
      
      const response = await axios.post(
        `${SEGMIND_BASE_URL}/faceswap-v2`,
        requestWithBase64,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error: any) {
      console.error('Face Swap V2 Error Details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        request: error.config
      });
      
      const errorMessage = error.response?.data?.message || error.response?.data || error.message;
      throw new Error(`Face Swap V2 API Error (${error.response?.status}): ${errorMessage}`);
    }
  }

  async faceSwapV4(request: FaceSwapV4Request): Promise<ApiResponse> {
    try {
      console.log('Face Swap V4.3 Request:', {
        url: `${SEGMIND_BASE_URL}/faceswap-v4.3`,
        headers: this.getHeaders(),
        requestSize: JSON.stringify(request).length
      });
      
      const response = await axios.post(
        `${SEGMIND_BASE_URL}/faceswap-v4.3`,
        request,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error: any) {
      console.error('Face Swap V4.3 Error Details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        request: error.config
      });
      
      const errorMessage = error.response?.data?.message || error.response?.data || error.message;
      throw new Error(`Face Swap V4.3 API Error (${error.response?.status}): ${errorMessage}`);
    }
  }

  async generateImage(request: ImageGenerationRequest): Promise<ApiResponse> {
    try {
      console.log('Image Generation Request:', {
        url: `${SEGMIND_BASE_URL}/sdxl1.0-txt2img`,
        headers: this.getHeaders(),
        requestSize: JSON.stringify(request).length
      });
      
      const response = await axios.post(
        `${SEGMIND_BASE_URL}/sdxl1.0-txt2img`,
        request,
        { headers: this.getHeaders() }
      );
      return response.data;
    } catch (error: any) {
      console.error('Image Generation Error Details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        request: error.config
      });
      
      const errorMessage = error.response?.data?.message || error.response?.data || error.message;
      throw new Error(`Image Generation API Error (${error.response?.status}): ${errorMessage}`);
    }
  }
}

export const convertFileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      // Remove the data URL prefix (data:image/...;base64,) and keep only base64 string
      const base64Only = result.split(',')[1];
      resolve(base64Only);
    };
    reader.onerror = error => reject(error);
  });
};

const CHRISTMAS_MESSAGES = [
  "Merry Christmas and Happy New Year!",
  "Wishing you joy, peace, and love this Christmas",
  "May your holidays be filled with wonder and joy",
  "Season's Greetings from our family to yours",
  "Christmas blessings to you and your loved ones",
  "Warmest wishes for a magical Christmas",
  "May the spirit of Christmas bring you happiness",
  "Sending you Christmas cheer and warm wishes"
];

const CHRISTMAS_STYLES = [
  "traditional Victorian Christmas style",
  "modern minimalist Christmas aesthetic",
  "rustic winter wonderland theme",
  "elegant golden Christmas decoration",
  "cozy fireplace Christmas setting",
  "snowy outdoor Christmas scene",
  "classic red and green Christmas theme",
  "winter forest Christmas backdrop"
];

export const loadExampleImages = async (): Promise<GeneratedImagePair> => {
  try {
    const [sourceResponse, targetResponse] = await Promise.all([
      fetch('/example_images/input1.jpg'),
      fetch('/example_images/target1.png')
    ]);

    if (!sourceResponse.ok || !targetResponse.ok) {
      throw new Error('Failed to load example images');
    }

    const [sourceBlob, targetBlob] = await Promise.all([
      sourceResponse.blob(),
      targetResponse.blob()
    ]);

    const sourceBase64 = await new Promise<string>((resolve) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (data:image/jpeg;base64,) and keep only base64 string
        const base64Only = result.split(',')[1];
        resolve(base64Only);
      };
      reader.readAsDataURL(sourceBlob);
    });

    const targetBase64 = await new Promise<string>((resolve) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix (data:image/png;base64,) and keep only base64 string
        const base64Only = result.split(',')[1];
        resolve(base64Only);
      };
      reader.readAsDataURL(targetBlob);
    });

    return {
      sourceImage: sourceBase64,
      targetImage: targetBase64,
      sourcePrompt: 'Example source image (input1.jpg)',
      targetPrompt: 'Example target image (target1.png)'
    };
  } catch (error) {
    throw new Error(`Failed to load example images: ${error}`);
  }
};

export const saveImageToFile = async (base64Data: string, filename: string, mimeType: string = 'image/png'): Promise<void> => {
  try {
    // Convert base64 to blob
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: mimeType });

    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error(`Failed to save ${filename}:`, error);
    throw new Error(`Failed to save ${filename}: ${error}`);
  }
};

export const saveTestResults = async (
  testResult: any,
  sourceBase64: string,
  targetBase64: string,
  resultBase64: string
): Promise<void> => {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const version = testResult.version.replace('.', '_');
    const faceIndices = testResult.sourceFaceIndex !== undefined ? 
      `_face${testResult.sourceFaceIndex}to${testResult.targetFaceIndex}` : '';
    const mode = testResult.imageMode || 'upload';

    const baseFilename = `${timestamp}_${version}${faceIndices}_${mode}`;

    // Save all three images
    await Promise.all([
      saveImageToFile(sourceBase64, `${baseFilename}_source.png`, 'image/png'),
      saveImageToFile(targetBase64, `${baseFilename}_target.png`, 'image/png'),
      saveImageToFile(resultBase64, `${baseFilename}_result.png`, 'image/png')
    ]);

    // Save metadata as JSON
    const metadata = {
      timestamp: testResult.timestamp,
      version: testResult.version,
      sourceFaceIndex: testResult.sourceFaceIndex,
      targetFaceIndex: testResult.targetFaceIndex,
      imageMode: testResult.imageMode,
      requestTime: testResult.requestTime,
      cost: testResult.result?.cost,
      inferenceTime: testResult.result?.inference_time,
      error: testResult.error
    };

    const metadataBlob = new Blob([JSON.stringify(metadata, null, 2)], { type: 'application/json' });
    const metadataUrl = URL.createObjectURL(metadataBlob);
    const metadataLink = document.createElement('a');
    metadataLink.href = metadataUrl;
    metadataLink.download = `${baseFilename}_metadata.json`;
    document.body.appendChild(metadataLink);
    metadataLink.click();
    document.body.removeChild(metadataLink);
    URL.revokeObjectURL(metadataUrl);

    console.log(`Saved test results: ${baseFilename}`);
  } catch (error) {
    console.error('Failed to save test results:', error);
  }
};

export const generateRandomChristmasImages = async (api: SegmindAPI): Promise<GeneratedImagePair> => {
  const randomMessage = CHRISTMAS_MESSAGES[Math.floor(Math.random() * CHRISTMAS_MESSAGES.length)];
  const randomStyle = CHRISTMAS_STYLES[Math.floor(Math.random() * CHRISTMAS_STYLES.length)];
  
  const targetPrompt = `Photo-realistic Christmas greeting card featuring 4 people smiling at camera, ${randomStyle}, professional photography, high quality, festive atmosphere, holiday decorations, text overlay "${randomMessage}", warm lighting, joyful expressions, family portrait style`;
  
  const sourcePrompt = `Photo-realistic portrait of 4 family members, high quality professional photography, clear faces, good lighting, neutral background, facing camera, family photo style, diverse ages, smiling expressions, casual clothing`;

  try {
    const [targetResponse, sourceResponse] = await Promise.all([
      api.generateImage({
        prompt: targetPrompt,
        width: 768,
        height: 512,
        num_inference_steps: 30,
        guidance_scale: 7.5,
        seed: Math.floor(Math.random() * 1000000)
      }),
      api.generateImage({
        prompt: sourcePrompt,
        width: 768,
        height: 512,
        num_inference_steps: 30,
        guidance_scale: 7.5,
        seed: Math.floor(Math.random() * 1000000)
      })
    ]);

    return {
      targetImage: targetResponse.image,
      sourceImage: sourceResponse.image,
      targetPrompt,
      sourcePrompt
    };
  } catch (error) {
    throw new Error(`Failed to generate images: ${error}`);
  }
};