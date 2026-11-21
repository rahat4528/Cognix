"use client";

import { useEffect, useState } from "react";
import { Terminal, Play, Save, Check, AlertCircle, Clock, Database } from "lucide-react";
import { api } from "@/lib/api";
import { SQLExecuteResponse } from "@/lib/types";

export default function SQLStudioPage() {
  const [sqlText, setSqlText] = useState<string>(
    "SELECT order_id, region, product_category, revenue, profit, profit_margin_pct FROM ds_global_enterprise_sales_2025 WHERE profit_margin_pct > 40.0 ORDER BY profit DESC LIMIT 50;"
  );
  const [result, setResult] = useState<SQLExecuteResponse | null>(null);
  const [executing, setExecuting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  async function handleExecute() {
    try {
      setExecuting(true);
      setError(null);
      const wss = await api.listWorkspaces();
      if (wss[0]) {
        const res = await api.executeSQL(wss[0].id, sqlText);
        setResult(res);
      }
    } catch (err: any) {
      setError(err.message || "Query execution failed");
      setResult(null);
    } finally {
      setExecuting(false);
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">SQL Studio</h1>
          <p className="text-gray-400 text-xs mt-1">
            Execute analytical SQL queries in a sandboxed, read-only DuckDB instance with statement timeout and memory constraints.
          </p>
        </div>

        <button
          onClick={handleExecute}
          disabled={executing}
          className="flex items-center gap-2 px-5 py-2 bg-primary hover:bg-primaryHover text-white text-sm font-medium rounded-lg transition-colors shadow-sm shadow-primary/20"
        >
          <Play className="w-4 h-4" />
          <span>{executing ? "Executing..." : "Run Query"}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Editor & View Schema */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SQL Editor Area */}
        <div className="lg:col-span-3 bg-surface rounded-xl border border-surfaceBorder overflow-hidden">
          <div className="px-4 py-2.5 bg-surfaceBorder/30 border-b border-surfaceBorder flex items-center justify-between">
            <span className="text-xs font-mono text-gray-400">DuckDB SQL Editor (Read-Only)</span>
            <span className="text-[11px] text-gray-500">Security Sandbox Active</span>
          </div>
          <textarea
            value={sqlText}
            onChange={(e) => setSqlText(e.target.value)}
            rows={7}
            className="w-full bg-[#0d131f] text-gray-200 p-4 font-mono text-xs focus:outline-none resize-none"
          />
        </div>

        {/* Registered Views Schema */}
        <div className="bg-surface rounded-xl border border-surfaceBorder p-4 space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 flex items-center gap-2">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            Registered Views
          </h3>
          <div className="p-2.5 bg-surfaceBorder/20 rounded border border-surfaceBorder text-xs font-mono text-gray-300">
            <span className="text-primary block font-semibold">ds_global_enterprise_sales_2025</span>
            <span className="text-[10px] text-gray-500 mt-1 block">Columns: order_id, region, revenue, profit, units_sold...</span>
          </div>
        </div>
      </div>

      {/* Query Results Table */}
      {result && (
        <div className="bg-surface rounded-xl border border-surfaceBorder overflow-hidden space-y-0">
          <div className="px-6 py-3 border-b border-surfaceBorder flex items-center justify-between bg-surfaceBorder/20">
            <div className="flex items-center gap-4 text-xs font-mono text-gray-400">
              <span className="text-white font-semibold">{result.row_count} rows returned</span>
              <span className="flex items-center gap-1 text-emerald-400">
                <Clock className="w-3.5 h-3.5" /> {result.duration_ms} ms
              </span>
            </div>
          </div>

          <div className="overflow-x-auto max-h-96">
            <table className="w-full text-left text-xs">
              <thead className="bg-surfaceBorder/30 text-gray-300 font-semibold sticky top-0">
                <tr>
                  {result.columns.map((col) => (
                    <th key={col} className="px-4 py-2.5 border-b border-surfaceBorder whitespace-nowrap">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-surfaceBorder/50 text-gray-300">
                {result.rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-surfaceBorder/20 transition-colors">
                    {result.columns.map((col) => (
                      <td key={col} className="px-4 py-2 whitespace-nowrap font-mono text-[11px]">
                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-gray-600">NULL</span>}
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
