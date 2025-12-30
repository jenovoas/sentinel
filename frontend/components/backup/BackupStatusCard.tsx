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
import Link from "next/link";
import { useBackupStatus } from "@/hooks/useBackupStatus";

export function BackupStatusCard() {
    const { status, config, refresh } = useBackupStatus();
    const [triggeringBackup, setTriggeringBackup] = useState(false);

    const handleTriggerBackup = async () => {
        setTriggeringBackup(true);
        try {
            const res = await fetch('/api/v1/backup/trigger', { method: 'POST' });
            const data = await res.json();

            if (data.status === 'success') {
                alert('✅ Backup completed successfully!');
                refresh(); // Refresh status
            } else {
                alert(`❌ Backup failed: ${data.message}`);
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
            healthy: "Operational",
            warning: "Warning",
            critical: "Critical",
        };

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
                        Backup System
                    </CardTitle>
                    {getHealthBadge()}
                </div>
                <CardDescription>Enterprise backup monitoring</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {/* Last Backup Info */}
                    <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                        <div>
                            <p className="text-sm text-gray-400">Last Backup</p>
                            <p className="text-lg font-semibold text-white">
                                {formatAge(status.lastBackupAge)}
                            </p>
                            {status.lastBackupTime && (
                                <p className="text-xs text-gray-500 mt-1">
                                    {status.lastBackupTime}
                                </p>
                            )}
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-400">Status</p>
                            <p
                                className={`text-lg font-semibold ${status.lastBackupStatus === 'success'
                                        ? 'text-emerald-400'
                                        : 'text-rose-400'
                                    }`}
                            >
                                {status.lastBackupStatus === 'success' ? '✓ Success' : '✗ Failed'}
                            </p>
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-3 gap-3">
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-cyan-400">{status.totalBackups}</p>
                            <p className="text-xs text-gray-400">Total Backups</p>
                        </div>
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-purple-400">
                                {status.totalSizeMB.toFixed(0)}MB
                            </p>
                            <p className="text-xs text-gray-400">Total Size</p>
                        </div>
                        <div className="text-center p-2 rounded bg-slate-800/30">
                            <p className="text-2xl font-bold text-emerald-400">
                                {config?.retentionDays || 7}d
                            </p>
                            <p className="text-xs text-gray-400">Retention</p>
                        </div>
                    </div>

                    {/* Configuration Badges */}
                    {config && (
                        <div className="flex flex-wrap gap-2">
                            {config.s3Enabled && (
                                <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-xs">
                                    S3 Enabled
                                </Badge>
                            )}
                            {config.minioEnabled && (
                                <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/20 text-xs">
                                    MinIO Enabled
                                </Badge>
                            )}
                            {config.encryptionEnabled && (
                                <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs">
                                    Encrypted
                                </Badge>
                            )}
                            {config.webhookEnabled && (
                                <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/20 text-xs">
                                    Notifications
                                </Badge>
                            )}
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
                        <Link href="/admin/backups" className="flex-1">
                            <Button variant="outline" className="w-full">
                                View Details
                            </Button>
                        </Link>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
