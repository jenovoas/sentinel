"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

type MetricTab = "overview" | "host" | "database" | "network" | "ai";

type MetricSample = {
    sampled_at: string;
    cpu_percent: number | null;
    memory_percent: number | null;
    memory_used_mb: number | null;
    gpu_percent: number | null;
    network_bytes_sent: number | null;
    network_bytes_recv: number | null;
    db_connections_active: number | null;
    db_locks: number | null;
};

type MetricsResponse = {
    available: boolean;
    persisted: boolean;
    sample_count: number;
    retention_capacity: number;
    samples: MetricSample[];
};

export default function MetricsPage() {
    const [activeTab, setActiveTab] = useState<MetricTab>("overview");
    const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;
        const loadMetrics = async () => {
            try {
                const response = await fetch("/api/v1/analytics/metrics/recent?hours=24&limit=200", { cache: "no-store" });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const result = (await response.json()) as MetricsResponse;
                if (!active) return;
                setMetrics(result);
                setError(null);
            } catch (err) {
                if (!active) return;
                setError(err instanceof Error ? err.message : "No se pudieron cargar las métricas");
            } finally {
                if (active) setLoading(false);
            }
        };

        void loadMetrics();
        const intervalId = window.setInterval(() => void loadMetrics(), 15_000);
        return () => {
            active = false;
            window.clearInterval(intervalId);
        };
    }, []);

    const tabs: { id: MetricTab; label: string; icon: string }[] = [
        { id: "overview", label: "Overview", icon: "📊" },
        { id: "host", label: "Host Metrics", icon: "🖥️" },
        { id: "database", label: "Database", icon: "🗄️" },
        { id: "network", label: "Network", icon: "🌐" },
        { id: "ai", label: "AI Performance", icon: "🤖" },
    ];

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

    const latestSample = metrics?.samples.length ? metrics.samples[metrics.samples.length - 1] : null;
    const metricRows: { label: string; value: number | null; unit: string }[] = (() => {
        switch (activeTab) {
            case "overview":
            case "host":
                return [
                    { label: "CPU", value: latestSample?.cpu_percent ?? null, unit: "%" },
                    { label: "Memoria", value: latestSample?.memory_percent ?? null, unit: "%" },
                    { label: "Memoria usada", value: latestSample?.memory_used_mb ?? null, unit: "MB" },
                    { label: "GPU", value: latestSample?.gpu_percent ?? null, unit: "%" },
                ];
            case "database":
                return [
                    { label: "Conexiones activas", value: latestSample?.db_connections_active ?? null, unit: "" },
                    { label: "Locks", value: latestSample?.db_locks ?? null, unit: "" },
                ];
            case "network":
                return [
                    { label: "Bytes enviados desde muestra anterior", value: latestSample?.network_bytes_sent ?? null, unit: "B" },
                    { label: "Bytes recibidos desde muestra anterior", value: latestSample?.network_bytes_recv ?? null, unit: "B" },
                ];
            case "ai":
                return [{ label: "GPU", value: latestSample?.gpu_percent ?? null, unit: "%" }];
        }
    })();

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
                                Muestras reales recolectadas por Cortex; las métricas no expuestas se indican como N/D.
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
                            <p className="text-cyan-400 font-semibold mb-1">Fuente: Cortex</p>
                            <p className="text-sm text-gray-300">
                                Esta vista consulta el historial en memoria de Cortex cada 15 segundos. El historial no es persistente;
                                GPU, base de datos y cualquier fuente sin muestra se muestran como N/D.
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
                        <div className="flex items-center justify-between gap-4">
                            <div>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-cyan-400">{tabs.find((tab) => tab.id === activeTab)?.icon}</span>
                                    {tabs.find((tab) => tab.id === activeTab)?.label}
                                </CardTitle>
                                <CardDescription>{getTabDescription(activeTab)}</CardDescription>
                            </div>
                            <div className="flex gap-2">
                                <Badge variant="outline" className={error
                                    ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                                    : "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"}>
                                    {loading ? "Cargando" : error ? "Cortex no disponible" : metrics?.available ? "Muestras disponibles" : "Sin muestras"}
                                </Badge>
                                <Badge variant="outline" className="bg-white/5 text-gray-400 border-white/10">
                                    Actualización: 15 s
                                </Badge>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {error && (
                            <p role="status" className="mb-4 rounded-lg border border-rose-500/20 bg-rose-500/10 p-3 text-sm text-rose-300">
                                No se pudo actualizar Cortex ({error}).{metrics ? " Se conserva la última respuesta válida." : ""}
                            </p>
                        )}
                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                            {metricRows.map((metric) => (
                                <div key={metric.label} className="rounded-lg border border-white/10 bg-slate-900/50 p-4">
                                    <p className="text-sm text-gray-400">{metric.label}</p>
                                    <p className="mt-2 font-mono text-2xl font-semibold text-cyan-300">
                                        {metric.value === null ? "N/D" : `${metric.value.toLocaleString()} ${metric.unit}`.trim()}
                                    </p>
                                </div>
                            ))}
                        </div>
                        <div className="mt-6 flex flex-wrap gap-x-6 gap-y-2 border-t border-white/10 pt-4 text-sm text-gray-400">
                            <span>Muestras recibidas: {metrics?.sample_count ?? "N/D"}</span>
                            <span>Última muestra: {latestSample ? new Date(latestSample.sampled_at).toLocaleString() : "N/D"}</span>
                            <span>Almacenamiento: {metrics ? (metrics.persisted ? "persistente" : "solo memoria; no persistente") : "N/D"}</span>
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Stats */}
                <div className="grid gap-4 md:grid-cols-4 mt-6">
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Muestras en memoria</p>
                            <p className="text-2xl font-semibold text-cyan-400">{metrics?.sample_count ?? "N/D"}</p>
                            <p className="text-xs text-gray-500 mt-1">Capacidad máxima: {metrics?.retention_capacity?.toLocaleString() ?? "N/D"}</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Persistencia</p>
                            <p className="text-2xl font-semibold text-gray-300">{metrics ? (metrics.persisted ? "Activa" : "No") : "N/D"}</p>
                            <p className="text-xs text-gray-500 mt-1">Historial volátil de Cortex</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Telemetría de GPU</p>
                            <p className="text-2xl font-semibold text-gray-400">{latestSample?.gpu_percent == null ? "N/D" : `${latestSample.gpu_percent}%`}</p>
                            <p className="text-xs text-gray-500 mt-1">No suministrada por Cortex</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Telemetría de DB</p>
                            <p className="text-2xl font-semibold text-gray-400">{latestSample?.db_connections_active == null ? "N/D" : latestSample.db_connections_active}</p>
                            <p className="text-xs text-gray-500 mt-1">Conexiones activas; N/D si no se informa</p>
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
                                access Grafana directly at <strong>localhost:3001</strong> (admin / REDACTED_PASSWORD).
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
