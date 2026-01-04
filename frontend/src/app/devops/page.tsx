"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Terminal,
    Container,
    Network,
    FileText,
    Play,
    Square,
    RefreshCw,
    Trash2,
    Download,
    Upload,
    Server,
    Cpu,
    HardDrive,
    Activity,
    AlertCircle,
    CheckCircle2,
    Clock,
    Code2,
    Zap,
    Shield,
    Database,
    Globe
} from "lucide-react";

interface DockerContainer {
    id: string;
    name: string;
    image: string;
    status: string;
    state: string;
    ports: string;
    created: string;
}

interface NetworkInterface {
    name: string;
    rx_bytes: number;
    tx_bytes: number;
    rx_packets: number;
    tx_packets: number;
}

interface LogEntry {
    timestamp: string;
    level: string;
    service: string;
    message: string;
}

export default function DevOpsPage() {
    const [activeTab, setActiveTab] = useState<"docker" | "network" | "terminal" | "logs">("docker");
    const [containers, setContainers] = useState<DockerContainer[]>([]);
    const [networks, setNetworks] = useState<NetworkInterface[]>([]);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [terminalOutput, setTerminalOutput] = useState<string[]>([]);
    const [terminalInput, setTerminalInput] = useState("");
    const [selectedShell, setSelectedShell] = useState<"bash" | "zsh" | "semsh">("bash");
    const [isLoading, setIsLoading] = useState(false);
    const terminalRef = useRef<HTMLDivElement>(null);

    // Fetch Docker containers
    const fetchContainers = async () => {
        try {
            const response = await fetch("http://localhost:8000/api/v1/docker/containers");
            if (response.ok) {
                const data = await response.json();
                setContainers(data.containers || []);
            }
        } catch (error) {
            console.error("Failed to fetch containers:", error);
        }
    };

    // Fetch network stats
    const fetchNetworkStats = async () => {
        try {
            const response = await fetch("http://localhost:8000/api/v1/system/network");
            if (response.ok) {
                const data = await response.json();
                setNetworks(data.interfaces || []);
            }
        } catch (error) {
            console.error("Failed to fetch network stats:", error);
        }
    };

    // Fetch logs
    const fetchLogs = async () => {
        try {
            const response = await fetch("http://localhost:8000/api/v1/logs?limit=100");
            if (response.ok) {
                const data = await response.json();
                setLogs(data.logs || []);
            }
        } catch (error) {
            console.error("Failed to fetch logs:", error);
        }
    };

    // Execute terminal command
    const executeCommand = async () => {
        if (!terminalInput.trim()) return;

        const command = terminalInput;
        setTerminalOutput(prev => [...prev, `$ ${command}`]);
        setTerminalInput("");

        try {
            const role = localStorage.getItem('sentinel_soul_role') || 'Unauthorized';
            const userId = localStorage.getItem('sentinel_soul_id') || 'unknown';

            const response = await fetch("http://localhost:8000/api/v1/terminal/exec", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    command,
                    shell: selectedShell,
                    user_id: userId,
                    role: role
                })
            });

            if (response.ok) {
                const data = await response.json();
                setTerminalOutput(prev => [...prev, data.output || "Command executed"]);
            } else {
                setTerminalOutput(prev => [...prev, "Error: Command failed"]);
            }
        } catch (error) {
            setTerminalOutput(prev => [...prev, `Error: ${error}`]);
        }

        // Auto-scroll to bottom
        setTimeout(() => {
            if (terminalRef.current) {
                terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
            }
        }, 100);
    };

    // Docker actions
    const dockerAction = async (containerId: string, action: "start" | "stop" | "restart") => {
        setIsLoading(true);
        try {
            await fetch(`http://localhost:8000/api/v1/docker/containers/${containerId}/${action}`, {
                method: "POST"
            });
            await fetchContainers();
        } catch (error) {
            console.error(`Failed to ${action} container:`, error);
        }
        setIsLoading(false);
    };

    useEffect(() => {
        if (activeTab === "docker") fetchContainers();
        if (activeTab === "network") fetchNetworkStats();
        if (activeTab === "logs") fetchLogs();

        const interval = setInterval(() => {
            if (activeTab === "docker") fetchContainers();
            if (activeTab === "network") fetchNetworkStats();
            if (activeTab === "logs") fetchLogs();
        }, 5000);

        return () => clearInterval(interval);
    }, [activeTab]);

    return (
        <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-cyan-500/30 overflow-hidden relative font-sans">
            {/* Visual Identity Layer */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-emerald-500/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-cyan-500/10 blur-[150px] rounded-full animate-pulse" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-30 brightness-150 contrast-125 pointer-events-none" />
            </div>

            <div className="relative z-10 mx-auto max-w-[1800px] px-8 py-10">
                {/* Header */}
                <header className="mb-16">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center gap-4 mb-4"
                    >
                        <div className="h-[3px] w-12 bg-gradient-to-r from-emerald-500 to-transparent rounded-full" />
                        <p className="text-[10px] uppercase tracking-[0.6em] text-emerald-400 font-black">
                            Sentinel DevOps OS // Infrastructure Command Center 0x8F92A
                        </p>
                    </motion.div>

                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
                        DevOps <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-white to-cyan-500">Console</span> Matrix
                    </h1>

                    <div className="flex flex-wrap gap-8 mt-8 items-center">
                        <div className="flex items-center gap-3">
                            <Server className="w-4 h-4 text-emerald-400 animate-pulse" />
                            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                                Mode: <span className="text-white">Infrastructure Management</span>
                            </p>
                        </div>
                    </div>
                </header>

                {/* Tab Navigation */}
                <div className="flex gap-4 mb-12 flex-wrap">
                    <TabButton
                        active={activeTab === "docker"}
                        onClick={() => setActiveTab("docker")}
                        icon={<Container size={18} />}
                        label="Docker Management"
                    />
                    <TabButton
                        active={activeTab === "network"}
                        onClick={() => setActiveTab("network")}
                        icon={<Network size={18} />}
                        label="Network Monitor"
                    />
                    <TabButton
                        active={activeTab === "terminal"}
                        onClick={() => setActiveTab("terminal")}
                        icon={<Terminal size={18} />}
                        label="Terminal Console"
                    />
                    <TabButton
                        active={activeTab === "logs"}
                        onClick={() => setActiveTab("logs")}
                        icon={<FileText size={18} />}
                        label="System Logs"
                    />
                </div>

                {/* Docker Management Tab */}
                {activeTab === "docker" && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        <div className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">
                                        Docker Containers
                                    </h2>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
                                        Container orchestration and management
                                    </p>
                                </div>
                                <button
                                    onClick={fetchContainers}
                                    className="px-6 py-3 rounded-2xl font-black uppercase tracking-wider text-sm bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30 transition-all flex items-center gap-2"
                                >
                                    <RefreshCw size={16} />
                                    Refresh
                                </button>
                            </div>

                            <div className="space-y-3">
                                {containers.length === 0 ? (
                                    <div className="text-center py-12 text-gray-500">
                                        <Container size={48} className="mx-auto mb-4 opacity-20" />
                                        <p className="text-sm uppercase tracking-widest">No containers found</p>
                                    </div>
                                ) : (
                                    containers.map((container) => (
                                        <ContainerCard
                                            key={container.id}
                                            container={container}
                                            onAction={dockerAction}
                                            isLoading={isLoading}
                                        />
                                    ))
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Network Monitor Tab */}
                {activeTab === "network" && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        <div className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">
                                        Network Interfaces
                                    </h2>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
                                        Real-time network traffic monitoring
                                    </p>
                                </div>
                                <button
                                    onClick={fetchNetworkStats}
                                    className="px-6 py-3 rounded-2xl font-black uppercase tracking-wider text-sm bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30 transition-all flex items-center gap-2"
                                >
                                    <RefreshCw size={16} />
                                    Refresh
                                </button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {networks.length === 0 ? (
                                    <div className="col-span-2 text-center py-12 text-gray-500">
                                        <Network size={48} className="mx-auto mb-4 opacity-20" />
                                        <p className="text-sm uppercase tracking-widest">No network data available</p>
                                    </div>
                                ) : (
                                    networks.map((net) => (
                                        <NetworkCard key={net.name} network={net} />
                                    ))
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Terminal Console Tab */}
                {activeTab === "terminal" && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        <div className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">
                                        Terminal Console
                                    </h2>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
                                        Execute system commands and scripts
                                    </p>
                                </div>
                                <div className="flex gap-2">
                                    <ShellButton
                                        active={selectedShell === "bash"}
                                        onClick={() => setSelectedShell("bash")}
                                        label="BASH"
                                    />
                                    <ShellButton
                                        active={selectedShell === "zsh"}
                                        onClick={() => setSelectedShell("zsh")}
                                        label="ZSH"
                                    />
                                    <ShellButton
                                        active={selectedShell === "semsh"}
                                        onClick={() => setSelectedShell("semsh")}
                                        label="SEMSH"
                                    />
                                </div>
                            </div>

                            {/* Terminal Output */}
                            <div
                                ref={terminalRef}
                                className="bg-black/60 border border-emerald-500/20 rounded-2xl p-6 h-[500px] overflow-y-auto font-mono text-sm mb-4"
                            >
                                {terminalOutput.length === 0 ? (
                                    <div className="text-emerald-400/50">
                                        <p>Sentinel DevOps Terminal v2.1.0</p>
                                        <p>Type 'help' for available commands</p>
                                        <p className="mt-2">Ready.</p>
                                    </div>
                                ) : (
                                    terminalOutput.map((line, index) => (
                                        <div
                                            key={index}
                                            className={line.startsWith("$") ? "text-cyan-400 font-bold" : "text-emerald-400"}
                                        >
                                            {line}
                                        </div>
                                    ))
                                )}
                            </div>

                            {/* Terminal Input */}
                            <div className="flex gap-3">
                                <div className="flex-1 relative">
                                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-cyan-400 font-mono font-bold">
                                        $
                                    </span>
                                    <input
                                        type="text"
                                        value={terminalInput}
                                        onChange={(e) => setTerminalInput(e.target.value)}
                                        onKeyPress={(e) => e.key === "Enter" && executeCommand()}
                                        placeholder="Enter command..."
                                        className="w-full bg-black/40 border border-emerald-500/20 rounded-2xl px-4 pl-8 py-4 text-white font-mono focus:outline-none focus:border-emerald-500/50 transition-all"
                                    />
                                </div>
                                <button
                                    onClick={executeCommand}
                                    className="px-8 py-4 rounded-2xl font-black uppercase tracking-wider text-sm bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-2xl hover:shadow-emerald-500/50 transition-all flex items-center gap-2"
                                >
                                    <Play size={16} />
                                    Execute
                                </button>
                            </div>

                            {/* Quick Commands */}
                            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
                                <QuickCommand
                                    label="System Status"
                                    command="sctl status"
                                    onClick={() => {
                                        setTerminalInput("sctl status");
                                        setTimeout(executeCommand, 100);
                                    }}
                                />
                                <QuickCommand
                                    label="Docker PS"
                                    command="docker ps"
                                    onClick={() => {
                                        setTerminalInput("docker ps");
                                        setTimeout(executeCommand, 100);
                                    }}
                                />
                                <QuickCommand
                                    label="Network Stats"
                                    command="ip -s link"
                                    onClick={() => {
                                        setTerminalInput("ip -s link");
                                        setTimeout(executeCommand, 100);
                                    }}
                                />
                                <QuickCommand
                                    label="Disk Usage"
                                    command="df -h"
                                    onClick={() => {
                                        setTerminalInput("df -h");
                                        setTimeout(executeCommand, 100);
                                    }}
                                />
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* System Logs Tab */}
                {activeTab === "logs" && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        <div className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">
                                        System Logs
                                    </h2>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
                                        Real-time log aggregation and analysis
                                    </p>
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        onClick={fetchLogs}
                                        className="px-6 py-3 rounded-2xl font-black uppercase tracking-wider text-sm bg-purple-500/20 text-purple-400 border border-purple-500/30 hover:bg-purple-500/30 transition-all flex items-center gap-2"
                                    >
                                        <RefreshCw size={16} />
                                        Refresh
                                    </button>
                                    <button
                                        className="px-6 py-3 rounded-2xl font-black uppercase tracking-wider text-sm bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30 transition-all flex items-center gap-2"
                                    >
                                        <Download size={16} />
                                        Export
                                    </button>
                                </div>
                            </div>

                            <div className="bg-black/60 border border-purple-500/20 rounded-2xl p-6 h-[600px] overflow-y-auto font-mono text-xs space-y-1">
                                {logs.length === 0 ? (
                                    <div className="text-center py-12 text-gray-500">
                                        <FileText size={48} className="mx-auto mb-4 opacity-20" />
                                        <p className="text-sm uppercase tracking-widest">No logs available</p>
                                    </div>
                                ) : (
                                    logs.map((log, index) => (
                                        <LogLine key={index} log={log} />
                                    ))
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>
        </main>
    );
}

// Helper Components

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
    return (
        <button
            onClick={onClick}
            className={`px-6 py-4 rounded-2xl font-black uppercase tracking-wider text-sm transition-all flex items-center gap-3 ${active
                ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-2xl shadow-emerald-500/50"
                : "bg-slate-900/40 text-gray-400 hover:text-white border border-white/5"
                }`}
        >
            {icon}
            {label}
        </button>
    );
}

function ShellButton({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-xl font-black uppercase tracking-wider text-xs transition-all ${active
                ? "bg-emerald-500 text-white"
                : "bg-slate-900/40 text-gray-400 hover:text-white border border-white/5"
                }`}
        >
            {label}
        </button>
    );
}

function ContainerCard({ container, onAction, isLoading }: {
    container: DockerContainer;
    onAction: (id: string, action: "start" | "stop" | "restart") => void;
    isLoading: boolean;
}) {
    const isRunning = container.state === "running";

    return (
        <div className="bg-[#0a0e1a]/60 border border-white/5 rounded-2xl p-6">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${isRunning ? "bg-emerald-500/20 text-emerald-400" : "bg-gray-500/20 text-gray-400"}`}>
                        <Container size={24} />
                    </div>
                    <div>
                        <h3 className="font-black text-white text-lg">{container.name}</h3>
                        <p className="text-xs text-gray-500 font-mono">{container.image}</p>
                    </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-black uppercase ${isRunning ? "bg-emerald-500/20 text-emerald-400" : "bg-gray-500/20 text-gray-400"
                    }`}>
                    {container.state}
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4 text-xs">
                <div>
                    <p className="text-gray-500 uppercase tracking-wider mb-1">Status</p>
                    <p className="text-white font-mono">{container.status}</p>
                </div>
                <div>
                    <p className="text-gray-500 uppercase tracking-wider mb-1">Ports</p>
                    <p className="text-white font-mono">{container.ports || "None"}</p>
                </div>
            </div>

            <div className="flex gap-2">
                {!isRunning && (
                    <button
                        onClick={() => onAction(container.id, "start")}
                        disabled={isLoading}
                        className="flex-1 px-4 py-2 rounded-xl font-black uppercase tracking-wider text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30 transition-all flex items-center justify-center gap-2"
                    >
                        <Play size={14} />
                        Start
                    </button>
                )}
                {isRunning && (
                    <>
                        <button
                            onClick={() => onAction(container.id, "stop")}
                            disabled={isLoading}
                            className="flex-1 px-4 py-2 rounded-xl font-black uppercase tracking-wider text-xs bg-rose-500/20 text-rose-400 border border-rose-500/30 hover:bg-rose-500/30 transition-all flex items-center justify-center gap-2"
                        >
                            <Square size={14} />
                            Stop
                        </button>
                        <button
                            onClick={() => onAction(container.id, "restart")}
                            disabled={isLoading}
                            className="flex-1 px-4 py-2 rounded-xl font-black uppercase tracking-wider text-xs bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/30 transition-all flex items-center justify-center gap-2"
                        >
                            <RefreshCw size={14} />
                            Restart
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}

function NetworkCard({ network }: { network: NetworkInterface }) {
    const formatBytes = (bytes: number) => {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
    };

    return (
        <div className="bg-[#0a0e1a]/60 border border-white/5 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-cyan-500/20 text-cyan-400">
                    <Network size={20} />
                </div>
                <h3 className="font-black text-white">{network.name}</h3>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                    <p className="text-gray-500 uppercase tracking-wider mb-1">RX Bytes</p>
                    <p className="text-emerald-400 font-mono font-bold">{formatBytes(network.rx_bytes)}</p>
                </div>
                <div>
                    <p className="text-gray-500 uppercase tracking-wider mb-1">TX Bytes</p>
                    <p className="text-cyan-400 font-mono font-bold">{formatBytes(network.tx_bytes)}</p>
                </div>
                <div>
                    <p className="text-gray-500 uppercase tracking-wider mb-1">RX Packets</p>
                    <p className="text-white font-mono">{network.rx_packets.toLocaleString()}</p>
                </div>
                <div>
                    <p className="text-gray-500 uppercase tracking-wider mb-1">TX Packets</p>
                    <p className="text-white font-mono">{network.tx_packets.toLocaleString()}</p>
                </div>
            </div>
        </div>
    );
}

function QuickCommand({ label, command, onClick }: { label: string; command: string; onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className="bg-[#0a0e1a]/60 border border-emerald-500/20 rounded-xl p-3 hover:bg-emerald-500/10 hover:border-emerald-500/40 transition-all text-left"
        >
            <p className="text-xs font-black text-emerald-400 uppercase tracking-wider mb-1">{label}</p>
            <p className="text-xs text-gray-400 font-mono">{command}</p>
        </button>
    );
}

function LogLine({ log }: { log: LogEntry }) {
    const levelColor = {
        ERROR: "text-rose-400",
        WARN: "text-amber-400",
        INFO: "text-cyan-400",
        DEBUG: "text-gray-400"
    }[log.level] || "text-white";

    return (
        <div className="flex gap-3 hover:bg-white/5 px-2 py-1 rounded">
            <span className="text-gray-500">{log.timestamp}</span>
            <span className={`${levelColor} font-bold w-16`}>{log.level}</span>
            <span className="text-purple-400 w-32">{log.service}</span>
            <span className="text-gray-300 flex-1">{log.message}</span>
        </div>
    );
}
