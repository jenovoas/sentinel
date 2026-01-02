import { useState, useEffect } from 'react';

export interface SentinelStatus {
    system: string;
    cpu: string;
    memory: string;
    uptime: number;
    active_threats: number;
    defense_level: string;
    ai_latency: string;
    auth_personnel: number;
    network_nodes: number;
    db_transactions: number;
    network?: {
        rx_bytes_sec: string;
        tx_bytes_sec: string;
    };
}

export function useSentinelStatus() {
    const [status, setStatus] = useState<SentinelStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch('/api/v1/dashboard/status');
                if (!res.ok) throw new Error('Failed to fetch status');
                const data = await res.json();

                // Unified mapping of backend response to SentinelStatus interface
                const mappedStatus: SentinelStatus = {
                    system: data.db_health?.status === 'healthy' ? 'STABLE' : 'DEGRADED',
                    cpu: data.system?.cpu_percent?.toFixed(1) || "0",
                    memory: data.system?.mem_percent?.toFixed(1) || "0",
                    uptime: 3600, // Fixed placeholder for now or add to backend
                    active_threats: data.db_stats?.locks || 0,
                    defense_level: "LEVEL 6",
                    ai_latency: "12ms",
                    auth_personnel: 1,
                    network_nodes: 128,
                    db_transactions: data.db_stats?.connections_total || 0,
                    network: {
                        rx_bytes_sec: data.network?.net_bytes_recv?.toString() || "0",
                        tx_bytes_sec: data.network?.net_bytes_sent?.toString() || "0"
                    }
                };

                setStatus(mappedStatus);
                setError(null);
            } catch (err) {
                console.error("Sentinel Status Error:", err);
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                setLoading(false);
            }
        };

        // Initial fetch
        fetchStatus();

        // Poll every 5 seconds
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    return { status, loading, error };
}
