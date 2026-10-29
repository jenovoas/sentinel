/**
 * Custom Hook: useBackupStatus
 * 
 * Fetches and manages backup system status with automatic refresh.
 * Provides real-time updates every 30 seconds.
 */

import { useState, useEffect, useCallback } from 'react';

export interface BackupStatus {
    available: boolean;
    health: 'healthy' | 'warning' | 'critical';
    lastBackupAge: number | null;
    lastBackupStatus: string;
    lastBackupTime: string | null;
    totalBackups: number | null;
    totalSizeMB: number | null;
    loading: boolean;
    error: string | null;
}

export interface BackupConfig {
    backupDir: string;
    retentionDays: number | null;
    s3Enabled: boolean | null;
    minioEnabled: boolean | null;
    encryptionEnabled: boolean | null;
    webhookEnabled: boolean | null;
}

export function useBackupStatus(refreshInterval = 30000) {
    const [status, setStatus] = useState<BackupStatus>({
        available: false,
        health: 'warning',
        lastBackupAge: null,
        lastBackupStatus: 'unknown',
        lastBackupTime: null,
        totalBackups: null,
        totalSizeMB: null,
        loading: true,
        error: null,
    });

    const [config, setConfig] = useState<BackupConfig | null>(null);

    const fetchStatus = useCallback(async () => {
        try {
            const res = await fetch('/api/v1/backup/status');

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            }

            const data = await res.json();

            const available = data.available === true;
            const lastBackup = data.last_backup ?? {};
            const metrics = data.metrics ?? {};
            const rawConfig = data.config;

            setStatus({
                available,
                health: data.health,
                lastBackupAge: !available || lastBackup.status === 'not_available'
                    ? null
                    : lastBackup.age_hours ?? null,
                lastBackupStatus: lastBackup.status ?? 'unknown',
                lastBackupTime: lastBackup.time ?? null,
                totalBackups: available ? metrics.total_backups ?? null : null,
                totalSizeMB: available ? metrics.total_size_mb ?? null : null,
                loading: false,
                error: null,
            });

            setConfig(rawConfig ? {
                backupDir: rawConfig.backup_dir,
                retentionDays: rawConfig.retention_days ?? null,
                s3Enabled: rawConfig.s3_enabled ?? null,
                minioEnabled: rawConfig.minio_enabled ?? null,
                encryptionEnabled: rawConfig.encryption_enabled ?? null,
                webhookEnabled: rawConfig.webhook_enabled ?? null,
            } : null);
        } catch (error) {
            console.error('Error fetching backup status:', error);
            setStatus((prev) => ({
                ...prev,
                loading: false,
                error: error instanceof Error ? error.message : 'Failed to load backup status',
            }));
        }
    }, []);

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, refreshInterval);
        return () => clearInterval(interval);
    }, [fetchStatus, refreshInterval]);

    return { status, config, refresh: fetchStatus };
}
