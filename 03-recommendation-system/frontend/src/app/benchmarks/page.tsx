'use client';

import React, { useState, useEffect } from 'react';
import { BarChart2, TrendingUp, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { BenchmarkReport } from '@/lib/types';
import { fetchBenchmarks } from '@/lib/api';

export default function BenchmarksStudio() {
  const [report, setReport] = useState<BenchmarkReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchBenchmarks()
      .then(setReport)
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Model Evaluation & Temporal Splits Studio</h2>
        <p className="text-sm text-slate-400 mt-1">
          Strict offline benchmark evaluations partitioned temporally to prevent data leakage.
        </p>
      </div>

      {/* Temporal Split Diagram */}
      <div className="bg-surface border border-surfaceBorder rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-success" />
            <span className="text-sm font-bold text-white">Temporal Partitioning Architecture (Zero Leakage)</span>
          </div>
          <span className="text-xs text-slate-400 font-mono">Chronological Progression</span>
        </div>

        <div className="grid grid-cols-12 gap-2 text-center text-xs font-semibold py-2">
          <div className="col-span-7 bg-primary/20 border border-primary/40 text-primary py-4 rounded-xl">
            <div>Training Partition (60%)</div>
            <div className="text-[10px] text-slate-400 font-mono mt-1">Earliest events (t &lt; T₁)</div>
          </div>
          <div className="col-span-2 bg-purple-500/20 border border-purple-500/40 text-purple-300 py-4 rounded-xl">
            <div>Validation (20%)</div>
            <div className="text-[10px] text-slate-400 font-mono mt-1">T₁ ≤ t &lt; T₂</div>
          </div>
          <div className="col-span-3 bg-accent/20 border border-accent/40 text-accent py-4 rounded-xl">
            <div>Test Holdout (20%)</div>
            <div className="text-[10px] text-slate-400 font-mono mt-1">Latest events (t ≥ T₂)</div>
          </div>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed">
          Standard random train/test splits cause severe optimistic bias in recommendation engines because future user interactions leak into past user profiles. Cognix strictly enforces chronological ordering: models are trained only on historical events and evaluated against unobserved future test events.
        </p>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500">Loading benchmark evaluation matrix...</div>
      ) : report ? (
        <div className="space-y-6">
          {/* Metrics Table */}
          <div className="bg-surface border border-surfaceBorder rounded-2xl overflow-hidden shadow-lg">
            <div className="px-6 py-4 border-b border-surfaceBorder flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Offline Model Performance Comparison (K=10)</h3>
              <span className="text-xs text-slate-400 font-mono">
                Evaluated Users: {report.dataset_metadata.test_eval_users}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/60 text-slate-400 border-b border-surfaceBorder">
                  <tr>
                    <th className="px-6 py-3 font-semibold">Algorithm Paradigm</th>
                    <th className="px-6 py-3 font-semibold">NDCG@10</th>
                    <th className="px-6 py-3 font-semibold">Recall@10</th>
                    <th className="px-6 py-3 font-semibold">Precision@10</th>
                    <th className="px-6 py-3 font-semibold">MAP@10</th>
                    <th className="px-6 py-3 font-semibold">Catalog Coverage</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surfaceBorder">
                  {Object.entries(report.benchmarks).map(([algo, metrics]) => {
                    const isHybrid = algo.toLowerCase().includes('hybrid');
                    return (
                      <tr
                        key={algo}
                        className={`transition ${
                          isHybrid ? 'bg-primary/5 font-semibold text-white' : 'hover:bg-slate-900/40 text-slate-300'
                        }`}
                      >
                        <td className="px-6 py-3.5 flex items-center space-x-2">
                          {isHybrid && <span className="w-2 h-2 rounded-full bg-primary" />}
                          <span>{algo}</span>
                        </td>
                        <td className="px-6 py-3.5 font-mono text-primary font-bold">
                          {metrics['ndcg@10'].toFixed(4)}
                        </td>
                        <td className="px-6 py-3.5 font-mono">
                          {metrics['recall@10'].toFixed(4)}
                        </td>
                        <td className="px-6 py-3.5 font-mono">
                          {metrics['precision@10'].toFixed(4)}
                        </td>
                        <td className="px-6 py-3.5 font-mono">
                          {metrics['map@10'].toFixed(4)}
                        </td>
                        <td className="px-6 py-3.5 font-mono text-success font-semibold">
                          {(metrics['catalog_coverage'] * 100).toFixed(1)}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* NDCG Comparison Bar Visualizer */}
          <div className="bg-surface border border-surfaceBorder rounded-2xl p-6 space-y-4">
            <h4 className="text-sm font-bold text-white">NDCG@10 Ranking Accuracy Comparison</h4>
            <div className="space-y-3 pt-2">
              {Object.entries(report.benchmarks).map(([algo, metrics]) => (
                <div key={algo} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold text-slate-300">{algo}</span>
                    <span className="font-mono text-primary font-bold">{metrics['ndcg@10'].toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-primary h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, metrics['ndcg@10'] * 350)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
