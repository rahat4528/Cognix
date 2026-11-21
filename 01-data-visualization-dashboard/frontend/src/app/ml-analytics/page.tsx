"use client";

import { useEffect, useState } from "react";
import { BrainCircuit, Activity, BarChart2, CheckCircle, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { MLExperiment, EvaluationMetrics } from "@/lib/types";
import EChartRenderer from "@/components/EChartRenderer";

export default function MLAnalyticsPage() {
  const [experiments, setExperiments] = useState<MLExperiment[]>([]);
  const [selectedExpId, setSelectedExpId] = useState<string>("");
  const [curvesData, setCurvesData] = useState<any>(null);
  const [evaluations, setEvaluations] = useState<EvaluationMetrics[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadExperiments();
  }, []);

  async function loadExperiments() {
    try {
      const wss = await api.listWorkspaces();
      if (wss[0]) {
        const list = await api.listMLExperiments(wss[0].id);
        setExperiments(list);
        if (list[0]) {
          handleSelectExperiment(list[0].id);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectExperiment(expId: string) {
    setSelectedExpId(expId);
    try {
      const curves = await api.getExperimentCurves(expId);
      setCurvesData(curves);
      const evals = await api.getExperimentEvaluation(expId);
      setEvaluations(evals);
    } catch (err) {
      console.error(err);
    }
  }

  // Format curves into chart format for ECharts
  let lossChartData: any[] = [];
  let accChartData: any[] = [];
  if (curvesData && curvesData.curves) {
    const runKey = Object.keys(curvesData.curves)[0];
    if (runKey) {
      const trainLoss = curvesData.curves[runKey]["train_loss"] || [];
      lossChartData = trainLoss.map((pt: any) => ({
        x: `Epoch ${pt.epoch || pt.step}`,
        val: pt.value,
      }));

      const trainAcc = curvesData.curves[runKey]["train_accuracy"] || [];
      accChartData = trainAcc.map((pt: any) => ({
        x: `Epoch ${pt.epoch || pt.step}`,
        val: pt.value,
      }));
    }
  }

  const activeEval = evaluations[0];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Machine Learning Analytics</h1>
          <p className="text-gray-400 text-xs mt-1">
            Visualize imported training curves and evaluate genuine scikit-learn calculated confusion matrices, ROC, and PR metrics.
          </p>
        </div>

        <span className="text-xs font-mono text-purple-400 bg-purple-500/10 border border-purple-500/20 px-3 py-1.5 rounded-lg flex items-center gap-2">
          <BrainCircuit className="w-3.5 h-3.5" />
          <span>Real ML Metrics • No Mocked Calculations</span>
        </span>
      </div>

      {/* Training & Validation Curves */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface rounded-xl border border-surfaceBorder p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Loss Convergence Curve</h3>
            <span className="text-[11px] text-gray-400 font-mono">label: imported metrics</span>
          </div>
          <EChartRenderer chartType="LINE" data={lossChartData} className="w-full h-72" />
        </div>

        <div className="bg-surface rounded-xl border border-surfaceBorder p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Accuracy Curve</h3>
            <span className="text-[11px] text-gray-400 font-mono">label: imported metrics</span>
          </div>
          <EChartRenderer chartType="LINE" data={accChartData} className="w-full h-72" />
        </div>
      </div>

      {/* Scikit-Learn Evaluation Metrics */}
      {activeEval && (
        <div className="bg-surface rounded-xl border border-surfaceBorder p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-surfaceBorder pb-4">
            <div>
              <h2 className="text-base font-bold text-white">Test Set Evaluation</h2>
              <span className="text-xs text-emerald-400 font-mono block mt-0.5">
                {activeEval.provenance_note}
              </span>
            </div>
            <span className="text-xs font-mono text-gray-400">Run: {activeEval.run_id}</span>
          </div>

          {/* Metric Tiles */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-surfaceBorder/20 p-4 rounded-xl border border-surfaceBorder">
              <span className="text-xs text-gray-400 uppercase tracking-wider block">Accuracy</span>
              <span className="text-2xl font-bold text-white mt-1 block">
                {(activeEval.accuracy * 100).toFixed(1)}%
              </span>
            </div>
            <div className="bg-surfaceBorder/20 p-4 rounded-xl border border-surfaceBorder">
              <span className="text-xs text-gray-400 uppercase tracking-wider block">Precision (Macro)</span>
              <span className="text-2xl font-bold text-blue-400 mt-1 block">
                {(activeEval.precision_macro * 100).toFixed(1)}%
              </span>
            </div>
            <div className="bg-surfaceBorder/20 p-4 rounded-xl border border-surfaceBorder">
              <span className="text-xs text-gray-400 uppercase tracking-wider block">Recall (Macro)</span>
              <span className="text-2xl font-bold text-cyan-400 mt-1 block">
                {(activeEval.recall_macro * 100).toFixed(1)}%
              </span>
            </div>
            <div className="bg-surfaceBorder/20 p-4 rounded-xl border border-surfaceBorder">
              <span className="text-xs text-gray-400 uppercase tracking-wider block">F1 Score</span>
              <span className="text-2xl font-bold text-purple-400 mt-1 block">
                {(activeEval.f1_macro * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Confusion Matrix Table */}
          {activeEval.confusion_matrix && (
            <div className="pt-4 border-t border-surfaceBorder">
              <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider mb-3">Confusion Matrix</h3>
              <div className="overflow-x-auto max-w-md">
                <table className="w-full text-center border-collapse border border-surfaceBorder text-xs font-mono">
                  <thead>
                    <tr className="bg-surfaceBorder/30 text-gray-400">
                      <th className="p-2 border border-surfaceBorder">Actual \ Pred</th>
                      {activeEval.confusion_matrix.labels.map((lbl) => (
                        <th key={lbl} className="p-2 border border-surfaceBorder">Pred {lbl}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {activeEval.confusion_matrix.matrix.map((row, rIdx) => (
                      <tr key={rIdx}>
                        <td className="p-2 bg-surfaceBorder/20 font-semibold text-gray-300 border border-surfaceBorder">
                          Actual {activeEval.confusion_matrix.labels[rIdx]}
                        </td>
                        {row.map((val, cIdx) => (
                          <td key={cIdx} className="p-2 border border-surfaceBorder text-white font-bold bg-surfaceBorder/10">
                            {val}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
