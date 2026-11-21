'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  Layers,
  Flame,
  Heart,
  ShoppingCart,
  Eye,
  ArrowRight,
  TrendingUp,
  CheckCircle2,
  Info
} from 'lucide-react';
import { RecommendationItem, Item } from '@/lib/types';
import {
  fetchPersonalizedRecommendations,
  fetchCollaborativeRecommendations,
  fetchContentBasedRecommendations,
  fetchSequentialRecommendations,
  recordInteraction
} from '@/lib/api';

export default function StorefrontHome() {
  const [hybridRecs, setHybridRecs] = useState<RecommendationItem[]>([]);
  const [collabRecs, setCollabRecs] = useState<RecommendationItem[]>([]);
  const [contentRecs, setContentRecs] = useState<RecommendationItem[]>([]);
  const [seqRecs, setSeqRecs] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const sessionId = 'session_live_web';

  const loadAllRecommendations = () => {
    Promise.all([
      fetchPersonalizedRecommendations(8, sessionId),
      fetchCollaborativeRecommendations(6),
      fetchContentBasedRecommendations(6),
      fetchSequentialRecommendations(6)
    ])
      .then(([hyb, col, cnt, seq]) => {
        setHybridRecs(hyb);
        setCollabRecs(col);
        setContentRecs(cnt);
        setSeqRecs(seq);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAllRecommendations();
  }, []);

  const handleInteraction = async (
    item: Item,
    type: 'click' | 'favorite' | 'add_to_cart'
  ) => {
    try {
      await recordInteraction(item.id, type, sessionId);
      const actionLabels = {
        click: 'Browsed item',
        favorite: 'Added to favorites',
        add_to_cart: 'Added to cart'
      };
      setActionNotice(`${actionLabels[type]}: "${item.title}". Updating live model signals...`);
      setTimeout(() => setActionNotice(null), 3500);

      // Re-fetch recommendations to show real-time adaptation
      const updatedHybrid = await fetchPersonalizedRecommendations(8, sessionId);
      setHybridRecs(updatedHybrid);
      const updatedSeq = await fetchSequentialRecommendations(6);
      setSeqRecs(updatedSeq);
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-10">
      {/* Hero Banner */}
      <div className="relative rounded-2xl bg-gradient-to-r from-purple-900/60 via-slate-900/80 to-surface border border-purple-500/30 p-8 overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/20 text-primary border border-primary/40">
            <Sparkles className="w-3.5 h-3.5 mr-1.5" />
            Adaptive Multi-Signal Recommender
          </span>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Personal Discovery Storefront
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            Real-time recommendations powered by Matrix Factorization (SVD), TF-IDF Content Embeddings,
            and Markov Session Transitions. Interactions immediately update your personalized recommendations.
          </p>
          <div className="flex items-center space-x-4 pt-2">
            <Link
              href="/onboarding"
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-primary hover:bg-primaryHover text-white text-xs font-semibold transition shadow-lg shadow-primary/25"
            >
              <span>Cold-Start Quiz</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              href="/benchmarks"
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition border border-slate-700"
            >
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Offline Evaluation Benchmarks</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Real-time Interaction Toast */}
      {actionNotice && (
        <div className="bg-emerald-500/10 border border-emerald-500/40 text-emerald-300 text-xs px-4 py-2.5 rounded-xl flex items-center space-x-2 animate-bounce">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          <span>{actionNotice}</span>
        </div>
      )}

      {loading ? (
        <div className="p-16 text-center text-xs text-slate-500 animate-pulse">
          Computing latent factor affinities and session transitions...
        </div>
      ) : (
        <div className="space-y-10">
          {/* Row 1: Hybrid Ensemble Recommender */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  <span>Recommended For You (Hybrid AI Blending)</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Blends Collaborative SVD (45%), Content-Based TF-IDF (35%), and Session Markov Chains (20%).
                </p>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                {hybridRecs.length} Recommendations
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              {hybridRecs.map((rec) => (
                <div
                  key={rec.item.id}
                  className="bg-surface border border-surfaceBorder hover:border-primary/50 rounded-xl p-4 flex flex-col justify-between space-y-3 transition shadow-md group"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="uppercase font-semibold text-primary font-mono">
                        {rec.item.category}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono font-bold">
                        {(rec.score * 100).toFixed(0)}% match
                      </span>
                    </div>

                    <h4 className="text-xs font-bold text-white group-hover:text-primary transition line-clamp-2">
                      {rec.item.title}
                    </h4>

                    <div className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                      {rec.item.description}
                    </div>

                    {rec.model_contributions && (
                      <div className="pt-2 border-t border-surfaceBorder flex items-center space-x-1.5 text-[10px] text-slate-500">
                        <span>Weights:</span>
                        {Object.entries(rec.model_contributions).map(([k, v]) => (
                          <span key={k} className="font-mono text-slate-400">
                            {k}:{(v * 100).toFixed(0)}%
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="pt-3 border-t border-surfaceBorder flex items-center justify-between">
                    <span className="text-sm font-extrabold text-white">
                      ${rec.item.price.toFixed(2)}
                    </span>
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleInteraction(rec.item, 'favorite')}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-accent hover:bg-accent/10 transition"
                        title="Favorite"
                      >
                        <Heart className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleInteraction(rec.item, 'add_to_cart')}
                        className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-primary/20 hover:bg-primary text-primary hover:text-white border border-primary/30 text-xs font-semibold transition"
                        title="Add to Cart"
                      >
                        <ShoppingCart className="w-3.5 h-3.5" />
                        <span>Add</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Row 2: Pure Collaborative Filtering (Matrix Factorization) */}
          <div className="space-y-4 pt-6 border-t border-surfaceBorder">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-purple-400" />
                  <span>Collaborative Filtering (Latent Factor Affinities)</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Discovered by 20-dimensional Truncated SVD matrix decomposition over community interactions.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {collabRecs.map((rec) => (
                <div
                  key={rec.item.id}
                  className="bg-surface border border-surfaceBorder hover:border-purple-500/40 rounded-xl p-3 flex flex-col justify-between space-y-2 transition"
                >
                  <div className="space-y-1">
                    <span className="text-[9px] uppercase font-bold text-purple-400">
                      {rec.item.category}
                    </span>
                    <h5 className="text-xs font-semibold text-slate-200 line-clamp-2">
                      {rec.item.title}
                    </h5>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t border-surfaceBorder text-xs">
                    <span className="font-bold text-white">${rec.item.price.toFixed(2)}</span>
                    <button
                      onClick={() => handleInteraction(rec.item, 'click')}
                      className="p-1 rounded text-slate-400 hover:text-white"
                      title="Inspect"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Row 3: Session Transitions (Sequential Markov Chain) */}
          <div className="space-y-4 pt-6 border-t border-surfaceBorder">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <Flame className="w-4 h-4 text-warning" />
                  <span>Sequential Session Trending (Markov Next-Item Transitions)</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Predicts your next browsing intent based on sequential session transition probabilities.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {seqRecs.map((rec) => (
                <div
                  key={rec.item.id}
                  className="bg-surface border border-surfaceBorder hover:border-warning/40 rounded-xl p-3 flex flex-col justify-between space-y-2 transition"
                >
                  <div className="space-y-1">
                    <span className="text-[9px] uppercase font-bold text-warning">
                      {rec.item.category}
                    </span>
                    <h5 className="text-xs font-semibold text-slate-200 line-clamp-2">
                      {rec.item.title}
                    </h5>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t border-surfaceBorder text-xs">
                    <span className="font-bold text-white">${rec.item.price.toFixed(2)}</span>
                    <button
                      onClick={() => handleInteraction(rec.item, 'click')}
                      className="p-1 rounded text-slate-400 hover:text-white"
                      title="Inspect"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
