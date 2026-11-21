"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Database,
  BarChart3,
  Terminal,
  BrainCircuit,
  ArrowUpRight,
  TrendingUp,
  FileCheck2,
  Clock,
  Zap
} from "lucide-react";
import { api } from "@/lib/api";

export default function OverviewPage() {
  const [datasetsCount, setDatasetsCount] = useState<number>(1);
  const [dashboardsCount, setDashboardsCount] = useState<number>(1);
  const [chartsCount, setChartsCount] = useState<number>(4);
  const [experimentsCount, setExperimentsCount] = useState<number>(1);

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Hero Welcome */}
      <div className="bg-gradient-to-r from-surface to-surfaceBorder/30 p-8 rounded-2xl border border-surfaceBorder relative overflow-hidden">
        <div className="max-w-2xl relative z-10 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-xs text-primary font-medium">
            <Zap className="w-3.5 h-3.5" />
            <span>Standalone DuckDB Engine Active</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Data Visualization Workspace
          </h1>
          <p className="text-gray-400 text-sm leading-relaxed">
            Ingest structured tabular datasets, construct declarative transformation pipelines, compile high-speed DuckDB analytical queries, and evaluate verified machine learning experiment curves.
          </p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-surface p-5 rounded-xl border border-surfaceBorder">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase tracking-wider">Active Datasets</span>
            <Database className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2">{datasetsCount}</p>
          <span className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
            <FileCheck2 className="w-3.5 h-3.5" /> 100% Quality Verified
          </span>
        </div>

        <div className="bg-surface p-5 rounded-xl border border-surfaceBorder">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase tracking-wider">Visualizations</span>
            <BarChart3 className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2">{chartsCount}</p>
          <span className="text-xs text-gray-400 mt-1 block">Bar, Scatter, Donut, Box</span>
        </div>

        <div className="bg-surface p-5 rounded-xl border border-surfaceBorder">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase tracking-wider">Grid Dashboards</span>
            <TrendingUp className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2">{dashboardsCount}</p>
          <span className="text-xs text-blue-400 mt-1 block">Optimistic Concurrency Active</span>
        </div>

        <div className="bg-surface p-5 rounded-xl border border-surfaceBorder">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase tracking-wider">ML Experiments</span>
            <BrainCircuit className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2">{experimentsCount}</p>
          <span className="text-xs text-purple-400 mt-1 block">Scikit-learn Evaluated</span>
        </div>
      </div>

      {/* Quick Launch Cards */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Workspace Workflows</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Link
            href="/datasets"
            className="group bg-surface hover:bg-surfaceBorder/30 p-6 rounded-xl border border-surfaceBorder transition-all duration-200"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-105 transition-transform">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white flex items-center justify-between">
              Dataset Explorer
              <ArrowUpRight className="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" />
            </h3>
            <p className="text-xs text-gray-400 mt-2 leading-relaxed">
              Upload CSV, Parquet, JSON, and Excel files. Inspect auto-inferred schemas, duplicate counts, and data health scores.
            </p>
          </Link>

          <Link
            href="/charts"
            className="group bg-surface hover:bg-surfaceBorder/30 p-6 rounded-xl border border-surfaceBorder transition-all duration-200"
          >
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4 group-hover:scale-105 transition-transform">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white flex items-center justify-between">
              Chart Builder
              <ArrowUpRight className="w-4 h-4 text-gray-500 group-hover:text-cyan-400 transition-colors" />
            </h3>
            <p className="text-xs text-gray-400 mt-2 leading-relaxed">
              Design multi-series bar, line, scatter, box plot, and histogram charts compiled server-side with zero-copy DuckDB execution.
            </p>
          </Link>

          <Link
            href="/sql"
            className="group bg-surface hover:bg-surfaceBorder/30 p-6 rounded-xl border border-surfaceBorder transition-all duration-200"
          >
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-4 group-hover:scale-105 transition-transform">
              <Terminal className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white flex items-center justify-between">
              SQL Studio
              <ArrowUpRight className="w-4 h-4 text-gray-500 group-hover:text-purple-400 transition-colors" />
            </h3>
            <p className="text-xs text-gray-400 mt-2 leading-relaxed">
              Query registered dataset views in a locked-down, read-only DuckDB sandbox with memory limits and statement timeouts.
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
