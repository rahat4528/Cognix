'use client';

import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Layers, ArrowRight } from 'lucide-react';
import { ImageAsset, SimilaritySearchResponse } from '@/lib/types';
import { fetchImages, searchSimilarImages } from '@/lib/api';

export default function VisualSimilarityStudio() {
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageAsset | null>(null);
  const [searchResults, setSearchResults] = useState<SimilaritySearchResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [searching, setSearching] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchImages()
      .then((data) => {
        setImages(data);
        if (data.length > 0) {
          setSelectedImage(data[0]);
          executeSearch(data[0].id);
        }
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const executeSearch = async (imageId: string) => {
    setSearching(true);
    setError(null);
    try {
      const res = await searchSimilarImages(imageId, 8);
      setSearchResults(res);
    } catch (err: any) {
      setError(err.message || 'Similarity search failed.');
      setSearchResults(null);
    } finally {
      setSearching(false);
    }
  };

  const handleSelectImage = (img: ImageAsset) => {
    setSelectedImage(img);
    executeSearch(img.id);
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Visual Similarity Search</h2>
        <p className="text-sm text-slate-400 mt-1">
          Exact vector cosine similarity computed over 576-dimensional MobileNetV3 visual embeddings.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading similarity studio...</div>
      ) : images.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-500">No images available. Upload images first.</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Query Asset Picker */}
          <div className="lg:col-span-1 space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Select Query Image
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

          {/* Results Area */}
          <div className="lg:col-span-3 space-y-6">
            {selectedImage && (
              <div className="bg-surface border border-surfaceBorder rounded-xl p-5 flex items-center space-x-4">
                <img
                  src={selectedImage.thumbnail_url}
                  alt={selectedImage.original_name}
                  className="w-20 h-20 object-cover rounded-lg border border-primary ring-2 ring-primary/40"
                />
                <div>
                  <div className="text-xs font-semibold text-primary uppercase tracking-wider">
                    Query Reference Image
                  </div>
                  <div className="text-base font-bold text-white mt-0.5">{selectedImage.original_name}</div>
                  <div className="text-xs text-slate-400 mt-1">
                    Embedding: 576 normalized float features • Exact L2 normalized cosine distance
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs p-4 rounded-xl">
                {error}
              </div>
            )}

            {searching ? (
              <div className="text-center py-12 text-xs text-primary animate-pulse">
                Computing pairwise cosine dot-products across image embedding bank...
              </div>
            ) : searchResults && (
              <div className="space-y-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>
                    Top Matches (Ranked by Cosine Similarity): <strong>{searchResults.matches.length}</strong>
                  </span>
                  <span>Evaluated candidates: {searchResults.total_candidates}</span>
                </div>

                {searchResults.matches.length === 0 ? (
                  <div className="bg-surface border border-surfaceBorder rounded-xl p-8 text-center text-xs text-slate-400">
                    No other candidate images with embeddings found. Upload and classify additional images to search!
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {searchResults.matches.map((match, idx) => (
                      <div
                        key={match.image_id}
                        className="bg-surface border border-surfaceBorder hover:border-primary/40 rounded-xl p-4 space-y-3 transition"
                      >
                        <div className="relative rounded-lg overflow-hidden border border-surfaceBorder">
                          <img
                            src={match.thumbnail_url}
                            alt={match.original_name}
                            className="w-full h-36 object-cover"
                          />
                          <div className="absolute top-2 right-2 px-2 py-0.5 rounded-full text-[10px] font-bold bg-black/80 text-accent border border-accent/40 backdrop-blur-md">
                            {(match.similarity_score * 100).toFixed(1)}% match
                          </div>
                        </div>

                        <div>
                          <div className="text-xs font-semibold text-white truncate">{match.original_name}</div>
                          {match.top_label && (
                            <div className="text-[11px] text-slate-400 mt-0.5">
                              Class: <span className="text-slate-300">{match.top_label}</span>
                            </div>
                          )}
                        </div>

                        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-accent h-full rounded-full"
                            style={{ width: `${match.similarity_score * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
