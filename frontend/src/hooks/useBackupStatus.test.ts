import { renderHook, act, waitFor } from '@testing-library/react';
import { useBackupStatus } from './useBackupStatus';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('useBackupStatus', () => {
    const mockBackupData = {
        health: 'healthy',
        last_backup: {
            age_hours: 2,
            status: 'success',
            time: '2026-03-24T07:41:15Z'
        },
        metrics: {
            total_backups: 42,
            total_size_mb: 1024
        },
        config: {
            backupDir: '/backups',
            retentionDays: 7,
            s3Enabled: true,
            minioEnabled: false,
            encryptionEnabled: true,
            webhookEnabled: false
        }
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should initialize with loading state', async () => {
        // Mock fetch to delay resolution
        (global.fetch as any).mockImplementation(() => new Promise(() => {}));

        const { result } = renderHook(() => useBackupStatus());

        expect(result.current.status.loading).toBe(true);
        expect(result.current.status.health).toBe('healthy');
        expect(result.current.config).toBeNull();
    });

    it('should fetch and map status data correctly', async () => {
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => mockBackupData,
        });

        const { result } = renderHook(() => useBackupStatus());

        await waitFor(() => expect(result.current.status.loading).toBe(false));

        expect(result.current.status).toEqual({
            health: 'healthy',
            lastBackupAge: 2,
            lastBackupStatus: 'success',
            lastBackupTime: '2026-03-24T07:41:15Z',
            totalBackups: 42,
            totalSizeMB: 1024,
            loading: false,
            error: null,
        });
        expect(result.current.config).toEqual(mockBackupData.config);
    });

    it('should handle HTTP errors', async () => {
        (global.fetch as any).mockResolvedValue({
            ok: false,
            status: 500,
            statusText: 'Internal Server Error',
        });

        const { result } = renderHook(() => useBackupStatus());

        await waitFor(() => expect(result.current.status.loading).toBe(false));

        expect(result.current.status.error).toBe('HTTP 500: Internal Server Error');
        expect(result.current.status.loading).toBe(false);
    });

    it('should handle network errors', async () => {
        (global.fetch as any).mockRejectedValue(new Error('Network failure'));

        const { result } = renderHook(() => useBackupStatus());

        await waitFor(() => expect(result.current.status.loading).toBe(false));

        expect(result.current.status.error).toBe('Network failure');
    });

    it('should manual refresh trigger a new fetch', async () => {
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => mockBackupData,
        });

        const { result } = renderHook(() => useBackupStatus());

        await waitFor(() => expect(result.current.status.loading).toBe(false));

        (global.fetch as any).mockClear();
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => ({ ...mockBackupData, health: 'warning' }),
        });

        await act(async () => {
            await result.current.refresh();
        });

        expect(global.fetch).toHaveBeenCalledTimes(1);
        expect(result.current.status.health).toBe('warning');
    });

    it('should refresh automatically on interval', async () => {
        vi.useFakeTimers();
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => mockBackupData,
        });

        renderHook(() => useBackupStatus(10000));

        expect(global.fetch).toHaveBeenCalledTimes(1);

        await act(async () => {
            vi.advanceTimersByTime(10000);
        });

        expect(global.fetch).toHaveBeenCalledTimes(2);
    });
});
