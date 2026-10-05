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

interface FailSafeStatus {
    available: boolean;
    status: string;
    qhc_sync: {
        connected: boolean;
        stale: boolean;
        tick: number | null;
    };
    playbook_metrics_available: boolean;
    execution_history_available: boolean;
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
                        {status.available ? 'RUNTIME DISPONIBLE' : 'NO DISPONIBLE'}
                    </Badge>
                </div>
                <CardDescription>Estado de sincronización QHC expuesto por Cortex; no hay historial de playbooks.</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                        <div className="text-center p-3 rounded bg-slate-800/30">
                            <p className="text-lg font-bold text-cyan-400">
                                {status.qhc_sync.connected && !status.qhc_sync.stale ? "Sincronizado" : "Sin sincronizar"}
                            </p>
                            <p className="text-xs text-gray-400">Estado QHC</p>
                        </div>
                        <div className="text-center p-3 rounded bg-slate-800/30">
                            <p className="text-lg font-bold text-gray-300">
                                {status.qhc_sync.tick == null ? "No disponible" : status.qhc_sync.tick}
                            </p>
                            <p className="text-xs text-gray-400">Último tick QHC</p>
                        </div>
                    </div>

                    <div className="rounded-lg bg-slate-800/50 p-3 text-sm text-gray-300">
                        <p>Conteos de ejecuciones, tasas de éxito e historial de playbooks no están expuestos por el runtime.</p>
                    </div>

                    <div className="flex gap-2">
                        <Link href="/security/watchdog" className="flex-1">
                            <Button variant="outline" className="w-full">
                                Ver watchdog
                            </Button>
                        </Link>
                        <Link href="/analytics" className="flex-1">
                            <Button variant="outline" className="w-full">
                                Ver métricas
                            </Button>
                        </Link>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
