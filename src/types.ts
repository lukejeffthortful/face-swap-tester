export interface FaceSwapV2Request {
  source_img: string;
  target_img: string;
  input_faces_index?: number;
  source_faces_index?: number;
  face_restore?: 'codeformer-v0.1.0.pth' | 'GFPGANv1.4.pth' | 'GFPGANv1.3.pth';
  base64?: boolean;
}

export interface FaceSwapV4Request {
  source_image: string;
  target_image: string;
  source_face_index?: number;
  target_face_index?: number;
  detection_face_order?: 'left_to_right' | 'top_to_bottom' | 'big_to_small';
  model_type?: 'speed' | 'quality';
  swap_type?: 'head' | 'face';
  style_type?: 'normal' | 'style';
  seed?: number;
  image_format?: 'JPEG' | 'PNG' | 'WebP';
  image_quality?: number;
}

export interface ApiResponse {
  image: string;
  cost?: number;
  inference_time?: number;
}

export interface TestResult {
  version: 'v2' | 'v4.3';
  result?: ApiResponse;
  error?: string;
  timestamp: number;
  sourceImage?: string;
  targetImage?: string;
  isRandomGenerated?: boolean;
  requestTime?: number;
  sourceFaceIndex?: number;
  targetFaceIndex?: number;
  imageMode?: 'upload' | 'random' | 'example';
}

export interface ImageGenerationRequest {
  prompt: string;
  width?: number;
  height?: number;
  num_inference_steps?: number;
  guidance_scale?: number;
  seed?: number;
}

export interface GeneratedImagePair {
  targetImage: string;
  sourceImage: string;
  targetPrompt: string;
  sourcePrompt: string;
}