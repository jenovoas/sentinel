import { useState, useEffect, useCallback } from "react";

export interface IncidentStats {
    total_incidents: number;
    open_incidents: number;
    critical_incidents: number;
    p1_count: number;
    p2_count: number;
    p3_count: number;
    p4_count: number;
}

export interface Incident {
    id: number;
    incident_id: string;
    title: string;
    category: string;
    priority: string;
    status: string;
    assigned_team: string | null;
    detection_time: string;
}

import { usePageVisibility } from "./usePageVisibility";

export function useIncidents(pollInterval = 30000) {
    const [stats, setStats] = useState<IncidentStats | null>(null);
    const [recentIncidents, setRecentIncidents] = useState<Incident[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const isVisible = usePageVisibility();

    const fetchData = useCallback(async () => {
        if (!isVisible) return; // Don't fetch if tab is hidden

        try {
            setError(null);
            // ... (rest of fetchData logic remains same, just preventing execution)

            // Parallel fetch for potential performance boost
            const [statsRes, incidentsRes] = await Promise.all([
                fetch("/api/v1/incidents/stats"),
                fetch("/api/v1/incidents?page=1&page_size=5&sort_by=created_at&sort_order=desc")
            ]);

            if (statsRes.ok) {
                const statsData = await statsRes.json();
                setStats(statsData);
            }

            if (incidentsRes.ok) {
                const incidentsData = await incidentsRes.json();
                setRecentIncidents(incidentsData.incidents || []);
            }
        } catch (err: any) {
            console.error("Error fetching incident data:", err);
            setError(err.message || "Failed to fetch incidents");
        } finally {
            setLoading(false);
        }
    }, [isVisible]);

    useEffect(() => {
        fetchData();
        // Only set interval if page is visible
        if (!isVisible) return;

        const interval = setInterval(fetchData, pollInterval);
        return () => clearInterval(interval);
    }, [fetchData, pollInterval, isVisible]);

    return { stats, recentIncidents, loading, error, refresh: fetchData };
}
