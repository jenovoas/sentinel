"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

type MetricTab = "overview" | "host" | "database" | "network" | "ai";

export default function MetricsPage() {
    const [activeTab, setActiveTab] = useState<MetricTab>("overview");

    const tabs: { id: MetricTab; label: string; icon: string }[] = [
        { id: "overview", label: "Overview", icon: "📊" },
        { id: "host", label: "Host Metrics", icon: "🖥️" },
        { id: "database", label: "Database", icon: "🗄️" },
        { id: "network", label: "Network", icon: "🌐" },
        { id: "ai", label: "AI Performance", icon: "🤖" },
    ];

    // Grafana dashboard URLs (adjust based on your actual dashboard IDs)
    const grafanaUrls: Record<MetricTab, string> = {
        overview: "http://localhost:3001/d/sentinel-overview/sentinel-overview?orgId=1&refresh=5s&kiosk",
        host: "http://localhost:3001/d/sentinel-host/host-metrics?orgId=1&refresh=5s&kiosk",
        database: "http://localhost:3001/d/sentinel-db/database-metrics?orgId=1&refresh=5s&kiosk",
        network: "http://localhost:3001/d/sentinel-network/network-metrics?orgId=1&refresh=5s&kiosk",
        ai: "http://localhost:3001/d/sentinel-ai/ai-performance?orgId=1&refresh=5s&kiosk",
    };

    const getTabDescription = (tab: MetricTab): string => {
        switch (tab) {
            case "overview":
                return "High-level system health and performance metrics";
            case "host":
                return "CPU, Memory, Disk, and GPU utilization";
            case "database":
                return "PostgreSQL connections, queries, and performance";
            case "network":
                return "Network traffic, latency, and throughput";
            case "ai":
                return "Ollama inference latency and GPU utilization";
        }
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
            <div
                className="absolute inset-0 opacity-50 blur-3xl bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(14,165,233,0.12),transparent_30%)]"
                aria-hidden
            />

            <div className="relative mx-auto max-w-[1800px] px-6 py-10">
                {/* Header */}
                <header className="mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm uppercase tracking-[0.25em] text-cyan-200/70">Sentinel Metrics</p>
                            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">
                                Technical Metrics
                            </h1>
                            <p className="text-gray-300 mt-2 max-w-2xl">
                                Detailed performance metrics powered by Grafana
                            </p>
                        </div>
                        <Link href="/dashboard">
                            <Button variant="outline">← Back to Dashboard</Button>
                        </Link>
                    </div>
                </header>

                {/* Info Banner */}
                <div className="mb-6 bg-cyan-500/10 border border-cyan-500/20 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <span className="text-2xl">ℹ️</span>
                        <div>
                            <p className="text-cyan-400 font-semibold mb-1">Embedded Grafana Dashboards</p>
                            <p className="text-sm text-gray-300">
                                These dashboards are embedded from your Grafana instance running on port 3001.
                                For full functionality and customization, visit{" "}
                                <a
                                    href="http://localhost:3001"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-cyan-400 hover:text-cyan-300 underline"
                                >
                                    Grafana directly
                                </a>.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="mb-6">
                    <div className="flex gap-2 overflow-x-auto pb-2">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`
                  flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap
                  ${activeTab === tab.id
                                        ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                                        : "bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10"
                                    }
                `}
                            >
                                <span>{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Dashboard Card */}
                <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-cyan-400">
                                        {tabs.find((t) => t.id === activeTab)?.icon}
                                    </span>
                                    {tabs.find((t) => t.id === activeTab)?.label}
                                </CardTitle>
                                <CardDescription>{getTabDescription(activeTab)}</CardDescription>
                            </div>
                            <div className="flex gap-2">
                                <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                                    Live
                                </Badge>
                                <Badge variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20">
                                    5s refresh
                                </Badge>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {/* Temporary: Direct links until dashboards are created */}
                        <div className="relative w-full bg-slate-900/50 rounded-lg overflow-hidden border border-white/10 p-12">
                            <div className="text-center space-y-6">
                                <div className="text-6xl">📊</div>
                                <div>
                                    <h3 className="text-2xl font-semibold text-white mb-2">
                                        Grafana Dashboard: {tabs.find((t) => t.id === activeTab)?.label}
                                    </h3>
                                    <p className="text-gray-400 mb-6">
                                        {getTabDescription(activeTab)}
                                    </p>
                                </div>

                                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 max-w-2xl mx-auto">
                                    <p className="text-yellow-400 font-semibold mb-2">⚠️ Dashboard Not Yet Created</p>
                                    <p className="text-sm text-gray-300">
                                        This dashboard needs to be created in Grafana first.
                                        Click below to open Grafana and create the <strong>{activeTab}</strong> dashboard.
                                    </p>
                                </div>

                                <div className="flex gap-4 justify-center">
                                    <a
                                        href="http://localhost:3001"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="px-6 py-3 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-lg hover:bg-cyan-500/30 transition-all font-medium"
                                    >
                                        Open Grafana →
                                    </a>
                                    <a
                                        href="http://localhost:9090"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="px-6 py-3 bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded-lg hover:bg-orange-500/30 transition-all font-medium"
                                    >
                                        Open Prometheus →
                                    </a>
                                </div>

                                <div className="text-left bg-slate-800/50 rounded-lg p-4 max-w-2xl mx-auto">
                                    <p className="text-sm text-gray-400 mb-2 font-semibold">Quick Setup:</p>
                                    <ol className="text-sm text-gray-300 space-y-1 list-decimal list-inside">
                                        <li>Open Grafana (admin / admin)</li>
                                        <li>Add Prometheus data source (http://prometheus:9090)</li>
                                        <li>Create new dashboard</li>
                                        <li>Add panels with Prometheus queries</li>
                                        <li>Save with ID: <code className="bg-slate-700 px-2 py-0.5 rounded">sentinel-{activeTab}</code></li>
                                    </ol>
                                </div>
                            </div>
                        </div>

                        {/* Fallback message */}
                        <div className="mt-4 text-center">
                            <p className="text-sm text-gray-400">
                                Need help creating dashboards?{" "}
                                <a
                                    href="https://grafana.com/docs/grafana/latest/dashboards/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-cyan-400 hover:text-cyan-300 underline"
                                >
                                    View Grafana Documentation
                                </a>
                            </p>
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Stats */}
                <div className="grid gap-4 md:grid-cols-4 mt-6">
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Prometheus</p>
                            <p className="text-2xl font-semibold text-emerald-400">✅ Active</p>
                            <p className="text-xs text-gray-500 mt-1">Scraping every 15s</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Grafana</p>
                            <p className="text-2xl font-semibold text-emerald-400">✅ Online</p>
                            <p className="text-xs text-gray-500 mt-1">Port 3001</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Loki</p>
                            <p className="text-2xl font-semibold text-emerald-400">✅ Ready</p>
                            <p className="text-xs text-gray-500 mt-1">Log aggregation</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Data Retention</p>
                            <p className="text-2xl font-semibold text-cyan-400">15d</p>
                            <p className="text-xs text-gray-500 mt-1">Metrics stored</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Info Footer */}
                <div className="mt-8 bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <span className="text-2xl">💡</span>
                        <div>
                            <p className="text-blue-400 font-semibold mb-1">About These Metrics</p>
                            <p className="text-sm text-gray-300">
                                Sentinel uses Prometheus for metrics collection, Grafana for visualization, and Loki for log aggregation.
                                All metrics are scraped every 15 seconds and stored for 15 days. For custom dashboards and advanced queries,
                                access Grafana directly at <strong>localhost:3001</strong> (admin / darkfenix).
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
