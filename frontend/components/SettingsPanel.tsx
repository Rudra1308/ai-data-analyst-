import React, { useState } from "react";
import { Save, Shield, Settings, Sliders, Key, Database } from "lucide-react";

interface SettingsPanelProps {
  apiKeys: {
    openai: string;
    anthropic: string;
    gemini: string;
    openrouter: string;
  };
  onSaveKeys: (keys: any) => void;
  modelConfig: {
    provider: string;
    model: string;
  };
  onSaveModel: (config: any) => void;
}

export default function SettingsPanel({
  apiKeys,
  onSaveKeys,
  modelConfig,
  onSaveModel,
}: SettingsPanelProps) {
  const [keys, setKeys] = useState(apiKeys);
  const [provider, setProvider] = useState(modelConfig.provider);
  const [model, setModel] = useState(modelConfig.model);
  const [message, setMessage] = useState("");

  const handleSaveKeys = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveKeys(keys);
    setMessage("API Keys updated successfully!");
    setTimeout(() => setMessage(""), 3000);
  };

  const handleSaveModel = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveModel({ provider, model });
    setMessage("Model preferences saved!");
    setTimeout(() => setMessage(""), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8 text-zinc-300">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-6 h-6 text-purple-400" />
          Settings & Configurations
        </h2>
        <p className="text-zinc-500 text-sm mt-1">Configure LLM providers, database connections, and model parameters.</p>
      </div>

      {message && (
        <div className="p-3 bg-purple-500/10 border border-purple-500/30 text-purple-400 rounded-lg text-sm animate-fade-in">
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Model Selection */}
        <form onSubmit={handleSaveModel} className="p-6 rounded-xl border border-zinc-900 bg-zinc-950/40 space-y-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-400" />
            Model Preferences
          </h3>
          <p className="text-xs text-zinc-500">Choose your analytical engine. All agents inherit this configuration.</p>

          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-zinc-400 block mb-1">LLM Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-zinc-700"
              >
                <option value="openrouter">OpenRouter (Recommended)</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="gemini">Google Gemini</option>
                <option value="ollama">Ollama (Local)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-zinc-400 block mb-1">Model Name</label>
              <input
                type="text"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="e.g. google/gemini-2.0-flash-exp:free"
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-zinc-700"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-all"
          >
            <Save className="w-4 h-4" />
            Save Configuration
          </button>
        </form>

        {/* API Credentials */}
        <form onSubmit={handleSaveKeys} className="p-6 rounded-xl border border-zinc-900 bg-zinc-950/40 space-y-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Key className="w-5 h-5 text-pink-400" />
            API Keys
          </h3>
          <p className="text-xs text-zinc-500">Provide keys for direct model access. Stored securely in environment context.</p>

          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-zinc-400 block mb-1">OpenRouter Key</label>
              <input
                type="password"
                value={keys.openrouter}
                onChange={(e) => setKeys({ ...keys, openrouter: e.target.value })}
                placeholder="sk-or-v1-..."
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-zinc-700"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-zinc-400 block mb-1">OpenAI API Key</label>
              <input
                type="password"
                value={keys.openai}
                onChange={(e) => setKeys({ ...keys, openai: e.target.value })}
                placeholder="sk-proj-..."
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-zinc-700"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-zinc-400 block mb-1">Anthropic Key</label>
              <input
                type="password"
                value={keys.anthropic}
                onChange={(e) => setKeys({ ...keys, anthropic: e.target.value })}
                placeholder="sk-ant-..."
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-zinc-700"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-zinc-400 block mb-1">Google Gemini Key</label>
              <input
                type="password"
                value={keys.gemini}
                onChange={(e) => setKeys({ ...keys, gemini: e.target.value })}
                placeholder="AIzaSy..."
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-zinc-700"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-all"
          >
            <Save className="w-4 h-4" />
            Update API Keys
          </button>
        </form>
      </div>

      {/* Database Connection */}
      <div className="p-6 rounded-xl border border-zinc-900 bg-zinc-950/40 space-y-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Database className="w-5 h-5 text-emerald-400" />
          Local Data Engine
        </h3>
        <p className="text-xs text-zinc-500">Information about active storage mechanisms and compute fallback structures.</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
          <div className="p-3 bg-zinc-900 rounded-lg border border-zinc-800 text-center">
            <span className="text-[10px] uppercase font-bold text-zinc-500 block">Query Compiler</span>
            <span className="text-white font-medium text-sm mt-1 block">DuckDB 0.10</span>
          </div>
          <div className="p-3 bg-zinc-900 rounded-lg border border-zinc-800 text-center">
            <span className="text-[10px] uppercase font-bold text-zinc-500 block">DataFrame Core</span>
            <span className="text-white font-medium text-sm mt-1 block">Polars v0.20</span>
          </div>
          <div className="p-3 bg-zinc-900 rounded-lg border border-zinc-800 text-center">
            <span className="text-[10px] uppercase font-bold text-zinc-500 block">Meta DB fallback</span>
            <span className="text-white font-medium text-sm mt-1 block">SQLite / WAL</span>
          </div>
          <div className="p-3 bg-zinc-900 rounded-lg border border-zinc-800 text-center">
            <span className="text-[10px] uppercase font-bold text-zinc-500 block">Sandbox Mode</span>
            <span className="text-emerald-400 font-semibold text-sm mt-1 block flex items-center justify-center gap-1">
              <Shield className="w-3.5 h-3.5" /> SECURE
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
