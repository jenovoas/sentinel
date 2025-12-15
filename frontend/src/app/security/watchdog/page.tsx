"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        // TODO: Fetch real auditd events from backend
        // For now, using mock data
        const mockEvents: AuditEvent[] = [
            {
                id: "1",
                timestamp: new Date(Date.now() - 1000 * 60 * 5),
                type: "execve",
                severity: "low",
                description: "Process execution: /usr/bin/python3",
                action: "Logged",
                user: "www-data",
                process: "python3",
            },
            {
                id: "2",
                timestamp: new Date(Date.now() - 1000 * 60 * 15),
                type: "open",
                severity: "low",
                description: "File access: /etc/passwd",
                action: "Logged",
                user: "root",
                process: "systemd",
            },
            {
                id: "3",
                timestamp: new Date(Date.now() - 1000 * 60 * 30),
                type: "chmod",
                severity: "medium",
                description: "Permission change: /tmp/script.sh",
                action: "Logged",
                user: "jnovoas",
                process: "chmod",
            },
        ];

        setEvents(mockEvents);
        setEventsToday(mockEvents.length);
        setThreatsDetected(0);
    }, []);

    const getSeverityColor = (severity: AuditEvent["severity"]) => {
        switch (severity) {
            case "critical":
                return "bg-rose-500/20 text-rose-400 border-rose-500/30";
            case "high":
                return "bg-orange-500/20 text-orange-400 border-orange-500/30";
            case "medium":
                return "bg-amber-500/20 text-amber-400 border-amber-500/30";
            case "low":
                return "bg-slate-500/20 text-slate-400 border-slate-500/30";
        }
    };

    const getStatusColor = (status: typeof securityStatus) => {
        switch (status) {
            case "secure":
                return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
            case "warning":
                return "text-amber-400 bg-amber-500/10 border-amber-500/20";
            case "critical":
                return "text-rose-400 bg-rose-500/10 border-rose-500/20";
        }
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100">
            <div
                className="absolute inset-0 opacity-50 blur-3xl bg-[radial-gradient(circle_at_20%_20%,rgba(239,68,68,0.12),transparent_35%),radial-gradient(circle_at_80%_0%,rgba(249,115,22,0.12),transparent_30%)]"
                aria-hidden
            />

            <div className="relative mx-auto max-w-7xl px-6 py-10">
                {/* Header */}
                <header className="mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm uppercase tracking-[0.25em] text-rose-200/70">Sentinel Security</p>
                            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white">
                                Auditd Watchdog
                            </h1>
                            <p className="text-gray-300 mt-2 max-w-2xl">
                                Real-time kernel-level security monitoring with exploit detection
                            </p>
                        </div>
                        <Link href="/dashboard">
                            <Button variant="outline">← Back to Dashboard</Button>
                        </Link>
                    </div>
                </header>

                {/* Security Status Hero */}
                <div className={`mb-8 rounded-2xl border p-6 ${getStatusColor(securityStatus)}`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <span className="text-4xl">🔒</span>
                                <h2 className="text-2xl font-semibold">
                                    {securityStatus === "secure" && "Security Status: SECURE"}
                                    {securityStatus === "warning" && "Security Warning"}
                                    {securityStatus === "critical" && "Critical Security Alert"}
                                </h2>
                            </div>
                            <p className="text-sm opacity-80">
                                Last scan: {mounted ? new Date().toLocaleTimeString() : "--:--:--"} • All systems monitored
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-3xl font-bold">{threatsDetected}</p>
                            <p className="text-sm opacity-80">Threats Detected (24h)</p>
                        </div>
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid gap-4 md:grid-cols-4 mb-8">
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Events Today</p>
                            <p className="text-3xl font-semibold text-cyan-400">{eventsToday}</p>
                            <p className="text-xs text-gray-500 mt-1">All logged</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Exploits Blocked</p>
                            <p className="text-3xl font-semibold text-emerald-400">0</p>
                            <p className="text-xs text-gray-500 mt-1">Last 7 days</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Syscalls Monitored</p>
                            <p className="text-3xl font-semibold text-purple-400">4</p>
                            <p className="text-xs text-gray-500 mt-1">execve, open, ptrace, chmod</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Compliance</p>
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
                                    <Badge variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20">
                                        Real-time
                                    </Badge>
                                </div>
                                <CardDescription>Kernel-level syscall monitoring</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {events.length === 0 ? (
                                        <p className="text-sm text-gray-400 text-center py-8">No events detected</p>
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
