'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  UploadCloud,
  Crosshair,
  Sparkles,
  Zap,
  Clock,
  HardDrive,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { ImageAsset, ClassificationResult, DetectionResult } from '@/lib/types';
import { fetchImages, runClassification, runDetection } from '@/lib/api';

export default function WorkbenchHome() {
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedImage, setSelectedImage] = useState<ImageAsset | null>(null);
  const [inferring, setInferring] = useState<boolean>(false);
  const [quickClassResult, setQuickClassResult] = useState<ClassificationResult | null>(null);
  const [quickDetResult, setQuickDetResult] = useState<DetectionResult | null>(null);

  useEffect(() => {
    fetchImages()
      .then((data) => {
        setImages(data);
        if (data.length > 0) setSelectedImage(data[0]);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleQuickInference = async (type: 'classification' | 'detection') => {
    if (!selectedImage) return;
    setInferring(true);
    try {
      if (type === 'classification') {
        const res = await runClassification(selectedImage.id);
        setQuickClassResult(res);
        setQuickDetResult(null);
      } else {
        const res = await runDetection(selectedImage.id);
        setQuickDetResult(res);
        setQuickClassResult(null);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setInferring(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Vision Workbench Overview</h2>
        <p className="text-sm text-slate-400 mt-1">
          High-performance, edge-optimized computer vision inference powered by PyTorch.
        </p>
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-surface border border-surfaceBorder rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Assets</span>
            <HardDrive className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">{images.length}</div>
          <div className="text-[11px] text-slate-500 mt-1">Sanitized & EXIF-stripped</div>
        </div>

        <div className="bg-surface border border-surfaceBorder rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Model Architectures</span>
            <Zap className="w-4 h-4 text-accent" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">2 + Grad-CAM</div>
          <div className="text-[11px] text-slate-500 mt-1">MobileNetV3 & SSDLite</div>
        </div>

        <div className="bg-surface border border-surfaceBorder rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Average Inference</span>
            <Clock className="w-4 h-4 text-warning" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">~35 ms</div>
          <div className="text-[11px] text-slate-500 mt-1">CPU Single-Threaded</div>
        </div>

        <div className="bg-surface border border-surfaceBorder rounded-xl p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Privacy Status</span>
            <ShieldAlert className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">100% Enforced</div>
          <div className="text-[11px] text-slate-500 mt-1">Zero biometric analysis</div>
        </div>
      </div>

      {/* Quick Playground Card */}
      <div className="bg-surface border border-surfaceBorder rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white">Interactive Inference Playground</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Select an ingested visual asset and execute instant authentic PyTorch inference.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              disabled={!selectedImage || inferring}
              onClick={() => handleQuickInference('classification')}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-primary hover:bg-primaryHover disabled:opacity-50 text-white rounded-lg text-xs font-medium transition shadow-md shadow-primary/20"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{inferring ? 'Inferring...' : 'Classify'}</span>
            </button>
            <button
              disabled={!selectedImage || inferring}
              onClick={() => handleQuickInference('detection')}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-accent hover:bg-emerald-600 disabled:opacity-50 text-white rounded-lg text-xs font-medium transition shadow-md shadow-accent/20"
            >
              <Crosshair className="w-3.5 h-3.5" />
              <span>{inferring ? 'Inferring...' : 'Detect Objects'}</span>
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-xs text-slate-500 py-8 text-center">Loading assets...</div>
        ) : images.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-surfaceBorder rounded-lg">
            <UploadCloud className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <p className="text-sm text-slate-400">No images ingested yet.</p>
            <Link
              href="/upload"
              className="inline-flex items-center space-x-1 text-xs text-primary font-medium mt-2 hover:underline"
            >
              <span>Upload your first image</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Asset Picker Grid */}
            <div className="md:col-span-1 space-y-2 max-h-[380px] overflow-y-auto pr-1">
              <span className="text-xs font-medium text-slate-400">Select Image:</span>
              <div className="grid grid-cols-2 gap-2">
                {images.map((img) => (
                  <button
                    key={img.id}
                    onClick={() => {
                      setSelectedImage(img);
                      setQuickClassResult(null);
                      setQuickDetResult(null);
                    }}
                    className={`relative rounded-lg overflow-hidden border p-1 text-left transition ${
                      selectedImage?.id === img.id
                        ? 'border-primary bg-primary/10 ring-1 ring-primary'
                        : 'border-surfaceBorder bg-slate-900/40 hover:border-slate-700'
                    }`}
                  >
                    <img
                      src={img.thumbnail_url}
                      alt={img.original_name}
                      className="w-full h-24 object-cover rounded"
                    />
                    <div className="text-[10px] text-slate-300 truncate mt-1 px-0.5">
                      {img.original_name}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Display / Results Panel */}
            <div className="md:col-span-2 bg-slate-950/60 rounded-xl border border-surfaceBorder p-4 flex flex-col justify-between">
              {selectedImage && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs text-slate-400 border-b border-surfaceBorder pb-2">
                    <span>{selectedImage.original_name}</span>
                    <span>{selectedImage.width} × {selectedImage.height} px</span>
                  </div>

                  {/* Centered Image */}
                  <div className="flex justify-center items-center bg-black/40 rounded-lg p-2 max-h-56 overflow-hidden">
                    <img
                      src={selectedImage.image_url}
                      alt={selectedImage.original_name}
                      className="max-h-52 object-contain rounded"
                    />
                  </div>

                  {/* Classification Result Display */}
                  {quickClassResult && (
                    <div className="bg-surface/90 border border-primary/30 rounded-lg p-3 text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white">Top Prediction:</span>
                        <span className="font-mono text-primary font-bold">
                          {quickClassResult.top_label} ({(quickClassResult.top_score * 100).toFixed(1)}%)
                        </span>
                      </div>
                      <div className="space-y-1">
                        {quickClassResult.predictions.slice(0, 3).map((p) => (
                          <div key={p.class_id} className="flex items-center justify-between text-[11px] text-slate-400">
                            <span>{p.label}</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className="bg-primary h-full"
                                  style={{ width: `${p.score * 100}%` }}
                                />
                              </div>
                              <span className="w-10 text-right font-mono">{(p.score * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800 flex justify-between">
                        <span>Model: {quickClassResult.model_name}</span>
                        <span>Latency: {quickClassResult.latency_ms} ms</span>
                      </div>
                    </div>
                  )}

                  {/* Detection Result Display */}
                  {quickDetResult && (
                    <div className="bg-surface/90 border border-accent/30 rounded-lg p-3 text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white">Objects Detected:</span>
                        <span className="font-mono text-accent font-bold">
                          {quickDetResult.total_objects} items
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {Object.entries(quickDetResult.class_counts).map(([label, count]) => (
                          <span
                            key={label}
                            className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-200 border border-slate-700 text-[11px]"
                          >
                            {label}: <strong>{count}</strong>
                          </span>
                        ))}
                      </div>
                      <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-800 flex justify-between">
                        <span>Model: {quickDetResult.model_name}</span>
                        <span>Latency: {quickDetResult.latency_ms} ms</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Feature Deep Dive Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href="/detection"
          className="group bg-surface border border-surfaceBorder hover:border-primary/50 rounded-xl p-5 transition flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded-lg bg-primary/20 text-primary flex items-center justify-center mb-3">
              <Crosshair className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white group-hover:text-primary transition">
              SSDLite Object Localization
            </h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Interactive HTML5 canvas bounding box overlays, class visibility toggles, and COCO JSON export.
            </p>
          </div>
          <span className="inline-flex items-center text-xs text-primary font-medium mt-4 group-hover:translate-x-0.5 transition">
            Launch Detection Studio &rarr;
          </span>
        </Link>

        <Link
          href="/classification"
          className="group bg-surface border border-surfaceBorder hover:border-accent/50 rounded-xl p-5 transition flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded-lg bg-accent/20 text-accent flex items-center justify-center mb-3">
              <Sparkles className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white group-hover:text-accent transition">
              Classification & Grad-CAM
            </h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              1,000-category softmax probabilities and gradient-weighted class activation mapping (approximate explanation).
            </p>
          </div>
          <span className="inline-flex items-center text-xs text-accent font-medium mt-4 group-hover:translate-x-0.5 transition">
            Open Explainability Studio &rarr;
          </span>
        </Link>

        <Link
          href="/camera"
          className="group bg-surface border border-surfaceBorder hover:border-warning/50 rounded-xl p-5 transition flex flex-col justify-between"
        >
          <div>
            <div className="w-8 h-8 rounded-lg bg-warning/20 text-warning flex items-center justify-center mb-3">
              <Zap className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-semibold text-white group-hover:text-warning transition">
              Live Edge Camera Stream
            </h4>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Real-time webcam inference with persistent active privacy badges and frame rate throttling.
            </p>
          </div>
          <span className="inline-flex items-center text-xs text-warning font-medium mt-4 group-hover:translate-x-0.5 transition">
            Start Live Camera &rarr;
          </span>
        </Link>
      </div>
    </div>
  );
}
