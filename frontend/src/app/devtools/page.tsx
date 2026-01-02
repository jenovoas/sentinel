"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
    Terminal,
    Zap,
    Activity,
    FileCode,
    PlayCircle,
    CheckCircle2,
    XCircle,
    Clock,
    BarChart3,
    Code2,
    Cpu,
    Database,
    Network,
    AlertTriangle
} from "lucide-react";

interface TestResult {
    name: string;
    status: "pass" | "fail" | "running";
    duration: number;
    message?: string;
}

interface PerformanceMetric {
    endpoint: string;
    latency_ms: number;
    status_code: number;
    timestamp: number;
}

export default function DevToolsPage() {
    const [activeTab, setActiveTab] = useState<"testing" | "profiling" | "docs">("testing");
    const [testResults, setTestResults] = useState<TestResult[]>([]);
    const [isRunningTests, setIsRunningTests] = useState(false);
    const [perfMetrics, setPerfMetrics] = useState<PerformanceMetric[]>([]);
    const [isProfiling, setIsProfiling] = useState(false);

    // Simulated test execution
    const runTests = async () => {
        setIsRunningTests(true);
        setTestResults([]);

        const tests = [
            { name: "Health Endpoint", endpoint: "/api/v1/health" },
            { name: "Dashboard Status", endpoint: "/api/v1/dashboard/status" },
            { name: "AI Health Check", endpoint: "/api/v1/ai/health" },
            { name: "TruthSync Health", endpoint: "/api/v1/truthsync/health" },
        ];

        for (const test of tests) {
            const start = Date.now();

            try {
                const response = await fetch(`http://localhost:8000${test.endpoint}`);
                const duration = Date.now() - start;

                setTestResults(prev => [...prev, {
                    name: test.name,
                    status: response.ok ? "pass" : "fail",
                    duration,
                    message: response.ok ? `HTTP ${response.status}` : `Failed: HTTP ${response.status}`
                }]);
            } catch (error) {
                setTestResults(prev => [...prev, {
                    name: test.name,
                    status: "fail",
                    duration: Date.now() - start,
                    message: `Error: ${error}`
                }]);
            }

            await new Promise(resolve => setTimeout(resolve, 500));
        }

        setIsRunningTests(false);
    };

    // Performance profiling
    const startProfiling = () => {
        setIsProfiling(true);
        setPerfMetrics([]);

        const interval = setInterval(async () => {
            const start = Date.now();
            try {
                const response = await fetch("http://localhost:8000/api/v1/health");
                const latency = Date.now() - start;

                setPerfMetrics(prev => [...prev.slice(-20), {
                    endpoint: "/api/v1/health",
                    latency_ms: latency,
                    status_code: response.status,
                    timestamp: Date.now()
                }]);
            } catch (error) {
                console.error("Profiling error:", error);
            }
        }, 2000);

        // Auto-stop after 60 seconds
        setTimeout(() => {
            clearInterval(interval);
            setIsProfiling(false);
        }, 60000);
    };

    const stopProfiling = () => {
        setIsProfiling(false);
    };

    const avgLatency = perfMetrics.length > 0
        ? perfMetrics.reduce((sum, m) => sum + m.latency_ms, 0) / perfMetrics.length
        : 0;

    const p95Latency = perfMetrics.length > 0
        ? perfMetrics.map(m => m.latency_ms).sort((a, b) => a - b)[Math.floor(perfMetrics.length * 0.95)]
        : 0;

    return (
        <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-purple-500/30 overflow-hidden relative font-sans">
            {/* Visual Identity Layer */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-500/10 blur-[150px] rounded-full animate-pulse" />
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
                        <div className="h-[3px] w-12 bg-gradient-to-r from-purple-500 to-transparent rounded-full" />
                        <p className="text-[10px] uppercase tracking-[0.6em] text-purple-400 font-black">
                            Sentinel DevTools OS // Advanced Testing Suite 0x8F92A
                        </p>
                    </motion.div>

                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
                        Developer <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-white to-cyan-500">Tools</span> Matrix
                    </h1>

                    <div className="flex flex-wrap gap-8 mt-8 items-center">
                        <div className="flex items-center gap-3">
                            <Terminal className="w-4 h-4 text-cyan-400 animate-pulse" />
                            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest italic">
                                Mode: <span className="text-white">Professional Testing</span>
                            </p>
                        </div>
                    </div>
                </header>

                {/* Tab Navigation */}
                <div className="flex gap-4 mb-12">
                    <TabButton
                        active={activeTab === "testing"}
                        onClick={() => setActiveTab("testing")}
                        icon={<PlayCircle size={18} />}
                        label="API Testing"
                    />
                    <TabButton
                        active={activeTab === "profiling"}
                        onClick={() => setActiveTab("profiling")}
                        icon={<BarChart3 size={18} />}
                        label="Performance Profiling"
                    />
                    <TabButton
                        active={activeTab === "docs"}
                        onClick={() => setActiveTab("docs")}
                        icon={<FileCode size={18} />}
                        label="API Documentation"
                    />
                </div>

                {/* Testing Tab */}
                {activeTab === "testing" && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Control Panel */}
                        <div className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">
                                        Test Suite Control
                                    </h2>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
                                        Automated API endpoint validation
                                    </p>
                                </div>
                                <button
                                    onClick={runTests}
                                    disabled={isRunningTests}
                                    className={`px-8 py-4 rounded-2xl font-black uppercase tracking-wider text-sm transition-all ${isRunningTests
                                            ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                                            : "bg-gradient-to-r from-purple-500 to-cyan-500 text-white hover:shadow-2xl hover:shadow-purple-500/50"
                                        }`}
                                >
                                    {isRunningTests ? (
                                        <span className="flex items-center gap-2">
                                            <Activity className="animate-spin" size={16} />
                                            Running Tests...
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            <PlayCircle size={16} />
                                            Run Test Suite
                                        </span>
                                    )}
                                </button>
                            </div>

                            {/* Test Results */}
                            <div className="space-y-3">
                                {testResults.length === 0 && !isRunningTests && (
                                    <div className="text-center py-12 text-gray-500">
                                        <Terminal size={48} className="mx-auto mb-4 opacity-20" />
                                        <p className="text-sm uppercase tracking-widest">No tests run yet</p>
                                    </div>
                                )}

                                {testResults.map((result, index) => (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        className="bg-[#0a0e1a]/60 border border-white/5 rounded-2xl p-6 flex items-center justify-between"
                                    >
                                        <div className="flex items-center gap-4">
                                            {result.status === "pass" && <CheckCircle2 className="text-emerald-400" size={24} />}
                                            {result.status === "fail" && <XCircle className="text-rose-400" size={24} />}
                                            {result.status === "running" && <Activity className="text-cyan-400 animate-spin" size={24} />}

                                            <div>
                                                <p className="font-black text-white">{result.name}</p>
                                                <p className="text-xs text-gray-500 uppercase tracking-wider">
                                                    {result.message}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2 text-gray-400">
                                            <Clock size={14} />
                                            <span className="text-sm font-mono">{result.duration}ms</span>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Test Statistics */}
                        {testResults.length > 0 && (
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                <StatCard
                                    label="Total Tests"
                                    value={testResults.length}
                                    icon={<Terminal />}
                                    color="text-cyan-400"
                                />
                                <StatCard
                                    label="Passed"
                                    value={testResults.filter(t => t.status === "pass").length}
                                    icon={<CheckCircle2 />}
                                    color="text-emerald-400"
                                />
                                <StatCard
                                    label="Failed"
                                    value={testResults.filter(t => t.status === "fail").length}
                                    icon={<XCircle />}
                                    color="text-rose-400"
                                />
                                <StatCard
                                    label="Avg Latency"
                                    value={`${Math.round(testResults.reduce((sum, t) => sum + t.duration, 0) / testResults.length)}ms`}
                                    icon={<Zap />}
                                    color="text-purple-400"
                                />
                            </div>
                        )}
                    </motion.div>
                )}

                {/* Profiling Tab */}
                {activeTab === "profiling" && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        {/* Profiling Control */}
                        <div className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8">
                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">
                                        Performance Profiler
                                    </h2>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
                                        Real-time latency monitoring
                                    </p>
                                </div>
                                <button
                                    onClick={isProfiling ? stopProfiling : startProfiling}
                                    className={`px-8 py-4 rounded-2xl font-black uppercase tracking-wider text-sm transition-all ${isProfiling
                                            ? "bg-rose-500 text-white hover:bg-rose-600"
                                            : "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-2xl hover:shadow-emerald-500/50"
                                        }`}
                                >
                                    {isProfiling ? (
                                        <span className="flex items-center gap-2">
                                            <Activity className="animate-pulse" size={16} />
                                            Stop Profiling
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            <PlayCircle size={16} />
                                            Start Profiling
                                        </span>
                                    )}
                                </button>
                            </div>

                            {/* Real-time Metrics */}
                            {perfMetrics.length > 0 && (
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                                    <MetricCard
                                        label="Avg Latency"
                                        value={`${avgLatency.toFixed(2)}ms`}
                                        icon={<Zap />}
                                        color="text-cyan-400"
                                    />
                                    <MetricCard
                                        label="P95 Latency"
                                        value={`${p95Latency.toFixed(2)}ms`}
                                        icon={<BarChart3 />}
                                        color="text-purple-400"
                                    />
                                    <MetricCard
                                        label="Samples"
                                        value={perfMetrics.length}
                                        icon={<Activity />}
                                        color="text-emerald-400"
                                    />
                                </div>
                            )}

                            {/* Latency Chart */}
                            <div className="bg-[#0a0e1a]/60 border border-white/5 rounded-2xl p-6">
                                <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-4">
                                    Latency Timeline
                                </h3>
                                <div className="h-64 flex items-end gap-1">
                                    {perfMetrics.length === 0 ? (
                                        <div className="w-full h-full flex items-center justify-center text-gray-500">
                                            <div className="text-center">
                                                <BarChart3 size={48} className="mx-auto mb-4 opacity-20" />
                                                <p className="text-sm uppercase tracking-widest">Start profiling to see data</p>
                                            </div>
                                        </div>
                                    ) : (
                                        perfMetrics.map((metric, index) => {
                                            const maxLatency = Math.max(...perfMetrics.map(m => m.latency_ms));
                                            const height = (metric.latency_ms / maxLatency) * 100;
                                            const color = metric.latency_ms > 100 ? "bg-rose-500" : metric.latency_ms > 50 ? "bg-amber-500" : "bg-emerald-500";

                                            return (
                                                <div
                                                    key={index}
                                                    className={`flex-1 ${color} rounded-t opacity-70 hover:opacity-100 transition-all`}
                                                    style={{ height: `${height}%` }}
                                                    title={`${metric.latency_ms.toFixed(2)}ms`}
                                                />
                                            );
                                        })
                                    )}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Documentation Tab */}
                {activeTab === "docs" && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[30px] p-8"
                    >
                        <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic mb-6">
                            API Documentation
                        </h2>

                        <div className="space-y-6">
                            <EndpointDoc
                                method="GET"
                                endpoint="/api/v1/health"
                                description="Get system health status"
                                response={{
                                    status: "healthy",
                                    uptime_seconds: 3600.5,
                                    components: {
                                        database: { status: "healthy" },
                                        redis: { status: "healthy" },
                                        ollama: { status: "healthy" }
                                    }
                                }}
                            />

                            <EndpointDoc
                                method="GET"
                                endpoint="/api/v1/dashboard/status"
                                description="Get detailed system metrics"
                                response={{
                                    cpu: "15.2",
                                    memory: "42.8",
                                    coherence: 0.96,
                                    entropy: 0.073
                                }}
                            />

                            <EndpointDoc
                                method="POST"
                                endpoint="/api/v1/ai/query"
                                description="Query AI model"
                                request={{
                                    prompt: "Explain quantum computing",
                                    max_tokens: 100,
                                    temperature: 0.3
                                }}
                                response={{
                                    response: "Quantum computing uses quantum mechanical phenomena...",
                                    model: "phi3:mini",
                                    enabled: true
                                }}
                            />
                        </div>

                        <div className="mt-8 p-6 bg-cyan-500/10 border border-cyan-500/20 rounded-2xl">
                            <p className="text-sm text-cyan-400 font-black uppercase tracking-wider">
                                📚 Full API documentation available at:
                            </p>
                            <code className="text-white font-mono text-sm block mt-2">
                                http://localhost:8000/docs
                            </code>
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
                    ? "bg-gradient-to-r from-purple-500 to-cyan-500 text-white shadow-2xl shadow-purple-500/50"
                    : "bg-slate-900/40 text-gray-400 hover:text-white border border-white/5"
                }`}
        >
            {icon}
            {label}
        </button>
    );
}

function StatCard({ label, value, icon, color }: { label: string; value: number | string; icon: React.ReactNode; color: string }) {
    return (
        <div className="bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[20px] p-6">
            <div className={`${color} mb-3`}>{icon}</div>
            <p className="text-3xl font-black text-white font-mono">{value}</p>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">{label}</p>
        </div>
    );
}

function MetricCard({ label, value, icon, color }: { label: string; value: string; icon: React.ReactNode; color: string }) {
    return (
        <div className="bg-[#0a0e1a]/60 border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-3">
                <div className={color}>{icon}</div>
                <p className="text-2xl font-black text-white font-mono">{value}</p>
            </div>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">{label}</p>
        </div>
    );
}

function EndpointDoc({ method, endpoint, description, request, response }: {
    method: string;
    endpoint: string;
    description: string;
    request?: any;
    response: any;
}) {
    const methodColor = method === "GET" ? "text-emerald-400" : method === "POST" ? "text-cyan-400" : "text-purple-400";

    return (
        <div className="bg-[#0a0e1a]/60 border border-white/5 rounded-2xl p-6">
            <div className="flex items-center gap-4 mb-3">
                <span className={`${methodColor} font-black text-sm px-3 py-1 bg-white/5 rounded-lg`}>
                    {method}
                </span>
                <code className="text-white font-mono text-sm">{endpoint}</code>
            </div>
            <p className="text-gray-400 text-sm mb-4">{description}</p>

            {request && (
                <div className="mb-4">
                    <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">Request:</p>
                    <pre className="bg-black/40 p-4 rounded-xl text-xs text-cyan-400 overflow-x-auto">
                        {JSON.stringify(request, null, 2)}
                    </pre>
                </div>
            )}

            <div>
                <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">Response:</p>
                <pre className="bg-black/40 p-4 rounded-xl text-xs text-emerald-400 overflow-x-auto">
                    {JSON.stringify(response, null, 2)}
                </pre>
            </div>
        </div>
    );
}
