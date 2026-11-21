'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, ShieldCheck, FileText } from 'lucide-react';
import { CVModelInfo } from '@/lib/types';
import { fetchModels } from '@/lib/api';

export default function ModelsRegistry() {
  const [models, setModels] = useState<CVModelInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchModels()
      .then(setModels)
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Model Registry & Architecture Cards</h2>
        <p className="text-sm text-slate-400 mt-1">
          Reproducible deep learning model specifications, parameter counts, input dimensions, and open-source licenses.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-500">Loading model registry...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {models.map((m) => (
            <div
              key={m.id}
              className="bg-surface border border-surfaceBorder rounded-xl p-6 flex flex-col justify-between space-y-4 shadow-lg"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="w-9 h-9 rounded-lg bg-primary/20 text-primary flex items-center justify-center">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                    {m.license}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-white">{m.name}</h3>
                  <p className="text-xs text-primary font-medium mt-0.5">{m.task}</p>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed">{m.purpose}</p>

                <div className="pt-3 border-t border-surfaceBorder space-y-2 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Framework:</span>
                    <span className="font-mono text-slate-200">{m.framework}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Input Resolution:</span>
                    <span className="font-mono text-slate-200">{m.input_resolution}</span>
                  </div>
                  {m.parameters_millions && (
                    <div className="flex justify-between text-slate-400">
                      <span>Parameters:</span>
                      <span className="font-mono text-slate-200">{m.parameters_millions}M</span>
                    </div>
                  )}
                  {m.embedding_dimension && (
                    <div className="flex justify-between text-slate-400">
                      <span>Embedding Dim:</span>
                      <span className="font-mono text-slate-200">{m.embedding_dimension} float32</span>
                    </div>
                  )}
                  {m.num_classes && (
                    <div className="flex justify-between text-slate-400">
                      <span>Categories:</span>
                      <span className="font-mono text-slate-200">{m.num_classes} classes</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="pt-3 border-t border-surfaceBorder flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center space-x-1 text-emerald-400">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Verified Weights</span>
                </span>
                <span className="font-mono">weights_only=True</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
