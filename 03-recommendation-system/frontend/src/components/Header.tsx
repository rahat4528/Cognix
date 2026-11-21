'use client';

import React from 'react';
import { ShoppingCart, User, Activity } from 'lucide-react';

export default function Header() {
  return (
    <header className="h-16 bg-surface/80 backdrop-blur-md border-b border-surfaceBorder px-8 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <h1 className="text-base font-semibold text-slate-200">
          Personal Discovery & Recommendation Engine
        </h1>
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-400 mr-1.5 animate-pulse" />
          Multi-Model Ensemble Active
        </span>
      </div>

      <div className="flex items-center space-x-4">
        <div className="text-xs text-slate-400 flex items-center space-x-1.5 bg-slate-900/60 px-3 py-1.5 rounded-full border border-slate-800">
          <Activity className="w-3.5 h-3.5 text-primary" />
          <span>SVD + TF-IDF + Markov</span>
        </div>

        <div className="flex items-center space-x-2 border-l border-slate-800 pl-4">
          <div className="w-7 h-7 rounded-full bg-primary/20 text-primary border border-primary/40 flex items-center justify-center font-bold text-xs">
            S
          </div>
          <span className="text-xs font-medium text-slate-300">shopper@cognix.local</span>
        </div>
      </div>
    </header>
  );
}
