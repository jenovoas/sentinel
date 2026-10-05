/**
 * BackupStatusCard Component
 * 
 * Displays backup system status, metrics, and quick actions.
 * Shows health indicator, last backup info, and key metrics.
 */

"use client";

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useBackupStatus } from "@/hooks/useBackupStatus";

export function BackupStatusCard() {
    const { status, config, refresh } = useBackupStatus();
    const [triggeringBackup, setTriggeringBackup] = useState(false);
    const backupStatusDisplay: Record<string, { label: string; className: string }> = {
        success: { label: 'Success', className: 'text-emerald-400' },
        failed: { label: 'Failed', className: 'text-rose-400' },
        completed: { label: 'Recent file detected', className: 'text-amber-400' },
        stale: { label: 'Stale file detected', className: 'text-rose-400' },
        recent_file_detected: { label: 'Recent file detected', className: 'text-amber-400' },
        stale_file_detected: { label: 'Stale file detected', className: 'text-rose-400' },
        not_available: { label: 'No file detected', className: 'text-amber-400' },
        unknown: { label: 'Not verified', className: 'text-gray-400' },
    };
    const lastBackupStatus = backupStatusDisplay[status.lastBackupStatus] ?? {
        label: 'Unknown',
        className: 'text-gray-400',
    };

    const handleTriggerBackup = async () => {
        setTriggeringBackup(true);
        try {
            const res = await fetch('/api/v1/backup/trigger', { method: 'POST' });
            const data = await res.json();

            if (res.ok && data.status === 'started') {
                alert(data.message || 'El proceso de respaldo se inició; el resultado aún no está confirmado.');
                refresh();
            } else {
                alert(data.message || `No se pudo iniciar el respaldo (HTTP ${res.status}).`);
            }
        } catch (error) {
            alert('❌ Error triggering backup');
            console.error(error);
        } finally {
            setTriggeringBackup(false);
        }
    };

    const getHealthBadge = () => {
        const colors = {
            healthy: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
            warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
            critical: "bg-rose-500/10 text-rose-400 border-rose-500/20",
        };

        const labels = {
            healthy: "Recent backup file",
            warning: "Backup status warning",
            critical: "Critical",
        };

        if (!status.available) {
            return <Badge variant="outline" className="bg-gray-500/10 text-gray-400 border-gray-500/20">Not available</Badge>;
        }

        return (
            <Badge variant="outline" className={colors[status.health]}>
                {labels[status.health]}
            </Badge>
        );
    };

    const formatAge = (hours: number) => {
        if (hours < 1) return "< 1 hour ago";
        if (hours < 24) return `${Math.round(hours)} hours ago`;
        const days = Math.floor(hours / 24);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    };

    if (status.loading) {
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

    if (status.error) {
        return (
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                <CardContent className="p-6">
                    <div className="text-center text-rose-400">
                        <p className="font-semibold mb-2">Failed to load backup status</p>
                        <p className="text-sm text-gray-400">{status.error}</p>
                        <Button
                            variant="outline"
                            className="mt-4"
                            onClick={refresh}
                        >
                            Retry
                        </Button>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                        <span className="text-blue-400">💾</span>
                        Backup status
                    </CardTitle>
                    {getHealthBadge()}
                </div>
                <CardDescription>Estado calculado a partir de archivos detectados en el directorio configurado.</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {/* Last Backup Info */}
                    <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                        <div>
                            <p className="text-sm text-gray-400">Last Backup</p>
                            <p className="text-lg font-semibold text-white">
                                {!status.available
                                    ? 'Directorio de respaldos no disponible'
                                    : status.lastBackupAge === null
                                        ? 'No se detectaron archivos de respaldo'
                                        : formatAge(status.lastBackupAge)}
                            </p>
                            {status.lastBackupTime && (
                                <p className="text-xs text-gray-500 mt-1">
                                    {status.lastBackupTime}
                                </p>
                            )}
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-400">Status</p>
                            <p className={`text-lg font-semibold ${lastBackupStatus.className}`}>
                                {status.available ? lastBackupStatus.label : 'Not available'}
                            </p>
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-3 gap-3">
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-cyan-400">{status.totalBackups ?? 'N/D'}</p>
                            <p className="text-xs text-gray-400">Total Backups</p>
                        </div>
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-purple-400">
                                {status.totalSizeMB === null ? 'N/D' : `${status.totalSizeMB}MB`}
                            </p>
                            <p className="text-xs text-gray-400">Total Size</p>
                        </div>
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-emerald-400">
                                {config?.retentionDays == null ? 'N/D' : `${config.retentionDays}d`}
                            </p>
                            <p className="text-xs text-gray-400">Retention</p>
                        </div>
                    </div>

                    {/* Configuration Badges */}
                    {config && (
                        <div className="flex flex-wrap gap-2">
                            {([
                                ["S3", config.s3Enabled],
                                ["MinIO", config.minioEnabled],
                                ["Cifrado", config.encryptionEnabled],
                                ["Notificaciones", config.webhookEnabled],
                            ] as const).map(([label, enabled]) => (
                                <Badge key={label} variant="outline" className="bg-slate-500/10 text-gray-300 border-white/10 text-xs">
                                    {label}: {enabled === null ? "N/D" : enabled ? "Activo" : "Inactivo"}
                                </Badge>
                            ))}
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            className="flex-1"
                            onClick={handleTriggerBackup}
                            disabled={triggeringBackup}
                        >
                            {triggeringBackup ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                                    Running...
                                </>
                            ) : (
                                'Trigger Backup'
                            )}
                        </Button>
                        <Button variant="outline" className="flex-1" disabled>
                            Detalles no disponibles
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
