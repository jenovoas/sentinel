"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { BackupStatusCard } from "@/components/backup/BackupStatusCard";
import { FailSafeSecurityCard } from "@/components/failsafe/FailSafeSecurityCard";

interface SLOData {
    availability: { value: number | null; target: number };
    errorRate: { value: number | null; target: number };
    latency: { value: number | null; target: number };
    aiResponse: { value: number | null; target: number };
}

interface AIInsight {
    type: "optimization" | "warning" | "info";
    message: string;
}

interface ResourceAlert {
    severity: "low" | "medium" | "high";
    message: string;
    count: number;
}

interface SystemLog {
    timestamp: string;
    level: string;
    unit: string;
    message: string;
}

interface SystemLogsState {
    available: boolean;
    logs: SystemLog[];
}

export default function DashboardPage() {
    const [sloData] = useState<SLOData>({
        availability: { value: null, target: 99.9 },
        errorRate: { value: null, target: 1.0 },
        latency: { value: null, target: 100 },
        aiResponse: { value: null, target: 3.0 },
    });

    const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
    const [resourceAlerts, setResourceAlerts] = useState<ResourceAlert[]>([]);
    const [anomaliesAvailable, setAnomaliesAvailable] = useState(false);
    const [systemLogs, setSystemLogs] = useState<SystemLogsState>({ available: false, logs: [] });

    const [systemStatus, setSystemStatus] = useState<"healthy" | "warning" | "critical" | "unknown">("unknown");

    // Fetch real data from backend
    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch statistics
                const statsRes = await fetch("/api/v1/analytics/statistics?hours=24");
                const statsData = await statsRes.json();

                // SLOs remain unavailable until the backend provides measured history.
                if (statsData) {
                    const cpu = statsData.cpu?.current;
                    const memory = statsData.memory?.current;
                    if (typeof cpu === "number" && typeof memory === "number") {
                        if (cpu > 95 || memory > 95) {
                            setSystemStatus("critical");
                        } else if (cpu > 85 || memory > 85) {
                            setSystemStatus("warning");
                        } else {
                            setSystemStatus("healthy");
                        }
                    } else {
                        setSystemStatus("unknown");
                    }
                }

                // Fetch anomalies
                const anomaliesRes = await fetch("/api/v1/analytics/anomalies?limit=10", { cache: "no-store" });
                const anomaliesData = await anomaliesRes.json();

                const anomalyRecords = anomaliesData?.anomalies;
                const hasAnomalyData = anomaliesData?.available === true && Array.isArray(anomalyRecords);
                setAnomaliesAvailable(hasAnomalyData);

                if (hasAnomalyData) {
                    const currentBreaches = anomalyRecords;
                    setAiInsights(currentBreaches.slice(0, 3).map((a: any) => ({
                        type: "warning",
                        message: a.title || a.description,
                    })));
                    setResourceAlerts(currentBreaches.slice(0, 5).map((a: any) => ({
                        severity: a.severity === "critical" ? "high" : a.severity === "warning" ? "medium" : "low",
                        message: a.title,
                        count: 1,
                    })));
                } else {
                    setAiInsights([]);
                    setResourceAlerts([]);
                }

                try {
                    const logsRes = await fetch("/api/system-logs?limit=10", { cache: "no-store" });
                    const logsData = await logsRes.json();
                    setSystemLogs({
                        available: logsRes.ok && logsData?.available === true,
                        logs: logsRes.ok && Array.isArray(logsData?.logs) ? logsData.logs : [],
                    });
                } catch {
                    setSystemLogs({ available: false, logs: [] });
                }
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            }
        };

        fetchData();

        // Refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status: typeof systemStatus) => {
        switch (status) {
            case "healthy":
                return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
            case "warning":
                return "text-amber-400 bg-amber-500/10 border-amber-500/20";
            case "critical":
                return "text-rose-400 bg-rose-500/10 border-rose-500/20";
            case "unknown":
                return "text-gray-400 bg-gray-500/10 border-gray-500/20";
        }
    };

    const getStatusIcon = (status: typeof systemStatus) => {
        switch (status) {
            case "healthy":
                return "🟢";
            case "warning":
                return "🟡";
            case "critical":
                return "🔴";
            case "unknown":
                return "⚪";
        }
    };

    const getSLOStatus = (value: number | null, target: number, inverse = false) => {
        if (value === null || !Number.isFinite(value)) return "unavailable" as const;
        const ratio = inverse ? target / value : value / target;
        if (ratio >= 1.0) return "good";
        if (ratio >= 0.9) return "warning";
        return "critical";
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
            <div
                className="absolute inset-0 opacity-50 blur-3xl bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(16,185,129,0.12),transparent_30%),radial-gradient(circle_at_70%_80%,rgba(139,92,246,0.12),transparent_25%)]"
                aria-hidden
            />

            <div className="relative mx-auto max-w-7xl px-6 py-10">
                {/* Header */}
                <header className="mb-8">
                    <p className="text-sm uppercase tracking-[0.25em] text-cyan-200/70">Sentinel</p>
                    <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">
                        Executive Dashboard
                    </h1>
                    <p className="text-gray-300 mt-2 max-w-2xl">
                        Business-level insights powered by AI and real-time security monitoring
                    </p>
                </header>

                {/* System Status Hero */}
                <div className={`mb-8 rounded-2xl border p-6 ${getStatusColor(systemStatus)}`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <span className="text-4xl">{getStatusIcon(systemStatus)}</span>
                                <h2 className="text-2xl font-semibold">
                                    {systemStatus === "healthy" && "Resource Usage Normal"}
                                    {systemStatus === "warning" && "High Resource Usage"}
                                    {systemStatus === "critical" && "Critical Resource Usage"}
                                    {systemStatus === "unknown" && "Resource Status Unavailable"}
                                </h2>
                            </div>
                            <p className="text-sm opacity-80" suppressHydrationWarning>
                                Last updated: {new Date().toLocaleTimeString()}
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-3xl font-bold">
                                {sloData.availability.value === null ? "N/A" : `${sloData.availability.value}%`}
                            </p>
                            <p className="text-sm opacity-80">Uptime (Target: {sloData.availability.target}%)</p>
                        </div>
                    </div>
                </div>

                {/* SLO Cards */}
                <section className="mb-8">
                    <h2 className="text-2xl font-semibold text-white mb-4">Service Level Objectives</h2>
                    <div className="grid gap-4 md:grid-cols-4">
                        <SLOCard
                            title="Availability"
                            value={sloData.availability.value === null ? "N/A" : `${sloData.availability.value}%`}
                            target={`${sloData.availability.target}%`}
                            status={getSLOStatus(sloData.availability.value, sloData.availability.target)}
                            description="System uptime"
                        />
                        <SLOCard
                            title="Error Rate"
                            value={sloData.errorRate.value === null ? "N/A" : `${sloData.errorRate.value}%`}
                            target={`<${sloData.errorRate.target}%`}
                            status={getSLOStatus(sloData.errorRate.value, sloData.errorRate.target, true)}
                            description="Failed requests"
                        />
                        <SLOCard
                            title="Latency P95"
                            value={sloData.latency.value === null ? "N/A" : `${sloData.latency.value}ms`}
                            target={`<${sloData.latency.target}ms`}
                            status={getSLOStatus(sloData.latency.value, sloData.latency.target, true)}
                            description="Response time"
                        />
                        <SLOCard
                            title="AI Response"
                            value={sloData.aiResponse.value === null ? "N/A" : `${sloData.aiResponse.value}s`}
                            target={`<${sloData.aiResponse.target}s`}
                            status={getSLOStatus(sloData.aiResponse.value, sloData.aiResponse.target, true)}
                            description="AI inference time"
                        />
                    </div>
                </section>

                {/* AI Insights, Security, Backup & Fail-Safe */}
                <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    {/* AI Insights */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-purple-400">💡</span>
                                    Presión de recursos
                                </CardTitle>
                                <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/20">
                                    {aiInsights.length} new
                                </Badge>
                            </div>
                            <CardDescription>Alertas en tiempo actual basadas en umbrales de CPU y RAM</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {aiInsights.length === 0 ? (
                                    <p className="text-sm text-gray-400">
                                        {anomaliesAvailable ? "No active insights" : "Live insight data unavailable"}
                                    </p>
                                ) : aiInsights.map((insight, i) => (
                                    <div
                                        key={i}
                                        className={`rounded-lg p-3 border ${insight.type === "optimization"
                                            ? "bg-cyan-500/10 border-cyan-500/20"
                                            : insight.type === "warning"
                                                ? "bg-amber-500/10 border-amber-500/20"
                                                : "bg-blue-500/10 border-blue-500/20"
                                            }`}
                                    >
                                        <p className="text-sm text-gray-300">{insight.message}</p>
                                    </div>
                                ))}
                            </div>
                            <div className="mt-4">
                                <Link href="/ai/playground">
                                    <Button variant="outline" className="w-full">
                                        Ask AI for Details
                                    </Button>
                                </Link>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Security Alerts */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-rose-400">🔒</span>
                                    Alertas de recursos
                                </CardTitle>
                                <Badge
                                    variant="outline"
                                    className={anomaliesAvailable
                                        ? resourceAlerts.length === 0
                                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                            : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                        : "bg-gray-500/10 text-gray-400 border-gray-500/20"}
                                >
                                    {!anomaliesAvailable
                                        ? "Unavailable"
                                        : resourceAlerts.length === 0
                                            ? "No active alerts"
                                            : "Alerts active"}
                                </Badge>
                            </div>
                            <CardDescription>Lectura actual; el runtime no conserva historial de alertas</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {resourceAlerts.length === 0 && (
                                    <p className="text-sm text-gray-400">
                                        {anomaliesAvailable ? "No active alerts" : "Live alert data unavailable"}
                                    </p>
                                )}
                                {resourceAlerts.map((alert, i) => (
                                    <div
                                        key={i}
                                        className={`rounded-lg p-3 border flex items-center justify-between ${alert.severity === "high"
                                            ? "bg-rose-500/10 border-rose-500/20"
                                            : alert.severity === "medium"
                                                ? "bg-amber-500/10 border-amber-500/20"
                                                : "bg-slate-500/10 border-slate-500/20"
                                            }`}
                                    >
                                        <p className="text-sm text-gray-300">{alert.message}</p>
                                        <Badge
                                            variant="outline"
                                            className={
                                                alert.severity === "high"
                                                    ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
                                                    : alert.severity === "medium"
                                                        ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                                                        : "bg-slate-500/20 text-slate-400 border-slate-500/30"
                                            }
                                        >
                                            {alert.count}
                                        </Badge>
                                    </div>
                                ))}
                            </div>
                            <div className="mt-4">
                                <Link href="/analytics">
                                    <Button variant="outline" className="w-full">
                                        Ver métricas activas
                                    </Button>
                                </Link>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Backup System */}
                    <BackupStatusCard />

                    {/* Fail-Safe Security */}
                    <FailSafeSecurityCard />
                </section>

                {/* Quick Actions */}
                <section className="mb-8">
                    <h2 className="text-2xl font-semibold text-white mb-4">Quick Actions</h2>
                    <div className="grid gap-4 md:grid-cols-4">
                        <Link href="/ai/playground">
                            <Card className="bg-purple-500/10 backdrop-blur-xl border-purple-500/20 hover:bg-purple-500/20 transition-colors cursor-pointer">
                                <CardContent className="p-6 text-center">
                                    <span className="text-4xl mb-2 block">🤖</span>
                                    <p className="font-semibold text-purple-400">Ask AI</p>
                                    <p className="text-xs text-gray-400 mt-1">Query insights</p>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link href="/metrics/host">
                            <Card className="bg-cyan-500/10 backdrop-blur-xl border-cyan-500/20 hover:bg-cyan-500/20 transition-colors cursor-pointer">
                                <CardContent className="p-6 text-center">
                                    <span className="text-4xl mb-2 block">📊</span>
                                    <p className="font-semibold text-cyan-400">View Metrics</p>
                                    <p className="text-xs text-gray-400 mt-1">Detailed dashboards</p>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link href="/security/watchdog">
                            <Card className="bg-rose-500/10 backdrop-blur-xl border-rose-500/20 hover:bg-rose-500/20 transition-colors cursor-pointer">
                                <CardContent className="p-6 text-center">
                                    <span className="text-4xl mb-2 block">🔒</span>
                                    <p className="font-semibold text-rose-400">Security</p>
                                    <p className="text-xs text-gray-400 mt-1">Auditd watchdog</p>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link href="/analytics">
                            <Card className="bg-emerald-500/10 backdrop-blur-xl border-emerald-500/20 hover:bg-emerald-500/20 transition-colors cursor-pointer">
                                <CardContent className="p-6 text-center">
                                    <span className="text-4xl mb-2 block">📈</span>
                                    <p className="font-semibold text-emerald-400">Analytics</p>
                                    <p className="text-xs text-gray-400 mt-1">Historical data</p>
                                </CardContent>
                            </Card>
                        </Link>
                    </div>
                </section>

                {/* Recent Activity */}
                <section>
                    <h2 className="text-2xl font-semibold text-white mb-4">Recent Activity</h2>
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            {systemLogs.logs.length === 0 ? (
                                <p className="text-sm text-gray-400">
                                    {systemLogs.available ? "No recent system events" : "System log feed unavailable"}
                                </p>
                            ) : (
                                <div className="space-y-3">
                                    {systemLogs.logs.map((log, index) => {
                                        const level = log.level.toUpperCase();
                                        const isCritical = level === "CRITICAL" || level === "ERROR";
                                        const isWarning = level === "WARNING";
                                        return (
                                            <div
                                                key={`${log.timestamp}-${log.unit}-${index}`}
                                                className={`rounded-lg border p-3 ${isCritical
                                                    ? "bg-rose-500/10 border-rose-500/20"
                                                    : isWarning
                                                        ? "bg-amber-500/10 border-amber-500/20"
                                                        : "bg-slate-500/10 border-slate-500/20"
                                                    }`}
                                            >
                                                <div className="flex items-start justify-between gap-4">
                                                    <p className="text-sm text-gray-200">{log.message}</p>
                                                    <Badge variant="outline">{level}</Badge>
                                                </div>
                                                <p className="mt-1 text-xs text-gray-500">
                                                    {log.timestamp} · {log.unit}
                                                </p>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </section>
            </div>
        </main>
    );
}

// SLO Card Component
function SLOCard({
    title,
    value,
    target,
    status,
    description,
}: {
    title: string;
    value: string;
    target: string;
    status: "good" | "warning" | "critical" | "unavailable";
    description: string;
}) {
    const statusColors = {
        good: "border-emerald-500/20 bg-emerald-500/10",
        warning: "border-amber-500/20 bg-amber-500/10",
        critical: "border-rose-500/20 bg-rose-500/10",
        unavailable: "border-gray-500/20 bg-gray-500/10",
    };

    const statusTextColors = {
        good: "text-emerald-400",
        warning: "text-amber-400",
        critical: "text-rose-400",
        unavailable: "text-gray-400",
    };

    return (
        <Card className={`backdrop-blur-xl border ${statusColors[status]}`}>
            <CardContent className="p-6">
                <p className="text-sm text-gray-400 mb-1">{title}</p>
                <p className={`text-3xl font-semibold ${statusTextColors[status]} mb-2`}>{value}</p>
                <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">{description}</span>
                    <span className="text-gray-500">Target: {target}</span>
                </div>
            </CardContent>
        </Card>
    );
}
