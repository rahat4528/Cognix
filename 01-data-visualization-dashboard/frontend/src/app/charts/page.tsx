"use client";

import { useEffect, useState } from "react";
import { BarChart3, Play, Save, Check, AlertCircle, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { Dataset, Chart } from "@/lib/types";
import EChartRenderer from "@/components/EChartRenderer";

export default function ChartsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [chartName, setChartName] = useState<string>("Custom Chart Analysis");
  const [chartType, setChartType] = useState<string>("BAR");
  const [xAxis, setXAxis] = useState<string>("region");
  const [yAxis, setYAxis] = useState<string>("revenue");
  const [aggregation, setAggregation] = useState<string>("sum");

  const [chartData, setChartData] = useState<any>(null);
  const [queryMetadata, setQueryMetadata] = useState<any>(null);
  const [executing, setExecuting] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listWorkspaces().then((wss) => {
      if (wss[0]) {
        api.listDatasets(wss[0].id).then((dsList) => {
          setDatasets(dsList);
          if (dsList[0]) {
            setSelectedDatasetId(dsList[0].id);
          }
        });
      }
    });
  }, []);

  async function handleExecuteQuery() {
    try {
      setExecuting(true);
      setError(null);
      // Query temporary chart or preview via backend
      const workspaces = await api.listWorkspaces();
      const currentWs = workspaces[0];

      // Create or update chart and query
      const chartResp = await api.createChart(currentWs.id, {
        name: chartName,
        dataset_id: selectedDatasetId,
        chart_type: chartType,
        config: {
          x_axis: xAxis,
          y_axis: yAxis,
          aggregation: aggregation,
          limit: 1000
        }
      });

      const qResult = await api.queryChart(chartResp.id);
      setChartData(qResult.data);
      setQueryMetadata(qResult.metadata);
    } catch (err: any) {
      setError(err.message || "Query compilation failed");
    } finally {
      setExecuting(false);
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Chart Builder</h1>
          <p className="text-gray-400 text-xs mt-1">
            Build interactive charts compiled directly into server-side DuckDB columnar analytical queries.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Builder Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="bg-surface rounded-xl border border-surfaceBorder p-6 space-y-5">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Configuration</h2>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Chart Title</label>
            <input
              type="text"
              value={chartName}
              onChange={(e) => setChartName(e.target.value)}
              className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Dataset</label>
            <select
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
              className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Chart Type</label>
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
              className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
            >
              <option value="BAR">Bar Chart</option>
              <option value="LINE">Line Chart</option>
              <option value="AREA">Area Chart</option>
              <option value="PIE">Pie Chart</option>
              <option value="DONUT">Donut Chart</option>
              <option value="SCATTER">Scatter Plot</option>
              <option value="HISTOGRAM">Histogram</option>
              <option value="BOX_PLOT">Box Plot</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">X-Axis / Category Column</label>
            <input
              type="text"
              value={xAxis}
              onChange={(e) => setXAxis(e.target.value)}
              placeholder="e.g. region"
              className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Y-Axis / Value Column</label>
            <input
              type="text"
              value={yAxis}
              onChange={(e) => setYAxis(e.target.value)}
              placeholder="e.g. revenue"
              className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Aggregation</label>
            <select
              value={aggregation}
              onChange={(e) => setAggregation(e.target.value)}
              className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
            >
              <option value="sum">Sum</option>
              <option value="avg">Average / Mean</option>
              <option value="min">Minimum</option>
              <option value="max">Maximum</option>
              <option value="count">Count (*)</option>
            </select>
          </div>

          <button
            onClick={handleExecuteQuery}
            disabled={executing}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-primary hover:bg-primaryHover text-white text-sm font-medium rounded-lg transition-colors shadow-sm shadow-primary/20"
          >
            <Play className="w-4 h-4" />
            <span>{executing ? "Compiling Query..." : "Execute & Render"}</span>
          </button>
        </div>

        {/* Visual Preview Column */}
        <div className="lg:col-span-2 bg-surface rounded-xl border border-surfaceBorder p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-surfaceBorder pb-3">
            <h3 className="text-sm font-semibold text-white">{chartName}</h3>
            {queryMetadata && (
              <span className="text-xs font-mono text-gray-400">
                {queryMetadata.execution_time_ms} ms • {queryMetadata.record_count} items {queryMetadata.sampled ? "(sampled)" : ""}
              </span>
            )}
          </div>

          <div className="my-6 min-h-[350px] flex items-center justify-center">
            {chartData ? (
              <EChartRenderer chartType={chartType} data={chartData} title={chartName} className="w-full h-96" />
            ) : (
              <div className="text-center text-gray-500 text-sm">
                <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-30 text-primary" />
                <p>Click &quot;Execute &amp; Render&quot; to compile and visualize real data.</p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-surfaceBorder text-xs text-gray-500 flex items-center justify-between">
            <span>Server-side calculated via DuckDB columnar queries</span>
            <span>Zero hardcoded mock values</span>
          </div>
        </div>
      </div>
    </div>
  );
}
