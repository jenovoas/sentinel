"use client";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

export default function SecurityWatchdogPage() {
    const threatsDetected: number | null = null;
    const eventsToday: number | null = null;

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
                                El feed de auditd y las métricas de exploits no están expuestos por la API actual de Cortex.
                            </p>
                        </div>
                        <Link href="/dashboard">
                            <Button variant="outline">← Back to Dashboard</Button>
                        </Link>
                    </div>
                </header>

                {/* Security Status Hero */}
                <div className="mb-8 rounded-2xl border p-6 text-gray-400 bg-gray-500/10 border-gray-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <span className="text-4xl">🔒</span>
                                <h2 className="text-2xl font-semibold">Estado de seguridad no disponible</h2>
                            </div>
                            <p className="text-sm opacity-80">
                                Último escaneo: N/D • Feed de auditoría no disponible
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-3xl font-bold">{threatsDetected ?? "N/D"}</p>
                            <p className="text-sm opacity-80">Threats Detected (24h)</p>
                        </div>
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid gap-4 md:grid-cols-4 mb-8">
                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Events Today</p>
                            <p className="text-3xl font-semibold text-cyan-400">{eventsToday ?? "N/D"}</p>
                            <p className="text-xs text-gray-500 mt-1">Feed auditd no disponible</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Exploits Blocked</p>
                            <p className="text-3xl font-semibold text-gray-400">N/D</p>
                            <p className="text-xs text-gray-500 mt-1">Feed de exploits no disponible</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Syscalls Monitored</p>
                            <p className="text-3xl font-semibold text-gray-400">N/D</p>
                            <p className="text-xs text-gray-500 mt-1">Inventario no expuesto por Cortex</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                        <CardContent className="p-6">
                            <p className="text-sm text-gray-400 mb-1">Compliance</p>
                            <p className="text-3xl font-semibold text-gray-400">N/D</p>
                            <p className="text-xs text-gray-500 mt-1">Sin evaluación de cumplimiento</p>
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
                                        No disponible
                                    </Badge>
                                </div>
                                <CardDescription>Kernel-level syscall monitoring</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    <p className="text-sm text-gray-400 text-center py-8">
                                        Cortex no expone un feed auditd para esta vista.
                                    </p>
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
                                <div className="bg-gray-500/10 border border-gray-500/20 rounded-lg p-4 mb-4">
                                    <p className="text-gray-300 font-semibold">Estado no disponible</p>
                                    <p className="text-sm text-gray-400 mt-1">
                                        Cortex no expone métricas de detección de exploits.
                                    </p>
                                </div>
                                <div className="space-y-2 text-sm text-gray-400">
                                    <div className="flex justify-between">
                                        <span>Privilege escalation</span>
                                        <span className="text-gray-400">N/D</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Suspicious executions</span>
                                        <span className="text-gray-400">N/D</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Unauthorized access</span>
                                        <span className="text-gray-400">N/D</span>
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
                                        <span className="text-gray-400">N/D</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">Encryption</span>
                                        <span className="text-gray-400">N/D</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">Access Control</span>
                                        <span className="text-gray-400">N/D</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-300">Backup</span>
                                        <span className="text-gray-400">N/D</span>
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
                                    Análisis de seguridad no disponible: Cortex no expone resultados de anomalías ni una evaluación de cumplimiento para esta vista.
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
                                Esta vista no recibe eventos auditd ni resultados de detección desde la API de Cortex.
                                Por ello, el estado de syscalls, exploits, cumplimiento y análisis permanece como no disponible;
                                esta pantalla no confirma ni descarta actividad de seguridad.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
