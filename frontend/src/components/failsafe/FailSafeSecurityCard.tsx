/**
 * FailSafeSecurityCard Component
 * 
 * Displays fail-safe security layer status and active playbooks.
 * Shows automated response system that triggers when primary systems fail.
 */

"use client";

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

interface Playbook {
    name: string;
    display_name: string;
    status: 'idle' | 'waiting' | 'triggered' | 'success' | 'failed';
    last_run: string | null;
    last_outcome: string | null;
    execution_count: number;
    success_rate: number;
}

interface FailSafeStatus {
    status: string;
    last_auto_remediation: string;
    active_playbooks: number;
    success_rate_30d: number;
    total_executions: number;
    playbooks: Playbook[];
}

export function FailSafeSecurityCard() {
    const [status, setStatus] = useState<FailSafeStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/v1/failsafe/status');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setStatus(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load');
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (playbookStatus: string) => {
        const colors = {
            idle: "bg-slate-500/10 text-slate-400 border-slate-500/20",
            waiting: "bg-amber-500/10 text-amber-400 border-amber-500/20",
            triggered: "bg-orange-500/10 text-orange-400 border-orange-500/20",
            success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
            failed: "bg-rose-500/10 text-rose-400 border-rose-500/20",
        };

        const labels = {
            idle: "✓ Idle",
            waiting: "⏳ Waiting",
            triggered: "⚡ Triggered",
            success: "✓ Success",
            failed: "✗ Failed",
        };

        return (
            <Badge variant="outline" className={colors[playbookStatus as keyof typeof colors]}>
                {labels[playbookStatus as keyof typeof labels]}
            </Badge>
        );
    };

    if (loading) {
        return (
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                <CardContent className="p-6">
                    <div className="flex items-center justify-center">
                        <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                <CardContent className="p-6">
                    <div className="text-center text-rose-400">
                        <p className="font-semibold mb-2">Failed to load fail-safe status</p>
                        <p className="text-sm text-gray-400">{error}</p>
                        <Button variant="outline" className="mt-4" onClick={fetchStatus}>
                            Retry
                        </Button>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (!status) return null;

    return (
        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                        <span className="text-emerald-400">🛡️</span>
                        Fail-Safe Security
                    </CardTitle>
                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                        {status.status === 'active' ? 'ACTIVE' : 'INACTIVE'}
                    </Badge>
                </div>
                <CardDescription>Automated response when primary systems fail</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {/* Summary Stats */}
                    <div className="grid grid-cols-3 gap-3">
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-emerald-400">{status.active_playbooks}</p>
                            <p className="text-xs text-gray-400">Active Playbooks</p>
                        </div>
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-cyan-400">{status.success_rate_30d}%</p>
                            <p className="text-xs text-gray-400">Success Rate</p>
                        </div>
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-purple-400">{status.total_executions}</p>
                            <p className="text-xs text-gray-400">Total Runs</p>
                        </div>
                    </div>

                    {/* Last Auto-Remediation */}
                    <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                        <div>
                            <p className="text-sm text-gray-400">Last Auto-Remediation</p>
                            <p className="text-lg font-semibold text-white">{status.last_auto_remediation}</p>
                        </div>
                        <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                    </div>

                    {/* Top 3 Playbooks */}
                    <div className="space-y-2">
                        <p className="text-xs text-gray-400 font-semibold uppercase">Recent Playbooks</p>
                        {status.playbooks.slice(0, 3).map((playbook) => (
                            <div
                                key={playbook.name}
                                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 hover:bg-slate-800/50 transition-colors"
                            >
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <p className="text-sm font-medium text-white">{playbook.display_name}</p>
                                        {getStatusBadge(playbook.status)}
                                    </div>
                                    <p className="text-xs text-gray-400">
                                        {playbook.last_run ? `Last run: ${playbook.last_run}` : 'Never executed'}
                                    </p>
                                    {playbook.last_outcome && (
                                        <p className="text-xs text-gray-500 mt-1">{playbook.last_outcome}</p>
                                    )}
                                </div>
                                <div className="text-right ml-4">
                                    <p className="text-sm font-semibold text-cyan-400">{playbook.execution_count}</p>
                                    <p className="text-xs text-gray-500">runs</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                        <Link href="/admin/failsafe" className="flex-1">
                            <Button variant="outline" className="w-full">
                                View All Playbooks
                            </Button>
                        </Link>
                        <Link href="/admin/failsafe/history" className="flex-1">
                            <Button variant="outline" className="w-full">
                                Execution History
                            </Button>
                        </Link>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
