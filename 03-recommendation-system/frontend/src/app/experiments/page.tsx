'use client';

import React, { useState, useEffect } from 'react';
import { GitBranch, Activity, Eye, MousePointer, CheckCircle, RefreshCw } from 'lucide-react';
import { ABExperimentSummary } from '@/lib/types';
import { fetchExperimentSummary, recordExperimentEvent } from '@/lib/api';

export default function ExperimentsConsole() {
  const [experiment, setExperiment] = useState<ABExperimentSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [simulatedLog, setSimulatedLog] = useState<string | null>(null);

  const loadData = () => {
    fetchExperimentSummary()
      .then(setExperiment)
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const simulateImpression = async (variantId: string) => {
    try {
      await recordExperimentEvent('exp_homepage_algo', variantId, 'impression');
      setSimulatedLog(`Recorded impression for variant: ${variantId}`);
      loadData();
    } catch (e: any) {
      console.error(e);
    }
  };

  const simulateClick = async (variantId: string) => {
    try {
      await recordExperimentEvent('exp_homepage_algo', variantId, 'click');
      setSimulatedLog(`Recorded click conversion for variant: ${variantId}`);
      loadData();
    } catch (e: any) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">A/B Testing Experiments Console</h2>
        <p className="text-sm text-slate-400 mt-1">
          Online experimentation tracking Click-Through Rate (CTR) and Conversion Rate (CVR) across recommendation models.
        </p>
      </div>

      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500">Loading experimentation data...</div>
      ) : experiment ? (
        <div className="space-y-6">
          {/* Overview Card */}
          <div className="bg-surface border border-surfaceBorder rounded-2xl p-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-success animate-pulse" />
                <span className="text-xs font-bold uppercase tracking-wider text-success">Active Live Trial</span>
              </div>
              <h3 className="text-lg font-bold text-white mt-1">{experiment.name}</h3>
              <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {experiment.experiment_id}</p>
            </div>

            <button
              onClick={loadData}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition border border-slate-700"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Metrics</span>
            </button>
          </div>

          {/* Variants Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {experiment.variants.map((v) => (
              <div
                key={v.variant_id}
                className="bg-surface border border-surfaceBorder rounded-2xl p-5 flex flex-col justify-between space-y-4 shadow-lg"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{v.variant_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/10 text-primary border border-primary/30">
                      {v.traffic_pct}% traffic
                    </span>
                  </div>

                  <div className="pt-2 grid grid-cols-2 gap-3 text-xs">
                    <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px]">Impressions</div>
                      <div className="text-base font-bold text-white mt-0.5">{v.impressions}</div>
                    </div>
                    <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px]">Clicks</div>
                      <div className="text-base font-bold text-white mt-0.5">{v.clicks}</div>
                    </div>
                  </div>

                  <div className="pt-2 grid grid-cols-2 gap-3 text-xs">
                    <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px]">CTR</div>
                      <div className="text-lg font-extrabold text-primary mt-0.5">{v.ctr_pct}%</div>
                    </div>
                    <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                      <div className="text-slate-400 text-[10px]">Conversions</div>
                      <div className="text-lg font-extrabold text-success mt-0.5">{v.cvr_pct}%</div>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-surfaceBorder flex items-center space-x-2">
                  <button
                    onClick={() => simulateImpression(v.variant_id)}
                    className="flex-1 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-semibold transition"
                  >
                    + Impression
                  </button>
                  <button
                    onClick={() => simulateClick(v.variant_id)}
                    className="flex-1 py-1.5 rounded-lg bg-primary/20 hover:bg-primary text-primary hover:text-white border border-primary/30 text-[11px] font-semibold transition"
                  >
                    + Click
                  </button>
                </div>
              </div>
            ))}
          </div>

          {simulatedLog && (
            <div className="bg-slate-900 border border-slate-800 text-xs text-slate-300 p-3 rounded-xl">
              {simulatedLog}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
