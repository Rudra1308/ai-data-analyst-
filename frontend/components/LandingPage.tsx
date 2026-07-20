import React from "react";
import { Sparkles, BarChart2, CheckCircle2, ShieldAlert, Cpu, ChevronRight } from "lucide-react";

interface LandingPageProps {
  onStart: () => void;
}

export default function LandingPage({ onStart }: LandingPageProps) {
  return (
    <div className="relative min-h-screen flex flex-col justify-between overflow-hidden bg-[#07070a]">
      {/* Background radial highlight */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-900/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-900/10 blur-[120px] rounded-full pointer-events-none" />

      {/* Header */}
      <header className="border-b border-zinc-900 px-6 py-4 flex items-center justify-between z-10 backdrop-blur-md bg-[#07070a]/60 sticky top-0">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-purple-600 to-blue-500 flex items-center justify-center font-bold text-white shadow-lg shadow-purple-500/25">
            A
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
            AI Data Analyst
          </span>
        </div>
        <button
          onClick={onStart}
          className="px-4 py-2 text-sm font-medium text-white bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700 rounded-lg transition-all"
        >
          Sign In
        </button>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 py-16 max-w-5xl mx-auto z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-purple-500/30 bg-purple-500/5 text-purple-400 text-xs font-medium mb-6 animate-pulse">
          <Sparkles className="w-3.5 h-3.5" />
          Enterprise-Grade Multi-Agent Analysis
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          Your Data. <br />
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
            Instantly Analyzed.
          </span>
        </h1>
        
        <p className="text-zinc-400 text-lg md:text-xl max-w-2xl mb-10 leading-relaxed">
          Upload CSV, Excel, Parquet or SQL databases. Ask questions in plain English. 
          Get clean data, interactive charts, forecasting models, and business summaries automatically.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-16">
          <button
            onClick={onStart}
            className="flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 rounded-xl transition-all shadow-lg shadow-purple-600/30"
          >
            Launch Platform
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left mt-8">
          <div className="p-6 rounded-2xl border border-zinc-900 bg-zinc-950/40 backdrop-blur-sm card-hover-effect">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 mb-4 border border-purple-500/20">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Multi-Agent Planner</h3>
            <p className="text-zinc-500 text-sm leading-relaxed">
              Planner coordinates cleaning, EDA, forecasting, and visualization agents sequentially through JSON messaging protocols.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-zinc-900 bg-zinc-950/40 backdrop-blur-sm card-hover-effect">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 mb-4 border border-blue-500/20">
              <BarChart2 className="w-5 h-5" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Polars & DuckDB Core</h3>
            <p className="text-zinc-500 text-sm leading-relaxed">
              Engineered for large-scale datasets. Uses Polars lazy frames and local SQL query compilation for sub-second analysis.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-zinc-900 bg-zinc-950/40 backdrop-blur-sm card-hover-effect">
            <div className="w-10 h-10 rounded-xl bg-pink-500/10 flex items-center justify-center text-pink-400 mb-4 border border-pink-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Automated Data Profiling</h3>
            <p className="text-zinc-500 text-sm leading-relaxed">
              Calculates missing-value metrics, IQR outlier clusters, and suggests database column normalization schemas out-of-the-box.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-950 px-6 py-6 text-center text-xs text-zinc-600 z-10 bg-[#07070a]">
        © 2026 AI Data Analyst Inc. All rights reserved. Enterprise-Grade Minimalist SaaS.
      </footer>
    </div>
  );
}
