/**
 * Custom Hook: useBackupStatus
 * 
 * Fetches and manages backup system status with automatic refresh.
 * Provides real-time updates every 30 seconds.
 */

import { useState, useEffect, useCallback } from 'react';

export interface BackupStatus {
    health: 'healthy' | 'warning' | 'critical';
    lastBackupAge: number;
    lastBackupStatus: string;
    lastBackupTime: string | null;
    totalBackups: number;
    totalSizeMB: number;
    loading: boolean;
    error: string | null;
}

export interface BackupConfig {
    backupDir: string;
    retentionDays: number;
    s3Enabled: boolean;
    minioEnabled: boolean;
    encryptionEnabled: boolean;
    webhookEnabled: boolean;
}

export function useBackupStatus(refreshInterval = 30000) {
    const [status, setStatus] = useState<BackupStatus>({
        health: 'healthy',
        lastBackupAge: 0,
        lastBackupStatus: 'unknown',
        lastBackupTime: null,
        totalBackups: 0,
        totalSizeMB: 0,
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

            setStatus({
                health: data.health,
                lastBackupAge: data.last_backup.age_hours || 0,
                lastBackupStatus: data.last_backup.status,
                lastBackupTime: data.last_backup.time,
                totalBackups: data.metrics.total_backups,
                totalSizeMB: data.metrics.total_size_mb,
                loading: false,
                error: null,
            });

            setConfig(data.config);
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
