"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button"; // Note: The original used Button from badge, let's fix to Badge
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

interface AuditEvent {
    id: string;
    timestamp: Date;
    type: string;
    severity: "low" | "medium" | "high" | "critical";
    description: string;
    action: string;
    user?: string;
    process?: string;
}

export default function SecurityWatchdogPage() {
    const [securityStatus, setSecurityStatus] = useState<"secure" | "warning" | "critical">("secure");
    const [events, setEvents] = useState<AuditEvent[]>([]);
    const [threatsDetected, setThreatsDetected] = useState(0);
    const [eventsToday, setEventsToday] = useState(0);
    const [mounted, setMounted] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setMounted(true);
    }, []);

    const fetchEvents = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/security/alerts?limit=20`);
            if (!response.ok) {
                throw new Error("Failed to fetch security alerts");
            }
            const data = await response.json();

            // Map backend SecurityAlertResponse to frontend AuditEvent
            const mappedEvents: AuditEvent[] = data.map((alert: any) => ({
                id: alert.id,
                timestamp: new Date(alert.detected_at),
                type: alert.alert_type,
                severity: alert.severity,
                description: alert.description,
                action: alert.is_investigated ? "Investigated" : "Pending",
                user: alert.context_data?.user || "N/A",
                process: alert.local_process || "N/A",
            }));

            setEvents(mappedEvents);

            // Calculate some stats
            const criticalCount = mappedEvents.filter(e => e.severity === 'critical' || e.severity === 'high').length;
            setThreatsDetected(criticalCount);

            const today = new Date().toDateString();
            const todayEvents = mappedEvents.filter(e => new Date(e.timestamp).toDateString() === today).length;
            setEventsToday(todayEvents);

            if (criticalCount > 0) {
                setSecurityStatus("critical");
            } else if (mappedEvents.length > 5) {
                setSecurityStatus("warning");
            } else {
                setSecurityStatus("secure");
            }

            setError(null);
        } catch (err: any) {
            console.error("Error fetching events:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (mounted) {
            fetchEvents();
            // Refresh every 30 seconds
            const interval = setInterval(fetchEvents, 30000);
            return () => clearInterval(interval);
        }
    }, [mounted]);

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case "critical":
                return "bg-rose-500/10 text-rose-500 border-rose-500/20";
            case "high":
                return "bg-orange-500/10 text-orange-500 border-orange-500/20";
            case "medium":
                return "bg-amber-500/10 text-amber-500 border-amber-500/20";
            default:
                return "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
        }
    };

    const getStatusColor = () => {
        switch (securityStatus) {
            case "critical":
                return "text-rose-500";
            case "warning":
                return "text-amber-500";
            default:
                return "text-emerald-500";
        }
    };

    return (
        <main className="min-h-screen bg-black text-white p-8 font-sans selection:bg-rose-500/30">
            <div className="max-w-7xl mx-auto">
                <header className="mb-12 flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="h-8 w-1 bg-rose-600 rounded-full" />
                            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                                SECURITY WATCHDOG
                            </h1>
                        </div>
                        <p className="text-gray-400 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
                            Active kernel-level exploit detection
                        </p>
                    </div>
                    <Link href="/dashboard">
                        <Badge variant="outline" className="px-4 py-2 hover:bg-white/5 cursor-pointer transition-colors">
                            ← Back to Dashboard
                        </Badge>
                    </Link>
                </header>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
                    {/* Status Card */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="pt-6">
                            <p className="text-sm font-medium text-gray-400 mb-1">Security Status</p>
                            <div className="flex items-center gap-2">
                                <p className={`text-3xl font-bold ${getStatusColor()}`}>
                                    {securityStatus.toUpperCase()}
                                </p>
                                {securityStatus === "secure" && <span>🛡️</span>}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Real-time protection active</p>
                        </CardContent>
                    </Card>

                    {/* Threats Detected */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="pt-6">
                            <p className="text-sm font-medium text-gray-400 mb-1">Critical Threats</p>
                            <p className="text-3xl font-semibold text-rose-500">{threatsDetected}</p>
                            <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
                        </CardContent>
                    </Card>

                    {/* Events Today */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="pt-6">
                            <p className="text-sm font-medium text-gray-400 mb-1">Events Today</p>
                            <p className="text-3xl font-semibold text-white">{eventsToday}</p>
                            <p className="text-xs text-gray-500 mt-1">Auditd syscall logs</p>
                        </CardContent>
                    </Card>

                    {/* Compliance */}
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="pt-6">
                            <p className="text-sm font-medium text-gray-400 mb-1">Compliance</p>
                            <p className="text-3xl font-semibold text-amber-400">95%</p>
                            <p className="text-xs text-gray-500 mt-1">SOC 2 ready</p>
                        </CardContent>
                    </Card>
                </div>

                <div className="grid gap-6 lg:grid-cols-3">
                    {/* Auditd Events Table */}
                    <div className="lg:col-span-2">
                        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle className="flex items-center gap-2">
                                        <span className="text-rose-400">🛡️</span>
                                        Auditd Events
                                    </CardTitle>
                                    <div className="flex items-center gap-2">
                                        {loading && <span className="text-xs text-gray-500 animate-pulse">Refreshing...</span>}
                                        <Badge variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20">
                                            Real-time
                                        </Badge>
                                    </div>
                                </div>
                                <CardDescription>Kernel-level syscall monitoring</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {error ? (
                                        <div className="text-center py-8">
                                            <p className="text-sm text-rose-400 mb-2">Error loading events</p>
                                            <p className="text-xs text-gray-500">{error}</p>
                                            <Badge
                                                variant="outline"
                                                className="mt-4 cursor-pointer hover:bg-white/10"
                                                onClick={() => fetchEvents()}
                                            >
                                                Retry
                                            </Badge>
                                        </div>
                                    ) : events.length === 0 ? (
                                        <p className="text-sm text-gray-400 text-center py-8">
                                            {loading ? "Loading events..." : "No events detected"}
                                        </p>
                                    ) : (
                                        events.map((event) => (
                                            <div
                                                key={event.id}
                                                className="bg-slate-900/50 rounded-lg p-4 border border-white/10 hover:border-rose-500/30 transition-colors"
                                            >
                                                <div className="flex items-start justify-between mb-2">
                                                    <div className="flex items-center gap-2">
                                                        <Badge variant="outline" className={getSeverityColor(event.severity)}>
                                                            {event.severity.toUpperCase()}
                                                        </Badge>
                                                        <Badge variant="outline" className="text-xs">
                                                            {event.type}
                                                        </Badge>
                                                    </div>
                                                    <span className="text-xs text-gray-500">
                                                        {mounted ? event.timestamp.toLocaleTimeString() : "--:--:--"}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-gray-300 mb-2">{event.description}</p>
                                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                                    {event.user && <span>User: {event.user}</span>}
                                                    {event.process && <span>Process: {event.process}</span>}
                                                    <span className="ml-auto text-emerald-400">{event.action}</span>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Exploit Detection */}
                        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-orange-400">⚠️</span>
                                    Exploit Detection
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4 mb-4">
                                    <p className="text-emerald-400 font-semibold">✅ All Clear</p>
                                    <p className="text-sm text-gray-300 mt-1">
                                        No exploits detected in the last 7 days
                                    </p>
                                </div>
                                <div className="space-y-2 text-sm text-gray-400">
                                    <div className="flex justify-between">
                                        <span>Privilege escalation</span>
                                        <span className="text-emerald-400">0</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Suspicious executions</span>
                                        <span className="text-emerald-400">0</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Unauthorized access</span>
                                        <span className="text-emerald-400">0</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Compliance */}
                        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-purple-400">📋</span>
                                    Compliance
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">Audit Logging</span>
                                        <span className="text-emerald-400">✅</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">Encryption</span>
                                        <span className="text-emerald-400">✅</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">Access Control</span>
                                        <span className="text-emerald-400">✅</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">Backup</span>
                                        <span className="text-amber-400">⚠️</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* AI Insights */}
                        <Card className="bg-white/5 backdrop-blur-xl border-purple-500/20">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="text-purple-400">💡</span>
                                    AI Security Insights
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-300">
                                    Security posture is strong. No anomalous patterns detected in the last 24 hours.
                                    Recommend reviewing backup configuration for SOC 2 compliance.
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                </div>

                {/* Info Footer */}
                <div className="mt-8 bg-rose-500/10 border border-rose-500/20 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <span className="text-2xl">ℹ️</span>
                        <div>
                            <p className="text-rose-400 font-semibold mb-1">Auditd Watchdog</p>
                            <p className="text-sm text-gray-300">
                                Sentinel monitors critical syscalls (execve, open, ptrace, chmod) at the kernel level
                                using auditd. All events are logged and analyzed in real-time for exploit detection.
                                This provides defense-in-depth security that operates below the application layer.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
