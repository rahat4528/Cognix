"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { LayoutDashboard, Download, Check, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { Dashboard } from "@/lib/types";
import EChartRenderer from "@/components/EChartRenderer";

export default function PublicDashboardPage() {
  const params = useParams();
  const token = params?.token as string;
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [chartDataMap, setChartDataMap] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      loadPublicDashboard(token);
    }
  }, [token]);

  async function loadPublicDashboard(tok: string) {
    try {
      setLoading(true);
      const dash = await api.getPublicDashboard(tok);
      setDashboard(dash);

      const map: Record<string, any> = {};
      for (const item of dash.charts) {
        try {
          const qRes = await api.queryChart(item.chart_id);
          map[item.chart_id] = qRes.data;
        } catch (err) {
          console.error(err);
        }
      }
      setChartDataMap(map);
    } catch (err: any) {
      setError(err.message || "Failed to load public dashboard");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center text-gray-400">
        Loading public dashboard...
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center text-red-400">
        {error || "Dashboard not found or link expired"}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8 space-y-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <header className="flex items-center justify-between border-b border-surfaceBorder pb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">{dashboard.title}</h1>
              <p className="text-xs text-gray-400 mt-0.5">{dashboard.description}</p>
            </div>
          </div>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-full">
            Read-Only Public View
          </span>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {dashboard.charts.map((c) => (
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
                    Loading data...
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
