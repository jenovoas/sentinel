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
  AnalyticsSample,
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
    hostCpu: [],
    hostMemory: [],
    hostGpu: [],
    hostNetwork: [],
  });
  const [anomalies, setAnomalies] = useState<AnomalyPoint[]>([]);
  const [anomaliesAvailable, setAnomaliesAvailable] = useState(false);
  const [metricsAvailable, setMetricsAvailable] = useState(false);
  const [storage, setStorage] = useState<StorageSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const hydrateHistory = useCallback(async () => {
    const feed = await AnalyticsAPI.getRecentMetricsFeed(200);
    setMetricsAvailable(feed.available);

    const sorted = [...feed.samples].sort(
      (a, b) => new Date(a.sampled_at).getTime() - new Date(b.sampled_at).getTime()
    );

    const toHistory = (selector: (sample: AnalyticsSample) => number | null): MetricHistory =>
      sorted
        .flatMap((sample) => {
          const value = selector(sample);
          const timestamp = new Date(sample.sampled_at).getTime();
          return value !== null && Number.isFinite(value) && Number.isFinite(timestamp)
            ? [{ timestamp, value }]
            : [];
        })
        .slice(-HISTORY_SIZE);

    setHistory({
      cpu: toHistory((sample) => sample.cpu_percent),
      memory: toHistory((sample) => sample.memory_percent),
      gpu: toHistory((sample) => sample.gpu_percent),
      network: [],
      hostCpu: [],
      hostMemory: [],
      hostGpu: [],
      hostNetwork: [],
    });
  }, []);

  const loadAnomalies = useCallback(async () => {
    const feed = await AnalyticsAPI.getAnomalies(200);
    setAnomalies(feed.anomalies);
    setAnomaliesAvailable(feed.available);
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
      { cpu: [], memory: [], gpu: [], network: [], hostCpu: [], hostMemory: [], hostGpu: [], hostNetwork: [] }
    );
  }, [anomalies]);

  return {
    history,
    metricsAvailable,
    anomalies,
    anomaliesAvailable,
    storage,
    loading,
    anomaliesByMetric,
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
