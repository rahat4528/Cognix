'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, AlertCircle, Info, Sliders, Layers } from 'lucide-react';
import { ImageAsset, ClassificationResult, ExplainabilityResult } from '@/lib/types';
import { fetchImages, runClassification, runExplainability } from '@/lib/api';

export default function ClassificationStudio() {
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageAsset | null>(null);
  const [classResult, setClassResult] = useState<ClassificationResult | null>(null);
  const [camResult, setCamResult] = useState<ExplainabilityResult | null>(null);
  const [camAlpha, setCamAlpha] = useState<number>(0.5);
  const [loading, setLoading] = useState<boolean>(true);
  const [inferring, setInferring] = useState<boolean>(false);
  const [explaining, setExplaining] = useState<boolean>(false);

  useEffect(() => {
    fetchImages()
      .then((data) => {
        setImages(data);
        if (data.length > 0) {
          setSelectedImage(data[0]);
          executeClassification(data[0].id);
        }
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const executeClassification = async (imageId: string) => {
    setInferring(true);
    setCamResult(null);
    try {
      const res = await runClassification(imageId, 5);
      setClassResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setInferring(false);
    }
  };

  const executeGradCAM = async (targetClassId?: number) => {
    if (!selectedImage) return;
    setExplaining(true);
    try {
      const res = await runExplainability(selectedImage.id, targetClassId, camAlpha);
      setCamResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setExplaining(false);
    }
  };

  const handleSelectImage = (img: ImageAsset) => {
    setSelectedImage(img);
    executeClassification(img.id);
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Image Classification & Grad-CAM Explainability</h2>
        <p className="text-sm text-slate-400 mt-1">
          MobileNetV3 neural inference with full top-5 probability distribution and gradient-weighted class activation mapping.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading classification studio...</div>
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

          {/* Right Main Analysis Area */}
          <div className="lg:col-span-3 space-y-6">
            {selectedImage && classResult && (
              <>
                {/* Meta Header */}
                <div className="bg-surface border border-surfaceBorder rounded-xl px-5 py-3 flex items-center justify-between text-xs text-slate-300">
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold text-white">{selectedImage.original_name}</span>
                    <span className="text-slate-500">•</span>
                    <span>Architecture: {classResult.model_name}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span>
                      Latency: <strong className="text-accent">{classResult.latency_ms} ms</strong>
                    </span>
                    {classResult.is_uncertain && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Uncertain Prediction (&lt;20%)
                      </span>
                    )}
                  </div>
                </div>

                {/* Top Prediction & Distribution Card */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left: Input Image */}
                  <div className="bg-surface border border-surfaceBorder rounded-xl p-4 flex flex-col items-center justify-center">
                    <div className="w-full flex justify-between items-center text-xs text-slate-400 mb-2">
                      <span>Input Image</span>
                      <span>{selectedImage.width} × {selectedImage.height} px</span>
                    </div>
                    <img
                      src={selectedImage.image_url}
                      alt={selectedImage.original_name}
                      className="max-h-72 object-contain rounded-lg border border-surfaceBorder"
                    />
                  </div>

                  {/* Right: Softmax Distribution */}
                  <div className="bg-surface border border-surfaceBorder rounded-xl p-5 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between pb-3 border-b border-surfaceBorder">
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                          Top-5 Predictions
                        </span>
                        <span className="text-xs text-slate-400">Softmax Confidence</span>
                      </div>

                      <div className="mt-4 space-y-3">
                        {classResult.predictions.map((p, idx) => (
                          <div key={p.class_id} className="space-y-1">
                            <div className="flex justify-between text-xs">
                              <span className={`font-medium ${idx === 0 ? 'text-primary' : 'text-slate-300'}`}>
                                {idx + 1}. {p.label}
                              </span>
                              <span className="font-mono text-slate-400">{(p.score * 100).toFixed(2)}%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  idx === 0 ? 'bg-primary' : 'bg-slate-600'
                                }`}
                                style={{ width: `${Math.max(2, p.score * 100)}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="pt-4 border-t border-surfaceBorder flex justify-between items-center">
                      <button
                        onClick={() => executeGradCAM(classResult.predictions[0]?.class_id)}
                        disabled={explaining}
                        className="flex items-center space-x-1.5 px-4 py-2 bg-accent hover:bg-emerald-600 disabled:opacity-50 text-white rounded-lg text-xs font-medium transition shadow-md shadow-accent/20"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>{explaining ? 'Generating Grad-CAM...' : 'Generate Grad-CAM Saliency'}</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Grad-CAM Visual Explainability Display */}
                {camResult && (
                  <div className="bg-surface border border-accent/40 rounded-xl p-6 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-surfaceBorder pb-3">
                      <div>
                        <h4 className="text-sm font-semibold text-white flex items-center space-x-2">
                          <span>Visual Explainability (Grad-CAM Heatmap)</span>
                          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-accent/20 text-accent border border-accent/30">
                            Layer: features[-1]
                          </span>
                        </h4>
                        <div className="text-xs text-slate-400 mt-0.5">
                          Explaining Target: <strong>{camResult.target_label}</strong> (Confidence: {(camResult.confidence * 100).toFixed(1)}%)
                        </div>
                      </div>

                      {/* Transparency Slider */}
                      <div className="flex items-center space-x-3 text-xs text-slate-300">
                        <Sliders className="w-3.5 h-3.5 text-accent" />
                        <span>Alpha Blend:</span>
                        <input
                          type="range"
                          min="0.1"
                          max="0.9"
                          step="0.1"
                          value={camAlpha}
                          onChange={(e) => {
                            setCamAlpha(parseFloat(e.target.value));
                            executeGradCAM(camResult.target_class_id);
                          }}
                          className="w-28 h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-accent"
                        />
                        <span className="font-mono text-white font-semibold">{(camAlpha * 100).toFixed(0)}%</span>
                      </div>
                    </div>

                    {/* Disclaimer Alert */}
                    <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 flex items-start space-x-2.5 text-xs text-amber-300">
                      <Info className="w-4 h-4 shrink-0 mt-0.5 text-amber-400" />
                      <div>
                        <div className="font-semibold text-amber-200">Scientific Diagnostic Notice</div>
                        <div className="text-amber-300/80 mt-0.5 leading-relaxed">
                          {camResult.disclaimer}
                        </div>
                      </div>
                    </div>

                    {/* Heatmap Overlay Display */}
                    <div className="flex justify-center bg-black/50 p-3 rounded-lg">
                      <img
                        src={camResult.heatmap_data_url}
                        alt="Grad-CAM Saliency Overlay"
                        className="max-h-96 object-contain rounded-lg border border-surfaceBorder shadow-xl"
                      />
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
