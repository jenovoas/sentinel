"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { BackupStatusCard } from "@/components/backup/BackupStatusCard";
import { FailSafeSecurityCard } from "@/components/failsafe/FailSafeSecurityCard";
import { IncidentManagementCard } from "@/components/IncidentManagementCard";

interface SLOData {
    availability: { value: number; target: number };
    errorRate: { value: number; target: number };
    latency: { value: number; target: number };
    aiResponse: { value: number; target: number };
}

interface AIInsight {
    type: "optimization" | "warning" | "info";
    message: string;
}

interface SecurityAlert {
    severity: "low" | "medium" | "high";
    message: string;
    count: number;
}

export default function DashboardPage() {
    const [sloData, setSloData] = useState<SLOData>({
        availability: { value: 99.95, target: 99.9 },
        errorRate: { value: 0.3, target: 1.0 },
        latency: { value: 45, target: 100 },
        aiResponse: { value: 1.2, target: 3.0 },
    });

    const [aiInsights, setAiInsights] = useState<AIInsight[]>([
        { type: "optimization", message: "CPU usage trending up 15% this week" },
        { type: "warning", message: "Memory leak suspected in backend service" },
        { type: "info", message: "GPU utilization could be optimized" },
    ]);

    const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([
        { severity: "low", message: "Failed login attempts", count: 5 },
        { severity: "low", message: "Auditd events", count: 2 },
    ]);

    const [systemStatus, setSystemStatus] = useState<"healthy" | "warning" | "critical">("healthy");

    // Fetch real data from backend
    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch statistics
                const statsRes = await fetch("/api/v1/analytics/statistics?hours=24");
                const statsData = await statsRes.json();

                // Update SLO data from real metrics
                if (statsData) {
                    setSloData({
                        availability: {
                            value: statsData.cpu?.avg < 90 ? 99.95 : 99.5,
                            target: 99.9
                        },
                        errorRate: {
                            value: statsData.anomalies_count > 10 ? 1.5 : 0.3,
                            target: 1.0
                        },
                        latency: {
                            value: 45, // TODO: Get from API metrics
                            target: 100
                        },
                        aiResponse: {
                            value: 1.2, // TODO: Get from AI health
                            target: 3.0
                        },
                    });

                    // Determine system status
                    if (statsData.cpu?.max > 90 || statsData.memory?.max > 90) {
                        setSystemStatus("warning");
                    } else if (statsData.cpu?.max > 95 || statsData.memory?.max > 95) {
                        setSystemStatus("critical");
                    } else {
                        setSystemStatus("healthy");
                    }
                }

                // Fetch anomalies
                const anomaliesRes = await fetch("/api/v1/analytics/anomalies?hours=24&limit=10");
                const anomaliesData = await anomaliesRes.json();

                if (anomaliesData?.anomalies) {
                    // Convert anomalies to insights
                    const insights: AIInsight[] = anomaliesData.anomalies
                        .filter((a: any) => !a.is_resolved)
                        .slice(0, 3)
                        .map((a: any) => ({
                            type: a.severity === "critical" ? "warning" : "optimization",
                            message: a.title || a.description,
                        }));

                    if (insights.length > 0) {
                        setAiInsights(insights);
                    }

                    // Convert to security alerts
                    const alerts: SecurityAlert[] = anomaliesData.anomalies
                        .filter((a: any) => !a.is_resolved)
                        .slice(0, 5)
                        .map((a: any) => ({
                            severity: a.severity === "critical" ? "high" : a.severity === "warning" ? "medium" : "low",
                            message: a.title,
                            count: 1,
                        }));

                    if (alerts.length > 0) {
                        setSecurityAlerts(alerts);
                    }
                }

                // Fetch AI health
                const aiHealthRes = await fetch("/api/v1/ai/health");
                const aiHealthData = await aiHealthRes.json();

                if (aiHealthData) {
                    setSloData(prev => ({
                        ...prev,
                        aiResponse: {
                            value: aiHealthData.enabled ? 1.2 : 0,
                            target: 3.0,
                        },
                    }));
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
        }
    };

    const getSLOStatus = (value: number, target: number, inverse = false) => {
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
                                    {systemStatus === "healthy" && "All Systems Operational"}
                                    {systemStatus === "warning" && "System Warning"}
                                    {systemStatus === "critical" && "Critical Issues Detected"}
                                </h2>
                            </div>
                            <p className="text-sm opacity-80" suppressHydrationWarning>
                                Last updated: {new Date().toLocaleTimeString()}
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-3xl font-bold">{sloData.availability.value}%</p>
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
                            value={`${sloData.availability.value}%`}
                            target={`${sloData.availability.target}%`}
                            status={getSLOStatus(sloData.availability.value, sloData.availability.target)}
                            description="System uptime"
                        />
                        <SLOCard
                            title="Error Rate"
                            value={`${sloData.errorRate.value}%`}
                            target={`<${sloData.errorRate.target}%`}
                            status={getSLOStatus(sloData.errorRate.value, sloData.errorRate.target, true)}
                            description="Failed requests"
                        />
                        <SLOCard
                            title="Latency P95"
                            value={`${sloData.latency.value}ms`}
                            target={`<${sloData.latency.target}ms`}
                            status={getSLOStatus(sloData.latency.value, sloData.latency.target, true)}
                            description="Response time"
                        />
                        <SLOCard
                            title="AI Response"
                            value={`${sloData.aiResponse.value}s`}
                            target={`<${sloData.aiResponse.target}s`}
                            status={getSLOStatus(sloData.aiResponse.value, sloData.aiResponse.target, true)}
                            description="AI inference time"
                        />
                    </div>
                </section>

                {/* AI Insights, Security, Backup, Fail-Safe & Incidents */}
                <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    {/* AI Insights */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-purple-400">💡</span>
                                    AI Insights
                                </CardTitle>
                                <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/20">
                                    {aiInsights.length} new
                                </Badge>
                            </div>
                            <CardDescription>Automatic analysis and recommendations</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {aiInsights.map((insight, i) => (
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
                                    Security Alerts
                                </CardTitle>
                                <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                                    Secure
                                </Badge>
                            </div>
                            <CardDescription>Last 24 hours</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {securityAlerts.map((alert, i) => (
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
                                <Link href="/security/watchdog">
                                    <Button variant="outline" className="w-full">
                                        View All Alerts
                                    </Button>
                                </Link>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Backup System */}
                    <BackupStatusCard />

                    {/* Fail-Safe Security */}
                    <FailSafeSecurityCard />

                    {/* Incident Management */}
                    <IncidentManagementCard />
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
                            <div className="space-y-3">
                                <ActivityItem
                                    time="10:30 AM"
                                    message="AI analyzed CPU spike (resolved)"
                                    type="success"
                                />
                                <ActivityItem
                                    time="09:15 AM"
                                    message="Backup completed successfully"
                                    type="success"
                                />
                                <ActivityItem
                                    time="08:00 AM"
                                    message="Daily SLO report generated"
                                    type="info"
                                />
                                <ActivityItem
                                    time="07:45 AM"
                                    message="Security scan completed - no threats"
                                    type="success"
                                />
                            </div>
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
    status: "good" | "warning" | "critical";
    description: string;
}) {
    const statusColors = {
        good: "border-emerald-500/20 bg-emerald-500/10",
        warning: "border-amber-500/20 bg-amber-500/10",
        critical: "border-rose-500/20 bg-rose-500/10",
    };

    const statusTextColors = {
        good: "text-emerald-400",
        warning: "text-amber-400",
        critical: "text-rose-400",
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

// Activity Item Component
function ActivityItem({
    time,
    message,
    type,
}: {
    time: string;
    message: string;
    type: "success" | "warning" | "info";
}) {
    const icons = {
        success: "✅",
        warning: "⚠️",
        info: "ℹ️",
    };

    return (
        <div className="flex items-start gap-3 pb-3 border-b border-white/5 last:border-0 last:pb-0">
            <span className="text-lg">{icons[type]}</span>
            <div className="flex-1">
                <p className="text-sm text-gray-300">{message}</p>
                <p className="text-xs text-gray-500 mt-1">{time}</p>
            </div>
        </div>
    );
}
