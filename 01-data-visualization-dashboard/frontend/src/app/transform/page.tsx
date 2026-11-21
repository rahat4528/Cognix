"use client";

import { useEffect, useState } from "react";
import { SlidersHorizontal, Plus, Play, Check, AlertCircle, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import { Dataset } from "@/lib/types";

export default function TransformationsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [opType, setOpType] = useState<string>("filter");
  const [column, setColumn] = useState<string>("");
  const [operator, setOperator] = useState<string>(">");
  const [value, setValue] = useState<string>("");
  const [newColumn, setNewColumn] = useState<string>("");
  const [expression, setExpression] = useState<string>("");

  const [previewRows, setPreviewRows] = useState<any[]>([]);
  const [previewCols, setPreviewCols] = useState<string[]>([]);
  const [isApplying, setIsApplying] = useState<boolean>(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

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

  async function handlePreview() {
    try {
      setErrorMsg(null);
      setSuccessMsg(null);
      const step: any = { op: opType, params: {} };
      if (opType === "filter") {
        step.params = { column, operator, value };
      } else if (opType === "derive_column") {
        step.params = { new_column: newColumn, expression };
      } else if (opType === "fill_missing") {
        step.params = { column, strategy: "mean" };
      } else if (opType === "deduplicate") {
        step.params = {};
      }

      const res = await api.previewTransformation(selectedDatasetId, [step]);
      setPreviewCols(res.columns);
      setPreviewRows(res.rows);
    } catch (err: any) {
      setErrorMsg(err.message || "Transformation preview failed");
    }
  }

  async function handleApply() {
    try {
      setIsApplying(true);
      setErrorMsg(null);
      const step: any = { op: opType, params: {} };
      if (opType === "filter") {
        step.params = { column, operator, value };
      } else if (opType === "derive_column") {
        step.params = { new_column: newColumn, expression };
      } else if (opType === "fill_missing") {
        step.params = { column, strategy: "mean" };
      } else if (opType === "deduplicate") {
        step.params = {};
      }

      const res = await api.applyTransformation(
        selectedDatasetId,
        [step],
        `Applied ${opType} step via Studio`
      );
      setSuccessMsg(`Transformation committed! Created Dataset Version v${res.new_version.version_number}`);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to commit transformation");
    } finally {
      setIsApplying(false);
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Transformation Studio</h1>
        <p className="text-gray-400 text-xs mt-1">
          Apply declarative transformations (filtering, safe mathematical derived columns, deduplication) producing new immutable dataset versions.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 text-sm flex items-center gap-3">
          <Check className="w-5 h-5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Transformation Configuration Box */}
      <div className="bg-surface rounded-xl border border-surfaceBorder p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div>
            <label className="block text-xs font-medium text-gray-300 uppercase tracking-wider mb-2">Target Dataset</label>
            <select
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
              className="w-full bg-surfaceBorder/40 border border-surfaceBorder rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-primary"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 uppercase tracking-wider mb-2">Operation Type</label>
            <select
              value={opType}
              onChange={(e) => setOpType(e.target.value)}
              className="w-full bg-surfaceBorder/40 border border-surfaceBorder rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-primary"
            >
              <option value="filter">Filter Rows</option>
              <option value="derive_column">Derive Column (Safe Math AST)</option>
              <option value="fill_missing">Fill Missing Values (Mean)</option>
              <option value="deduplicate">Deduplicate Rows</option>
            </select>
          </div>
        </div>

        {/* Dynamic Fields */}
        {opType === "filter" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-2 border-t border-surfaceBorder">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Column Name</label>
              <input
                type="text"
                value={column}
                onChange={(e) => setColumn(e.target.value)}
                placeholder="e.g. profit_margin_pct"
                className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Operator</label>
              <select
                value={operator}
                onChange={(e) => setOperator(e.target.value)}
                className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
              >
                <option value=">">&gt; (Greater than)</option>
                <option value=">=">&gt;= (Greater than or equal)</option>
                <option value="<">&lt; (Less than)</option>
                <option value="<=">&lt;= (Less than or equal)</option>
                <option value="==">== (Equals)</option>
                <option value="!=">!= (Not equals)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Threshold Value</label>
              <input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="e.g. 50"
                className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
          </div>
        )}

        {opType === "derive_column" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2 border-t border-surfaceBorder">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">New Column Name</label>
              <input
                type="text"
                value={newColumn}
                onChange={(e) => setNewColumn(e.target.value)}
                placeholder="e.g. net_profit_ratio"
                className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Safe Math Expression</label>
              <input
                type="text"
                value={expression}
                onChange={(e) => setExpression(e.target.value)}
                placeholder="e.g. profit / (revenue + 1.0)"
                className="w-full bg-surfaceBorder/30 border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white font-mono"
              />
            </div>
          </div>
        )}

        {/* Buttons */}
        <div className="flex items-center gap-3 pt-4 border-t border-surfaceBorder">
          <button
            onClick={handlePreview}
            className="flex items-center gap-2 px-4 py-2 bg-surfaceBorder hover:bg-surfaceBorder/80 text-white text-sm font-medium rounded-lg transition-colors"
          >
            <Play className="w-4 h-4 text-cyan-400" />
            <span>Test & Preview</span>
          </button>

          <button
            onClick={handleApply}
            disabled={isApplying}
            className="flex items-center gap-2 px-5 py-2 bg-primary hover:bg-primaryHover text-white text-sm font-medium rounded-lg transition-colors shadow-sm shadow-primary/20"
          >
            <Check className="w-4 h-4" />
            <span>{isApplying ? "Committing Version..." : "Commit as New Version"}</span>
          </button>
        </div>
      </div>

      {/* Preview Output Table */}
      {previewRows.length > 0 && (
        <div className="bg-surface rounded-xl border border-surfaceBorder overflow-hidden">
          <div className="px-6 py-4 border-b border-surfaceBorder">
            <h3 className="text-sm font-semibold text-white">Transformed Preview</h3>
          </div>
          <div className="overflow-x-auto max-h-80">
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
      )}
    </div>
  );
}
