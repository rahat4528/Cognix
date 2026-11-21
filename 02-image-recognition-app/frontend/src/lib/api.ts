import {
  ImageAsset,
  ClassificationResult,
  DetectionResult,
  ExplainabilityResult,
  SimilaritySearchResponse,
  CVModelInfo
} from './types';

const API_BASE = '/api/v1';

export async function fetchImages(): Promise<ImageAsset[]> {
  const res = await fetch(`${API_BASE}/images/`);
  if (!res.ok) throw new Error('Failed to fetch images');
  return res.json();
}

export async function uploadImage(file: File): Promise<ImageAsset> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/images/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(errorData.detail || 'Upload failed');
  }
  return res.json();
}

export async function deleteImage(imageId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/images/${imageId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete image');
}

export async function runClassification(
  imageId: string,
  topK: number = 5,
  uncertaintyThreshold: number = 0.20
): Promise<ClassificationResult> {
  const res = await fetch(
    `${API_BASE}/inference/classify/${imageId}?top_k=${topK}&uncertainty_threshold=${uncertaintyThreshold}`,
    { method: 'POST' }
  );
  if (!res.ok) throw new Error('Classification failed');
  return res.json();
}

export async function runDetection(
  imageId: string,
  scoreThreshold: number = 0.30
): Promise<DetectionResult> {
  const res = await fetch(
    `${API_BASE}/inference/detect/${imageId}?score_threshold=${scoreThreshold}`,
    { method: 'POST' }
  );
  if (!res.ok) throw new Error('Detection failed');
  return res.json();
}

export async function runExplainability(
  imageId: string,
  targetClassId?: number,
  alpha: number = 0.5
): Promise<ExplainabilityResult> {
  let url = `${API_BASE}/inference/explain/${imageId}?alpha=${alpha}`;
  if (targetClassId !== undefined) {
    url += `&target_class_id=${targetClassId}`;
  }
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) throw new Error('Explainability analysis failed');
  return res.json();
}

export async function searchSimilarImages(imageId: string, topK: number = 6): Promise<SimilaritySearchResponse> {
  const res = await fetch(`${API_BASE}/analyses/similarity-search/${imageId}?top_k=${topK}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Similarity search failed' }));
    throw new Error(err.detail || 'Similarity search failed');
  }
  return res.json();
}

export async function fetchModels(): Promise<CVModelInfo[]> {
  const res = await fetch(`${API_BASE}/models/`);
  if (!res.ok) throw new Error('Failed to fetch models');
  const data = await res.json();
  return data.models;
}

export async function processLiveCameraFrame(blob: Blob, scoreThreshold: number = 0.35) {
  const formData = new FormData();
  formData.append('file', blob, 'webcam_frame.jpg');
  const res = await fetch(`${API_BASE}/inference/live-frame?score_threshold=${scoreThreshold}`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Live frame processing failed');
  return res.json();
}
