'use client';

import React, { useState, useEffect } from 'react';
import { UploadCloud, CheckCircle2, AlertTriangle, Trash2, Shield, FileCheck } from 'lucide-react';
import { ImageAsset } from '@/lib/types';
import { fetchImages, uploadImage, deleteImage } from '@/lib/api';

export default function UploadStudio() {
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<boolean>(false);

  const loadData = () => {
    fetchImages()
      .then(setImages)
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setErrorMessage(null);

    try {
      for (let i = 0; i < files.length; i++) {
        await uploadImage(files[i]);
      }
      loadData();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to upload image.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (imageId: string) => {
    if (!confirm('Permanently delete this image and all its analyses?')) return;
    try {
      await deleteImage(imageId);
      setImages(prev => prev.filter(img => img.id !== imageId));
    } catch (err: any) {
      alert('Delete failed: ' + err.message);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Image Ingestion & Sanitization Studio</h2>
        <p className="text-sm text-slate-400 mt-1">
          Secure, authenticated upload pipeline with automated EXIF stripping and decompression bomb protection.
        </p>
      </div>

      {/* Privacy & Safeguard Banner */}
      <div className="bg-surface border border-surfaceBorder rounded-xl p-4 flex items-start space-x-3 text-xs text-slate-300">
        <Shield className="w-5 h-5 text-accent shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-semibold text-white">Privacy Safeguard & Data Hygiene Policies</div>
          <div className="text-slate-400 leading-relaxed">
            Every uploaded asset is strictly sanitized: EXIF metadata (GPS location, device IDs, timestamps) is stripped.
            Decompression bombs are mitigated with a 25-megapixel limit. Deletions cascade to immediately destroy all raw bytes,
            thumbnails, and derived feature vectors.
          </div>
        </div>
      </div>

      {/* Drag & Drop Area */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFileUpload(e.dataTransfer.files);
        }}
        className={`border-2 border-dashed rounded-xl p-10 text-center transition flex flex-col items-center justify-center space-y-3 cursor-pointer ${
          dragOver ? 'border-primary bg-primary/10' : 'border-surfaceBorder bg-surface hover:border-slate-700'
        }`}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          className="hidden"
          onChange={(e) => handleFileUpload(e.target.files)}
        />
        <div className="w-12 h-12 rounded-full bg-primary/20 text-primary flex items-center justify-center shadow-lg shadow-primary/20">
          <UploadCloud className="w-6 h-6" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">
            {uploading ? 'Sanitizing and uploading image...' : 'Click or drag images to upload'}
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Supported formats: JPEG, PNG, WebP (Max 25 MB, up to 25 Megapixels)
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs p-3 rounded-lg flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Ingested Assets Table */}
      <div className="bg-surface border border-surfaceBorder rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-surfaceBorder flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Ingested Asset Library ({images.length})</h3>
          <span className="text-xs text-slate-400">Authenticated User Assets</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading library...</div>
        ) : images.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">No images ingested yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 border-b border-surfaceBorder">
                <tr>
                  <th className="px-6 py-3">Preview</th>
                  <th className="px-6 py-3">File Name</th>
                  <th className="px-6 py-3">Resolution</th>
                  <th className="px-6 py-3">Size</th>
                  <th className="px-6 py-3">Perceptual Hash (dHash)</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surfaceBorder">
                {images.map((img) => (
                  <tr key={img.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-6 py-3">
                      <img
                        src={img.thumbnail_url}
                        alt={img.original_name}
                        className="w-12 h-12 object-cover rounded-lg border border-surfaceBorder"
                      />
                    </td>
                    <td className="px-6 py-3">
                      <div className="font-medium text-white truncate max-w-xs">{img.original_name}</div>
                      <div className="text-[10px] text-slate-500 font-mono">{img.id}</div>
                    </td>
                    <td className="px-6 py-3 text-slate-300 font-mono">
                      {img.width} × {img.height}
                    </td>
                    <td className="px-6 py-3 text-slate-300">
                      {(img.file_size_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-6 py-3 font-mono text-[11px] text-slate-400">
                      {img.perceptual_hash}
                    </td>
                    <td className="px-6 py-3 text-right">
                      <button
                        onClick={() => handleDelete(img.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition"
                        title="Cascading Privacy Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
