"use client";

import { useEffect, useState } from "react";
import {
  Database,
  Upload,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Search,
  Filter,
  Eye,
  Trash2
} from "lucide-react";
import { api } from "@/lib/api";
import { Dataset } from "@/lib/types";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [previewRows, setPreviewRows] = useState<any[]>([]);
  const [previewCols, setPreviewCols] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const workspaceId = "enterprise-analytics-ml"; // default seed workspace slug/id

  useEffect(() => {
    loadDatasets();
  }, []);

  async function loadDatasets() {
    try {
      setLoading(true);
      const workspaces = await api.listWorkspaces();
      const currentWs = workspaces[0];
      if (currentWs) {
        const list = await api.listDatasets(currentWs.id);
        setDatasets(list);
        if (list.length > 0) {
          handleSelectDataset(list[0]);
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to load datasets");
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectDataset(ds: Dataset) {
    try {
      setSelectedDataset(ds);
      const preview = await api.previewDataset(ds.id, 1, 25);
      setPreviewCols(preview.columns);
      setPreviewRows(preview.rows);
    } catch (err: any) {
      console.error(err);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError(null);
      const workspaces = await api.listWorkspaces();
      const currentWs = workspaces[0];
      
      const formData = new FormData();
      formData.append("file", file);
      formData.append("name", file.name.replace(/\.[^/.]+$/, ""));

      await api.uploadDataset(currentWs.id, formData);
      await loadDatasets();
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Dataset Explorer</h1>
          <p className="text-gray-400 text-xs mt-1">Inspect schemas, data quality metrics, and preview row partitions.</p>
        </div>

        <label className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primaryHover text-white text-sm font-medium rounded-lg cursor-pointer transition-colors shadow-sm shadow-primary/20">
          <Upload className="w-4 h-4" />
          <span>{uploading ? "Ingesting..." : "Upload Dataset"}</span>
          <input
            type="file"
            accept=".csv,.parquet,.json,.xlsx"
            className="hidden"
            onChange={handleFileUpload}
            disabled={uploading}
          />
        </label>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Datasets List */}
        <div className="bg-surface rounded-xl border border-surfaceBorder p-5 space-y-3">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Available Datasets</h2>
          <div className="space-y-2">
            {datasets.map((ds) => {
              const isSelected = selectedDataset?.id === ds.id;
              const quality = ds.latest_version?.quality_score ?? 100;
              return (
                <div
                  key={ds.id}
                  onClick={() => handleSelectDataset(ds)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-surfaceBorder/50 border-primary text-white"
                      : "bg-surfaceBorder/20 border-surfaceBorder text-gray-300 hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-sm text-white">{ds.name}</h3>
                      <span className="text-[11px] text-gray-400 mt-0.5 block">
                        Format: <span className="uppercase font-mono">{ds.latest_version?.file_format}</span> • {ds.latest_version?.row_count} rows
                      </span>
                    </div>
                    <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono font-medium">
                      Q: {quality}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Selected Dataset Detail & Quality Summary */}
        <div className="lg:col-span-2 space-y-6">
          {selectedDataset && selectedDataset.latest_version && (
            <>
              {/* Quality & Schema Summary Card */}
              <div className="bg-surface rounded-xl border border-surfaceBorder p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-surfaceBorder pb-4">
                  <div>
                    <h2 className="text-lg font-bold text-white">{selectedDataset.name}</h2>
                    <p className="text-xs text-gray-400 mt-0.5">{selectedDataset.description || "No description provided."}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-400 block">SHA-256 Checksum</span>
                    <span className="text-[10px] font-mono text-gray-500 block truncate max-w-[200px]">
                      {selectedDataset.latest_version.checksum_sha256}
                    </span>
                  </div>
                </div>

                {/* Quality Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
                  <div className="bg-surfaceBorder/20 p-3 rounded-lg border border-surfaceBorder">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Completeness</span>
                    <span className="text-lg font-bold text-emerald-400 mt-1 block">
                      {selectedDataset.latest_version.quality_report?.completeness_score ?? 100}%
                    </span>
                  </div>
                  <div className="bg-surfaceBorder/20 p-3 rounded-lg border border-surfaceBorder">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Uniqueness</span>
                    <span className="text-lg font-bold text-blue-400 mt-1 block">
                      {selectedDataset.latest_version.quality_report?.uniqueness_score ?? 100}%
                    </span>
                  </div>
                  <div className="bg-surfaceBorder/20 p-3 rounded-lg border border-surfaceBorder">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Columns</span>
                    <span className="text-lg font-bold text-white mt-1 block">
                      {selectedDataset.latest_version.column_count}
                    </span>
                  </div>
                  <div className="bg-surfaceBorder/20 p-3 rounded-lg border border-surfaceBorder">
                    <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Total Rows</span>
                    <span className="text-lg font-bold text-white mt-1 block">
                      {selectedDataset.latest_version.row_count}
                    </span>
                  </div>
                </div>
              </div>

              {/* Data Preview Table */}
              <div className="bg-surface rounded-xl border border-surfaceBorder overflow-hidden">
                <div className="px-6 py-4 border-b border-surfaceBorder flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white">Data Sample Preview</h3>
                  <span className="text-xs text-gray-400">Showing first 25 rows</span>
                </div>
                <div className="overflow-x-auto max-h-96">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-surfaceBorder/30 text-gray-300 font-semibold sticky top-0">
                      <tr>
                        {previewCols.map((c) => (
                          <th key={c} className="px-4 py-2.5 border-b border-surfaceBorder whitespace-nowrap">
                            {c}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-surfaceBorder/50 text-gray-300">
                      {previewRows.map((row, idx) => (
                        <tr key={idx} className="hover:bg-surfaceBorder/20 transition-colors">
                          {previewCols.map((c) => (
                            <td key={c} className="px-4 py-2 whitespace-nowrap font-mono text-[11px]">
                              {row[c] !== null && row[c] !== undefined ? String(row[c]) : <span className="text-gray-600">NULL</span>}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
