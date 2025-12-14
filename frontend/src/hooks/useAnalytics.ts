/**
 * Custom hooks for Dashboard
 * Encapsulates state management and side effects
 */

import { useEffect, useState, useCallback, useMemo } from "react";
import { 
  AnomalyPoint, 
  HistoryState, 
  StorageSummary,
  MetricHistory,
} from "@/lib/types";
import { AnalyticsAPI } from "@/lib/api";

const HISTORY_SIZE = 60;
const API_REFRESH_MS = 15000;

export const useAnalytics = () => {
  const [history, setHistory] = useState<HistoryState>({
    cpu: [],
    memory: [],
    gpu: [],
    network: [],
  });
  const [anomalies, setAnomalies] = useState<AnomalyPoint[]>([]);
  const [storage, setStorage] = useState<StorageSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const normalizeNetworkPercent = useCallback((bytesSent: number, bytesRecv: number) => {
    const total = bytesSent + bytesRecv;
    const gb = total / (1024 * 1024 * 1024);
    return Math.min(gb * 10, 100);
  }, []);

  const hydrateHistory = useCallback(async () => {
    const samples = await AnalyticsAPI.getRecentMetrics(200);
    if (samples.length === 0) return;

    const sorted = [...samples].sort(
      (a, b) => new Date(a.sampled_at).getTime() - new Date(b.sampled_at).getTime()
    );

    const toHistory = (selector: (s: typeof samples[0]) => number): MetricHistory =>
      sorted
        .map((s) => ({
          timestamp: new Date(s.sampled_at).getTime(),
          value: selector(s),
        }))
        .slice(-HISTORY_SIZE);

    setHistory({
      cpu: toHistory((s) => s.cpu_percent),
      memory: toHistory((s) => s.memory_percent),
      gpu: toHistory((s) => s.gpu_percent ?? 0),
      network: toHistory((s) => normalizeNetworkPercent(s.network_bytes_sent, s.network_bytes_recv)),
    });
  }, [normalizeNetworkPercent]);

  const loadAnomalies = useCallback(async () => {
    const data = await AnalyticsAPI.getAnomalies(24, 200);
    setAnomalies(data);
  }, []);

  const loadStorage = useCallback(async () => {
    const data = await AnalyticsAPI.getStorageSummary();
    if (data) setStorage(data);
  }, []);

  const refresh = useCallback(async () => {
    await Promise.all([hydrateHistory(), loadAnomalies(), loadStorage()]);
    setLoading(false);
  }, [hydrateHistory, loadAnomalies, loadStorage]);

  // Initial load and intervals
  useEffect(() => {
    refresh();
    const historyInterval = setInterval(hydrateHistory, API_REFRESH_MS);
    const anomaliesInterval = setInterval(loadAnomalies, 60000);
    const storageInterval = setInterval(loadStorage, 30000);

    return () => {
      clearInterval(historyInterval);
      clearInterval(anomaliesInterval);
      clearInterval(storageInterval);
    };
  }, [hydrateHistory, loadAnomalies, loadStorage, refresh]);

  // Group anomalies by metric
  const anomaliesByMetric = useMemo(() => {
    return anomalies.reduce<Record<keyof HistoryState, AnomalyPoint[]>>(
      (acc, a) => {
        acc[a.metric] = [...(acc[a.metric] ?? []), a];
        return acc;
      },
      { cpu: [], memory: [], gpu: [], network: [] }
    );
  }, [anomalies]);

  return {
    history,
    anomalies,
    storage,
    loading,
    anomaliesByMetric,
    normalizeNetworkPercent,
  };
};

export const useDetailModal = () => {
  const [modal, setModal] = useState<{
    type: "metrics" | "anomalies" | "database" | null;
    isOpen: boolean;
  }>({ type: null, isOpen: false });

  const open = useCallback((type: "metrics" | "anomalies" | "database") => {
    setModal({ type, isOpen: true });
  }, []);

  const close = useCallback(() => {
    setModal({ type: null, isOpen: false });
  }, []);

  return { modal, open, close };
};
