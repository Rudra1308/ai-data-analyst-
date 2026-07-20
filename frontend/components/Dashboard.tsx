import React, { useState, useEffect, useRef } from "react";
import {
  Folder,
  Plus,
  Database,
  UploadCloud,
  Layers,
  Settings,
  BrainCircuit,
  LogOut,
  User as UserIcon,
  ChevronsUpDown,
  Sparkles,
  RefreshCw,
  FolderOpen
} from "lucide-react";
import ChatInterface from "./ChatInterface";
import DataExplorer from "./DataExplorer";
import VisualizationStudio from "./VisualizationStudio";
import SettingsPanel from "./SettingsPanel";

interface DashboardProps {
  onLogout: () => void;
  user: any;
}

export default function Dashboard({ onLogout, user }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<"chat" | "explorer" | "studio" | "settings">("chat");
  const [projects, setProjects] = useState<any[]>([]);
  const [activeProject, setActiveProject] = useState<any>(null);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [activeDataset, setActiveDataset] = useState<any>(null);
  const [conversations, setConversations] = useState<any[]>([]);
  const [activeConversation, setActiveConversation] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isCleaning, setIsCleaning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Model & Keys Settings State
  const [apiKeys, setApiKeys] = useState({
    openai: "",
    anthropic: "",
    gemini: "",
    openrouter: ""
  });
  const [modelConfig, setModelConfig] = useState({
    provider: "openrouter",
    model: "google/gemini-2.0-flash-exp:free"
  });

  const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

  // Check stored credentials & initialize
  useEffect(() => {
    // Load local storage items if any
    const storedKeys = localStorage.getItem("ai_analyst_keys");
    if (storedKeys) setApiKeys(JSON.parse(storedKeys));

    const storedModel = localStorage.getItem("ai_analyst_model");
    if (storedModel) setModelConfig(JSON.parse(storedModel));

    fetchProjects();
  }, []);

  // Fetch all projects owned by the user
  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/projects/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length > 0) {
          handleSelectProject(data[0]);
        } else {
          // Auto-create a default project if none exist
          createProject("My Workspace", "Default analytics playground");
        }
      }
    } catch (e) {
      console.error("Failed to load projects", e);
    }
  };

  const createProject = async (name: string, description?: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/projects/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ name, description })
      });
      if (res.ok) {
        const newProj = await res.json();
        setProjects(prev => [...prev, newProj]);
        handleSelectProject(newProj);
      }
    } catch (e) {
      console.error("Failed to create project", e);
    }
  };

  const handleSelectProject = async (project: any) => {
    setActiveProject(project);
    fetchDatasets(project.id);
    fetchConversations(project.id);
  };

  // Fetch project datasets
  const fetchDatasets = async (projectId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/datasets/?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setDatasets(data);
        if (data.length > 0) {
          setActiveDataset(data[0]);
        } else {
          setActiveDataset(null);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Fetch project conversations
  const fetchConversations = async (projectId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/chats/conversations?project_id=${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
        if (data.length > 0) {
          handleSelectConversation(data[0].id);
        } else {
          // Auto create a conversation if none
          createConversation(projectId);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const createConversation = async (projectId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/chats/conversations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ project_id: projectId, title: "New Analysis" })
      });
      if (res.ok) {
        const data = await res.json();
        setConversations(prev => [data, ...prev]);
        setActiveConversation(data);
        setMessages([]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectConversation = async (convId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/chats/conversations/${convId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setActiveConversation(data);
        setMessages(data.messages || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Upload Dataset handler
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !activeProject) return;

    setIsUploading(true);
    const file = files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", activeProject.id);

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/datasets/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setDatasets(prev => [data, ...prev]);
        setActiveDataset(data);
        setActiveTab("explorer");
      } else {
        const err = await res.json();
        alert(`Upload error: ${err.detail}`);
      }
    } catch (e) {
      alert("Failed to upload dataset.");
    } finally {
      setIsUploading(false);
    }
  };

  // Auto clean dataset handler
  const handleCleanDataset = async (instruction?: string) => {
    if (!activeDataset) return;
    setIsCleaning(true);

    const formData = new FormData();
    if (instruction) {
      formData.append("instruction", instruction);
    }

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/datasets/${activeDataset.id}/clean`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      if (res.ok) {
        const cleaned = await res.json();
        setDatasets(prev => [cleaned, ...prev]);
        setActiveDataset(cleaned);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsCleaning(false);
    }
  };

  // Submit analytical question to LLM multi-agent pipeline
  const handleSendMessage = async (content: string) => {
    if (!activeConversation || !activeDataset) return;
    setIsLoading(true);

    // Immediately push user question placeholder
    const userMsg = {
      role: "user",
      content,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${BACKEND_URL}/chats/conversations/${activeConversation.id}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          content,
          dataset_id: activeDataset.id,
          api_keys: apiKeys,
          model_settings: modelConfig
        })
      });

      if (res.ok) {
        const assistantMsg = await res.json();
        setMessages(prev => {
          // Replace last message or append
          return [...prev.filter(m => m.role === "user" || m.id), assistantMsg];
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#07070a] text-zinc-300">
      {/* Sidebar Panel */}
      <aside className="w-64 bg-zinc-950 border-r border-zinc-900 flex flex-col justify-between shrink-0">
        <div className="flex-1 flex flex-col overflow-y-auto">
          {/* Logo */}
          <div className="p-5 border-b border-zinc-900 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-600 to-blue-500 flex items-center justify-center font-bold text-white shadow-md shadow-purple-500/10">
                A
              </div>
              <span className="font-bold tracking-tight text-white text-base">AI Analyst</span>
            </div>
            <span className="px-1.5 py-0.5 rounded bg-zinc-900 text-[10px] text-zinc-500 font-bold border border-zinc-800">
              SaaS
            </span>
          </div>

          {/* Project switch */}
          <div className="p-4 border-b border-zinc-900 space-y-2">
            <label className="text-[10px] uppercase font-bold text-zinc-500 block">Workspace</label>
            <div className="flex items-center justify-between bg-zinc-900 rounded-lg px-3 py-2 border border-zinc-800 text-sm hover:border-zinc-700 transition-all cursor-pointer">
              <div className="flex items-center gap-2 text-white font-medium">
                <FolderOpen className="w-4 h-4 text-purple-400" />
                <span>{activeProject?.name || "Loading..."}</span>
              </div>
              <Plus
                className="w-4 h-4 text-zinc-500 hover:text-white"
                onClick={(e) => {
                  e.stopPropagation();
                  const name = prompt("Enter project name:");
                  if (name) createProject(name);
                }}
              />
            </div>
          </div>

          {/* Datasets list */}
          <div className="p-4 border-b border-zinc-900 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-[10px] uppercase font-bold text-zinc-500 block">Uploaded Datasets</label>
              <button
                disabled={isUploading}
                onClick={() => fileInputRef.current?.click()}
                className="text-xs text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1"
              >
                {isUploading ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                Add
              </button>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleUpload}
                accept=".csv,.xlsx,.xls,.parquet,.feather,.json"
                className="hidden"
              />
            </div>
            <div className="space-y-1">
              {datasets.map(d => (
                <button
                  key={d.id}
                  onClick={() => setActiveDataset(d)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs flex items-center justify-between transition-all ${
                    activeDataset?.id === d.id
                      ? "bg-purple-500/10 border border-purple-500/20 text-white font-semibold"
                      : "hover:bg-zinc-900 border border-transparent text-zinc-400"
                  }`}
                >
                  <span className="truncate pr-2">{d.filename}</span>
                  <Database className="w-3.5 h-3.5 shrink-0 text-zinc-500" />
                </button>
              ))}
              {datasets.length === 0 && (
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="p-3 border border-dashed border-zinc-900 hover:border-zinc-800 rounded-lg text-center cursor-pointer text-[10px] text-zinc-500 space-y-1"
                >
                  <UploadCloud className="w-4 h-4 mx-auto text-zinc-650" />
                  <span>Upload CSV/Excel</span>
                </div>
              )}
            </div>
          </div>

          {/* Tab selectors */}
          <nav className="p-4 space-y-1">
            <button
              onClick={() => setActiveTab("chat")}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                activeTab === "chat" ? "bg-zinc-900 text-white" : "hover:bg-zinc-900/50 text-zinc-400 hover:text-white"
              }`}
            >
              <BrainCircuit className="w-4 h-4 text-purple-400" />
              Chat Analyst
            </button>
            <button
              onClick={() => setActiveTab("explorer")}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                activeTab === "explorer" ? "bg-zinc-900 text-white" : "hover:bg-zinc-900/50 text-zinc-400 hover:text-white"
              }`}
            >
              <Database className="w-4 h-4 text-blue-400" />
              Data Explorer
            </button>
            <button
              onClick={() => setActiveTab("studio")}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                activeTab === "studio" ? "bg-zinc-900 text-white" : "hover:bg-zinc-900/50 text-zinc-400 hover:text-white"
              }`}
            >
              <Layers className="w-4 h-4 text-pink-400" />
              Visualization Studio
            </button>
            <button
              onClick={() => setActiveTab("settings")}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                activeTab === "settings" ? "bg-zinc-900 text-white" : "hover:bg-zinc-900/50 text-zinc-400 hover:text-white"
              }`}
            >
              <Settings className="w-4 h-4 text-zinc-400" />
              Settings
            </button>
          </nav>
        </div>

        {/* User profile footer */}
        <div className="p-4 border-t border-zinc-900 flex items-center justify-between text-xs text-zinc-400 bg-zinc-950/80">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center border border-zinc-700">
              <UserIcon className="w-3.5 h-3.5" />
            </div>
            <div className="truncate w-24">
              <span className="text-white block truncate font-medium">{user.full_name || "User Profile"}</span>
              <span className="text-[10px] text-zinc-500 block truncate capitalize">{user.role}</span>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="p-1.5 hover:bg-zinc-900 rounded-lg border border-zinc-850 hover:text-white transition-all"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto bg-[#07070a]">
        {activeTab === "chat" && (
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            dataset={activeDataset}
          />
        )}
        {activeTab === "explorer" && (
          <DataExplorer
            dataset={activeDataset}
            onClean={handleCleanDataset}
            isCleaning={isCleaning}
          />
        )}
        {activeTab === "studio" && (
          <VisualizationStudio dashboards={[]} dataset={activeDataset} />
        )}
        {activeTab === "settings" && (
          <SettingsPanel
            apiKeys={apiKeys}
            onSaveKeys={(keys) => {
              setApiKeys(keys);
              localStorage.setItem("ai_analyst_keys", JSON.stringify(keys));
            }}
            modelConfig={modelConfig}
            onSaveModel={(conf) => {
              setModelConfig(conf);
              localStorage.setItem("ai_analyst_model", JSON.stringify(conf));
            }}
          />
        )}
      </main>
    </div>
  );
}
