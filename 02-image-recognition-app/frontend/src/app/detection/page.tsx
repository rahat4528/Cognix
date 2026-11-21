'use client';

import React, { useState, useEffect } from 'react';
import { Crosshair, Sliders, Layers } from 'lucide-react';
import { ImageAsset, DetectionResult } from '@/lib/types';
import { fetchImages, runDetection } from '@/lib/api';
import CanvasDetectionViewer from '@/components/CanvasDetectionViewer';

export default function DetectionStudio() {
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageAsset | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [inferring, setInferring] = useState<boolean>(false);

  useEffect(() => {
    fetchImages()
      .then((data) => {
        setImages(data);
        if (data.length > 0) {
          setSelectedImage(data[0]);
          executeDetection(data[0].id);
        }
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const executeDetection = async (imageId: string) => {
    setInferring(true);
    try {
      const res = await runDetection(imageId, 0.20);
      setDetectionResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setInferring(false);
    }
  };

  const handleSelectImage = (img: ImageAsset) => {
    setSelectedImage(img);
    executeDetection(img.id);
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">SSDLite Object Detection & Localization</h2>
        <p className="text-sm text-slate-400 mt-1">
          Interactive HTML5 Canvas bounding box viewer with multi-box localization, class filtering, and COCO format export.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading detection studio...</div>
      ) : images.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-500">No images available. Upload an image first.</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Thumbnails Picker */}
          <div className="lg:col-span-1 space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Select Visual Asset
            </span>
            <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
              {images.map((img) => (
                <button
                  key={img.id}
                  onClick={() => handleSelectImage(img)}
                  className={`w-full flex items-center space-x-3 p-2 rounded-xl border text-left transition ${
                    selectedImage?.id === img.id
                      ? 'border-primary bg-primary/10 ring-1 ring-primary'
                      : 'border-surfaceBorder bg-surface hover:border-slate-700'
                  }`}
                >
                  <img
                    src={img.thumbnail_url}
                    alt={img.original_name}
                    className="w-14 h-14 object-cover rounded-lg shrink-0 border border-surfaceBorder"
                  />
                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-medium text-white truncate">{img.original_name}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {img.width} × {img.height} px
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Right Canvas & Detections Display */}
          <div className="lg:col-span-3 space-y-4">
            {selectedImage && detectionResult && (
              <>
                {/* Meta bar */}
                <div className="bg-surface border border-surfaceBorder rounded-xl px-5 py-3 flex items-center justify-between text-xs text-slate-300">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-white">{selectedImage.original_name}</span>
                    <span className="text-slate-500">•</span>
                    <span>Architecture: {detectionResult.model_name}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span>
                      Latency: <strong className="text-accent">{detectionResult.latency_ms} ms</strong>
                    </span>
                    <span>
                      Total Objects: <strong className="text-white">{detectionResult.total_objects}</strong>
                    </span>
                  </div>
                </div>

                {/* Canvas Detection Viewer */}
                <CanvasDetectionViewer
                  imageUrl={selectedImage.image_url}
                  originalWidth={selectedImage.width}
                  originalHeight={selectedImage.height}
                  detections={detectionResult.detections}
                  filename={selectedImage.original_name.split('.')[0]}
                />
              </>
            )}
            {inferring && (
              <div className="text-center py-4 text-xs text-primary animate-pulse">
                Running real-time SSDLite detection pass...
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
