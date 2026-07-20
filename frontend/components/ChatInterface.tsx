import React, { useState } from "react";
import { Send, Sparkles, Terminal, ShieldAlert, CheckCircle, ChevronDown, ChevronUp, Bot, User, BrainCircuit, RefreshCw, BarChart4 } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LineChart, Line } from "recharts";

interface ChatInterfaceProps {
  messages: any[];
  onSendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
  dataset: any;
}

export default function ChatInterface({
  messages,
  onSendMessage,
  isLoading,
  dataset,
}: ChatInterfaceProps) {
  const [query, setQuery] = useState("");
  const [expandedCodeId, setExpandedCodeId] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSendMessage(query);
    setQuery("");
  };

  const suggestions = [
    "What caused revenue to fall in March?",
    "Predict next month's sales trend",
    "Find anomalies in the data quality profile",
    "Run t-test on numeric distributions"
  ];

  const handleSuggestionClick = (text: string) => {
    if (isLoading) return;
    onSendMessage(text);
  };

  const toggleCode = (id: string) => {
    setExpandedCodeId(expandedCodeId === id ? null : id);
  };

  // Safe JSON parse helper
  const parseJsonSafe = (str: string) => {
    try {
      return JSON.parse(str);
    } catch {
      return null;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-65px)] bg-[#09090b] text-zinc-300">
      {/* Messages list */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="max-w-3xl mx-auto text-center space-y-8 pt-16">
            <div className="flex flex-col items-center">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-purple-600 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-500/25 mb-4">
                <BrainCircuit className="w-7 h-7 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Ask anything about your data</h2>
              <p className="text-zinc-500 text-sm mt-2 max-w-md">
                Our multi-agent system will automatically clean variables, run statistical tests, generate charts, and compile summaries.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto pt-4">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestionClick(s)}
                  className="p-4 rounded-xl border border-zinc-900 bg-zinc-950/40 text-left text-sm font-semibold hover:border-zinc-800 hover:bg-zinc-900/40 text-zinc-400 hover:text-white transition-all card-hover-effect"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((msg, i) => {
              const isUser = msg.role === "user";
              
              // Extract report details if present in execution_result
              const execRes = msg.execution_result || {};
              const reportDetails = execRes.report_details || null;
              
              return (
                <div key={msg.id || i} className={`flex gap-4 p-5 rounded-2xl border ${
                  isUser ? "bg-zinc-950/20 border-zinc-900/60" : "bg-zinc-950/40 border-zinc-900"
                }`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${
                    isUser ? "bg-zinc-900 border-zinc-850 text-zinc-400" : "bg-purple-900/20 border-purple-500/30 text-purple-400"
                  }`}>
                    {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  <div className="flex-1 space-y-4 overflow-hidden">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-wider text-zinc-500">
                        {isUser ? "User Query" : "AI Analyst Report"}
                      </span>
                    </div>

                    {/* Content */}
                    <div className="prose prose-invert max-w-none text-sm leading-relaxed text-zinc-300 whitespace-pre-line">
                      {msg.content}
                    </div>

                    {/* Agent Sequence Reasoning Chain Tracing */}
                    {msg.agent_metadata?.reasoning_chain && (
                      <div className="p-3 bg-zinc-900/50 rounded-lg border border-zinc-850 space-y-2">
                        <span className="text-[10px] uppercase font-bold text-zinc-500 flex items-center gap-1.5">
                          <BrainCircuit className="w-3.5 h-3.5 text-purple-400 animate-spin" />
                          Multi-Agent Reasoning Trace
                        </span>
                        <div className="space-y-1 pl-1">
                          {msg.agent_metadata.reasoning_chain.map((step: string, sIdx: number) => (
                            <span key={sIdx} className="text-xs text-zinc-500 block">• {step}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Expandable Generated Python Code */}
                    {msg.generated_code && (
                      <div className="border border-zinc-900 rounded-lg overflow-hidden bg-zinc-950">
                        <button
                          onClick={() => toggleCode(msg.id || String(i))}
                          className="w-full flex items-center justify-between px-4 py-2 text-xs font-mono text-zinc-500 hover:text-white bg-zinc-900/40 border-b border-zinc-900 transition-all"
                        >
                          <span className="flex items-center gap-1.5">
                            <Terminal className="w-3.5 h-3.5 text-zinc-400" />
                            View Generated Python Sandbox Code
                          </span>
                          {expandedCodeId === (msg.id || String(i)) ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        {expandedCodeId === (msg.id || String(i)) && (
                          <pre className="p-4 text-xs font-mono overflow-x-auto text-emerald-400/90 leading-relaxed bg-[#0b0b0f]">
                            <code>{msg.generated_code}</code>
                          </pre>
                        )}
                      </div>
                    )}

                    {/* Recommendations & Risks Report layout */}
                    {reportDetails && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                        {reportDetails.recommended_actions?.length > 0 && (
                          <div className="p-4 rounded-xl border border-zinc-850 bg-zinc-900/20 space-y-2">
                            <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                              <CheckCircle className="w-4 h-4" /> Recommended Actions
                            </span>
                            <ul className="space-y-1.5 pl-1 text-xs text-zinc-400">
                              {reportDetails.recommended_actions.map((act: string, idx: number) => (
                                <li key={idx} className="list-disc list-inside leading-relaxed">{act}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {reportDetails.potential_risks?.length > 0 && (
                          <div className="p-4 rounded-xl border border-zinc-850 bg-zinc-900/20 space-y-2">
                            <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                              <ShieldAlert className="w-4 h-4" /> Strategic Risks & Notes
                            </span>
                            <ul className="space-y-1.5 pl-1 text-xs text-zinc-400">
                              {reportDetails.potential_risks.map((risk: string, idx: number) => (
                                <li key={idx} className="list-disc list-inside leading-relaxed">{risk}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {/* DataFrame Preview Widget */}
                    {execRes.dataframe && execRes.dataframe.rows && (
                      <div className="border border-zinc-900 rounded-xl overflow-hidden bg-zinc-950/60 max-w-full">
                        <div className="px-4 py-2 border-b border-zinc-900 flex items-center justify-between bg-zinc-900/40">
                          <span className="text-xs font-bold text-white flex items-center gap-1.5">
                            <BarChart4 className="w-3.5 h-3.5 text-zinc-400" />
                            Data Output Preview ({execRes.dataframe.total_rows} rows)
                          </span>
                        </div>
                        <div className="overflow-x-auto max-h-[300px]">
                          <table className="w-full text-left text-xs">
                            <thead className="bg-zinc-900/80 text-zinc-400 font-bold sticky top-0">
                              <tr>
                                {execRes.dataframe.columns.map((c: string) => (
                                  <th key={c} className="px-4 py-2 border-b border-zinc-900">{c}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-900">
                              {execRes.dataframe.rows.map((row: any, rIdx: number) => (
                                <tr key={rIdx} className="hover:bg-zinc-900/20">
                                  {execRes.dataframe.columns.map((c: string) => (
                                    <td key={c} className="px-4 py-2.5 text-zinc-400 whitespace-nowrap">{String(row[c] ?? "")}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {isLoading && (
          <div className="max-w-4xl mx-auto flex items-center gap-3 p-5 rounded-2xl border border-zinc-900 bg-zinc-950/40">
            <div className="w-8 h-8 rounded-lg bg-purple-900/20 border border-purple-500/30 flex items-center justify-center text-purple-400 animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="space-y-1.5 flex-1">
              <span className="text-[10px] uppercase font-bold text-zinc-500 block animate-pulse">Running planning sequence...</span>
              <div className="h-4 w-48 bg-zinc-900 rounded animate-pulse" />
            </div>
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="border-t border-zinc-900 p-4 bg-zinc-950/60 sticky bottom-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading || !dataset}
            placeholder={dataset ? "Ask a question about your data..." : "Upload a dataset first to begin typing..."}
            className="flex-1 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-zinc-650 transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim() || !dataset}
            className="w-12 h-12 flex items-center justify-center bg-gradient-to-tr from-purple-600 to-blue-500 text-white hover:from-purple-500 hover:to-blue-400 rounded-xl shadow-lg shadow-purple-500/10 transition-all disabled:opacity-50"
          >
            {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </form>
      </div>
    </div>
  );
}
export const mock_messages = [];
