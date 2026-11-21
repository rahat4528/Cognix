'use client';

import React, { useState, useEffect } from 'react';
import { Search, ShoppingBag, Eye, Heart, ShoppingCart, Sparkles } from 'lucide-react';
import { Item, RecommendationItem } from '@/lib/types';
import { fetchCatalog, fetchSimilarItems, recordInteraction } from '@/lib/api';

const CATEGORIES = [
  'All',
  'Audio',
  'Computing',
  'Wearables',
  'Smart Office',
  'Photography',
  'Smart Home'
];

export default function CatalogExplorer() {
  const [items, setItems] = useState<Item[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [similarItems, setSimilarItems] = useState<RecommendationItem[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState<boolean>(false);

  useEffect(() => {
    setLoading(true);
    const cat = selectedCategory === 'All' ? undefined : selectedCategory;
    fetchCatalog(cat, searchQuery || undefined)
      .then(setItems)
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [selectedCategory, searchQuery]);

  const handleSelectItem = async (item: Item) => {
    setSelectedItem(item);
    setLoadingSimilar(true);
    recordInteraction(item.id, 'click').catch(() => {});
    try {
      const sim = await fetchSimilarItems(item.id, 4);
      setSimilarItems(sim);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSimilar(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Product Catalog Explorer</h2>
        <p className="text-sm text-slate-400 mt-1">
          Explore 100 enterprise catalog items with TF-IDF content similarity and category filters.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-surface border border-surfaceBorder rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                selectedCategory === cat
                  ? 'bg-primary text-white shadow-md shadow-primary/20'
                  : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-64">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search catalog..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Main Grid & Drawer Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Catalog Grid (2 columns on lg) */}
        <div className="lg:col-span-2">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-500">Loading catalog...</div>
          ) : items.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-500">No items match your criteria.</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {items.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleSelectItem(item)}
                  className={`bg-surface border rounded-xl p-4 flex flex-col justify-between space-y-3 cursor-pointer transition ${
                    selectedItem?.id === item.id
                      ? 'border-primary bg-primary/5 ring-1 ring-primary'
                      : 'border-surfaceBorder hover:border-slate-700'
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="font-mono text-primary font-bold uppercase">{item.category}</span>
                      <span className="text-amber-400 font-semibold font-mono">★ {item.rating.toFixed(1)}</span>
                    </div>
                    <h4 className="text-xs font-bold text-white line-clamp-2">{item.title}</h4>
                    <p className="text-[11px] text-slate-400 line-clamp-2">{item.description}</p>
                  </div>

                  <div className="pt-2 border-t border-surfaceBorder flex justify-between items-center text-xs">
                    <span className="font-extrabold text-white">${item.price.toFixed(2)}</span>
                    <span className="text-[10px] text-primary font-medium hover:underline">
                      View Details &rarr;
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Selected Item & Similar Items Panel */}
        <div className="lg:col-span-1">
          {selectedItem ? (
            <div className="bg-surface border border-surfaceBorder rounded-xl p-5 space-y-5 sticky top-24">
              <div className="space-y-2">
                <span className="text-[10px] font-mono uppercase font-bold text-primary">
                  {selectedItem.category}
                </span>
                <h3 className="text-base font-bold text-white">{selectedItem.title}</h3>
                <div className="text-xl font-extrabold text-white">${selectedItem.price.toFixed(2)}</div>
                <p className="text-xs text-slate-300 leading-relaxed">{selectedItem.description}</p>

                <div className="pt-2 flex flex-wrap gap-1">
                  {selectedItem.tags.split(' ').map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 text-[10px] font-mono"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Similar Items (TF-IDF Cosine Match) */}
              <div className="pt-4 border-t border-surfaceBorder space-y-3">
                <div className="flex items-center space-x-1.5 text-xs font-bold text-white">
                  <Sparkles className="w-3.5 h-3.5 text-primary" />
                  <span>Similar Items (Content TF-IDF)</span>
                </div>

                {loadingSimilar ? (
                  <div className="text-[11px] text-slate-500 py-3 text-center">Finding similar items...</div>
                ) : similarItems.length === 0 ? (
                  <div className="text-[11px] text-slate-500 py-2">No similar items found.</div>
                ) : (
                  <div className="space-y-2">
                    {similarItems.map((sim) => (
                      <div
                        key={sim.item.id}
                        onClick={() => handleSelectItem(sim.item)}
                        className="bg-slate-900/60 border border-slate-800 hover:border-primary/40 rounded-lg p-2.5 flex items-center justify-between cursor-pointer transition text-xs"
                      >
                        <div className="min-w-0 pr-2">
                          <div className="font-semibold text-slate-200 truncate">{sim.item.title}</div>
                          <div className="text-[10px] text-slate-400 mt-0.5">
                            ${sim.item.price.toFixed(2)} • {sim.item.category}
                          </div>
                        </div>
                        <span className="text-[10px] font-mono font-bold text-primary shrink-0">
                          {(sim.score * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-surface border border-surfaceBorder rounded-xl p-8 text-center text-xs text-slate-400 sticky top-24">
              Select an item from the catalog to view details and live TF-IDF content recommendations.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
