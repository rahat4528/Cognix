export interface ImageAsset {
  id: string;
  filename: string;
  original_name: string;
  mime_type: string;
  file_size_bytes: number;
  width: number;
  height: number;
  perceptual_hash: string;
  thumbnail_url: string;
  image_url: string;
  created_at: string;
}

export interface PredictionItem {
  class_id: number;
  label: string;
  score: number;
}

export interface ClassificationResult {
  analysis_id: string;
  image_id: string;
  model_name: string;
  model_version: string;
  top_label: string;
  top_score: number;
  is_uncertain: boolean;
  predictions: PredictionItem[];
  embedding?: number[];
  latency_ms: number;
}

export interface DetectedObject {
  label: string;
  class_id: number;
  score: number;
  bbox_pixels: [number, number, number, number]; // [x1, y1, x2, y2]
  bbox_normalized: [number, number, number, number];
  width: number;
  height: number;
}

export interface DetectionResult {
  analysis_id: string;
  image_id: string;
  model_name: string;
  model_version: string;
  total_objects: number;
  class_counts: Record<string, number>;
  detections: DetectedObject[];
  latency_ms: number;
}

export interface ExplainabilityResult {
  analysis_id: string;
  image_id: string;
  model_name: string;
  target_class_id: number;
  target_label: string;
  confidence: number;
  heatmap_data_url: string;
  disclaimer: string;
  latency_ms: number;
}

export interface SimilarityMatch {
  image_id: string;
  original_name: string;
  thumbnail_url: string;
  similarity_score: number;
  top_label?: string;
}

export interface SimilaritySearchResponse {
  query_image_id: string;
  total_candidates: number;
  matches: SimilarityMatch[];
}

export interface CVModelInfo {
  id: string;
  name: string;
  task: string;
  framework: string;
  parameters_millions?: number;
  embedding_dimension?: number;
  input_resolution: string;
  num_classes?: number;
  license: string;
  purpose: string;
}
