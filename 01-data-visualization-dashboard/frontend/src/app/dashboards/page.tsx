"use client";

import { useEffect, useState } from "react";
import { LayoutDashboard, Share2, Plus, Check, Copy } from "lucide-react";
import { api } from "@/lib/api";
import { Dashboard } from "@/lib/types";
import EChartRenderer from "@/components/EChartRenderer";

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [activeDashboard, setActiveDashboard] = useState<Dashboard | null>(null);
  const [chartDataMap, setChartDataMap] = useState<Record<string, any>>({});
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    loadDashboards();
  }, []);

  async function loadDashboards() {
    try {
      const wss = await api.listWorkspaces();
      if (wss[0]) {
        const list = await api.listDashboards(wss[0].id);
        setDashboards(list);
        if (list[0]) {
          handleSelectDashboard(list[0]);
        }
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function handleSelectDashboard(d: Dashboard) {
    setActiveDashboard(d);
    // Fetch query results for all charts on this dashboard
    const map: Record<string, any> = {};
    for (const item of d.charts) {
      try {
        const qRes = await api.queryChart(item.chart_id);
        map[item.chart_id] = qRes.data;
      } catch (err) {
        console.error(err);
      }
    }
    setChartDataMap(map);
  }

  async function handleShare() {
    if (!activeDashboard) return;
    try {
      const res = await api.shareDashboard(activeDashboard.id);
      const fullUrl = `${window.location.origin}${res.share_url}`;
      setShareUrl(fullUrl);
    } catch (err) {
      console.error(err);
    }
  }

  function copyShareLink() {
    if (!shareUrl) return;
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Grid Dashboards</h1>
          <p className="text-gray-400 text-xs mt-1">
            Dynamic grid layouts with scoped filters, optimistic concurrency versioning, and revocable public share links.
          </p>
        </div>

        <button
          onClick={handleShare}
          className="flex items-center gap-2 px-4 py-2 bg-surfaceBorder hover:bg-surfaceBorder/80 text-white text-sm font-medium rounded-lg transition-colors border border-surfaceBorder"
        >
          <Share2 className="w-4 h-4 text-cyan-400" />
          <span>Generate Share Link</span>
        </button>
      </div>

      {shareUrl && (
        <div className="p-4 bg-surface rounded-xl border border-primary/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs uppercase font-semibold text-primary">Public Token Link:</span>
            <span className="text-xs font-mono text-gray-300">{shareUrl}</span>
          </div>
          <button
            onClick={copyShareLink}
            className="flex items-center gap-1.5 px-3 py-1 bg-primary text-white text-xs font-medium rounded-md"
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
        </div>
      )}

      {/* Active Dashboard Grid */}
      {activeDashboard && (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-surface p-4 rounded-xl border border-surfaceBorder">
            <div>
              <h2 className="text-lg font-bold text-white">{activeDashboard.title}</h2>
              <p className="text-xs text-gray-400 mt-0.5">{activeDashboard.description}</p>
            </div>
            <span className="text-xs font-mono text-gray-400 bg-surfaceBorder/50 px-2.5 py-1 rounded">
              v{activeDashboard.version} (Concurrency Guarded)
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {activeDashboard.charts.map((c) => (
              <div key={c.chart_id} className="bg-surface rounded-xl border border-surfaceBorder p-5">
                <h3 className="text-sm font-semibold text-gray-200 mb-3">{c.chart_name || "Chart"}</h3>
                <div className="min-h-[280px]">
                  {chartDataMap[c.chart_id] ? (
                    <EChartRenderer
                      chartType={c.chart_type || "BAR"}
                      data={chartDataMap[c.chart_id]}
                      className="w-full h-72"
                    />
                  ) : (
                    <div className="h-72 flex items-center justify-center text-xs text-gray-500">
                      Loading chart...
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
