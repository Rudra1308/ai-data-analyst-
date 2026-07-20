import React, { useState } from "react";
import { AlertTriangle, Info, Check, RefreshCw, Wand2, Database, ShieldCheck, ListFilter } from "lucide-react";

interface DataExplorerProps {
  dataset: any;
  onClean: (instruction?: string) => Promise<void>;
  isCleaning: boolean;
}

export default function DataExplorer({ dataset, onClean, isCleaning }: DataExplorerProps) {
  const [cleanInstruction, setCleanInstruction] = useState("");
  const [activeTab, setActiveTab] = useState<"schema" | "quality">("schema");

  if (!dataset) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-zinc-500 h-[60vh]">
        <Database className="w-12 h-12 text-zinc-700 mb-4 animate-bounce" />
        <span className="text-sm font-medium">No dataset loaded. Upload a CSV file in the sidebar to begin explorer diagnostics.</span>
      </div>
    );
  }

  const profile = dataset.profile_json || {};
  const summary = profile.summary || {};
  const columns = profile.columns || {};
  const quality = profile.quality_report || { overall_score: 100, issues: [] };

  const handleCleanClick = () => {
    onClean(cleanInstruction || undefined);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/5";
    if (score >= 70) return "text-amber-400 border-amber-500/30 bg-amber-500/5";
    return "text-rose-400 border-rose-500/30 bg-rose-500/5";
  };

  return (
    <div className="space-y-6 text-zinc-300 p-6">
      {/* Top Header Card */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-xl border border-zinc-900 bg-zinc-950/40">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-purple-400" />
            {dataset.filename}
          </h2>
          <div className="flex items-center gap-4 text-xs text-zinc-500 pt-1">
            <span>Size: <strong>{(dataset.file_size / 1024).toFixed(1)} KB</strong></span>
            <span>Dimensions: <strong>{dataset.row_count} rows × {dataset.col_count} columns</strong></span>
            <span>Version: <strong>v{dataset.version}</strong></span>
          </div>
        </div>

        {/* Quality Score Ring */}
        <div className={`flex items-center gap-3 px-4 py-2 border rounded-xl ${getScoreColor(quality.overall_score)}`}>
          <div className="text-center">
            <span className="text-[10px] uppercase font-bold text-zinc-500 block">Quality Score</span>
            <span className="text-2xl font-extrabold tracking-tight mt-0.5 block">{quality.overall_score}</span>
          </div>
          <div className="w-px h-8 bg-zinc-800" />
          <ShieldCheck className="w-6 h-6" />
        </div>
      </div>

      {/* Auto-Cleaning Control Panel */}
      <div className="p-6 rounded-xl border border-zinc-900 bg-zinc-950/40 space-y-4">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Wand2 className="w-4 h-4 text-purple-400" />
          Agentic Data Cleaning
        </h3>
        <p className="text-xs text-zinc-500 leading-relaxed">
          The Cleaner Agent automatically resolves duplicate indices, imputes moderate missing cell values, 
          identifies statistical outliers using Interquartile boundaries, and formats columns into database-safe names.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={cleanInstruction}
            onChange={(e) => setCleanInstruction(e.target.value)}
            placeholder="Optional cleaning instructions (e.g. 'Drop nulls in column Age, keep duplicates')"
            className="flex-1 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-zinc-600 transition-all"
          />
          <button
            onClick={handleCleanClick}
            disabled={isCleaning}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white rounded-lg text-sm font-semibold transition-all shadow-md shadow-purple-600/10 disabled:opacity-50"
          >
            {isCleaning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
            {isCleaning ? "Cleaning..." : "Auto Clean"}
          </button>
        </div>
      </div>

      {/* Tabs list */}
      <div className="flex border-b border-zinc-900 gap-6">
        <button
          onClick={() => setActiveTab("schema")}
          className={`pb-2.5 text-sm font-semibold border-b-2 transition-all ${
            activeTab === "schema" ? "text-purple-400 border-purple-500" : "text-zinc-500 border-transparent hover:text-zinc-400"
          }`}
        >
          Column Schema Details
        </button>
        <button
          onClick={() => setActiveTab("quality")}
          className={`pb-2.5 text-sm font-semibold border-b-2 transition-all flex items-center gap-1.5 ${
            activeTab === "quality" ? "text-purple-400 border-purple-500" : "text-zinc-500 border-transparent hover:text-zinc-400"
          }`}
        >
          Diagnostics Report
          {quality.issues.length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full bg-amber-500/10 text-amber-500 text-[10px] font-bold">
              {quality.issues.length}
            </span>
          )}
        </button>
      </div>

      {/* Tab contents */}
      {activeTab === "schema" ? (
        <div className="grid grid-cols-1 gap-4">
          {Object.entries(columns).map(([colName, col]: [string, any]) => (
            <div key={colName} className="p-4 rounded-xl border border-zinc-900 bg-zinc-950/20 flex flex-col md:flex-row md:items-center justify-between gap-4 card-hover-effect">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">{colName}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-zinc-900 border border-zinc-800 rounded text-zinc-500 uppercase">
                    {col.dtype}
                  </span>
                </div>
                <div className="text-xs text-zinc-500 flex items-center gap-4">
                  <span>Nulls: <strong>{col.null_count} ({col.null_percentage}%)</strong></span>
                  <span>Unique: <strong>{col.unique_count}</strong></span>
                  <span>Group: <strong className="capitalize">{col.type_group}</strong></span>
                </div>
              </div>

              {/* Display statistics or values distribution */}
              {col.stats && (
                <div className="flex flex-wrap gap-2 text-[10px] text-zinc-400 max-w-md">
                  {col.type_group === "numeric" && (
                    <>
                      <span className="px-2 py-1 bg-zinc-900 rounded">Mean: <strong>{col.stats.mean?.toFixed(2)}</strong></span>
                      <span className="px-2 py-1 bg-zinc-900 rounded">Median: <strong>{col.stats.median?.toFixed(2)}</strong></span>
                      <span className="px-2 py-1 bg-zinc-900 rounded">Range: <strong>{col.stats.min} - {col.stats.max}</strong></span>
                    </>
                  )}
                  {col.type_group === "temporal" && (
                    <span className="px-2 py-1 bg-zinc-900 rounded">Timeline: <strong>{col.stats.min} to {col.stats.max}</strong></span>
                  )}
                </div>
              )}

              {col.value_distribution && (
                <div className="flex flex-wrap gap-1.5 text-[9px] text-zinc-500 max-w-md">
                  {Object.entries(col.value_distribution).slice(0, 3).map(([val, cnt]: [any, any]) => (
                    <span key={val} className="px-1.5 py-0.5 bg-zinc-900 rounded border border-zinc-850">
                      {val}: <strong className="text-zinc-400">{cnt}</strong>
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {quality.issues.length === 0 ? (
            <div className="p-8 text-center border border-zinc-900 rounded-xl bg-zinc-950/20 text-zinc-500 flex flex-col items-center">
              <Check className="w-8 h-8 text-emerald-400 mb-2" />
              <span className="text-sm font-semibold">Perfect dataset health! No diagnostic issues found.</span>
            </div>
          ) : (
            quality.issues.map((issue: any, index: number) => (
              <div
                key={index}
                className={`p-4 rounded-xl border flex items-start gap-3 ${
                  issue.severity === "warning"
                    ? "border-amber-500/20 bg-amber-500/5 text-amber-300"
                    : "border-blue-500/20 bg-blue-500/5 text-blue-300"
                }`}
              >
                {issue.severity === "warning" ? (
                  <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                ) : (
                  <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                )}
                <div>
                  <span className="text-xs uppercase font-bold text-zinc-500 block mb-0.5">
                    {issue.type} • Column {issue.column}
                  </span>
                  <p className="text-sm">{issue.message}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
