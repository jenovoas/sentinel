/**
 * Analytics API Service
 * Centralized data fetching logic following Single Responsibility Principle
 */

import { 
  AnalyticsSample, 
  AnomalyPoint, 
  StorageSummary,
  HistoryState,
} from "./types";

const API_BASE = "";

export const AnalyticsAPI = {
  /**
   * Fetch recent metric samples from the analytics endpoint
   */
  async getRecentMetrics(limit = 200): Promise<AnalyticsSample[]> {
    try {
      const res = await fetch(`${API_BASE}/api/v1/analytics/metrics/recent?limit=${limit}`, {
        cache: "no-store",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as { samples: AnalyticsSample[] };
      return json.samples ?? [];
    } catch (err) {
      console.error("[AnalyticsAPI] getRecentMetrics error:", err);
      return [];
    }
  },

  /**
   * Fetch detected anomalies for the last N hours
   */
  async getAnomalies(hours = 24, limit = 200): Promise<AnomalyPoint[]> {
    try {
      const res = await fetch(
        `${API_BASE}/api/v1/analytics/anomalies?hours=${hours}&limit=${limit}`,
        { cache: "no-store" }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as {
        anomalies: Array<{
          id: string;
          detected_at: string;
          severity: AnomalyPoint["severity"];
          title: string;
          type: string;
          metric_value?: number;
        }>;
      };

      const mapMetric = (type: string): keyof HistoryState => {
        switch (type) {
          case "cpu_spike":
            return "cpu";
          case "memory_spike":
            return "memory";
          case "gpu_overheat":
            return "gpu";
          case "network_spike":
          case "conn_surge":
          case "lock_detected":
          case "query_slow":
            return "network";
          default:
            return "cpu";
        }
      };

      return (json.anomalies ?? []).map((a) => ({
        id: a.id,
        timestamp: new Date(a.detected_at).getTime(),
        severity: a.severity,
        title: a.title,
        type: a.type as AnomalyPoint["type"],
        metric: mapMetric(a.type),
        metricValue: a.metric_value,
      }));
    } catch (err) {
      console.error("[AnalyticsAPI] getAnomalies error:", err);
      return [];
    }
  },

  /**
   * Fetch storage summary (metrics count, anomalies count, DB size)
   */
  async getStorageSummary(): Promise<StorageSummary | null> {
    try {
      const res = await fetch(`${API_BASE}/api/v1/analytics/storage/summary`, {
        cache: "no-store",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return (await res.json()) as StorageSummary;
    } catch (err) {
      console.error("[AnalyticsAPI] getStorageSummary error:", err);
      return null;
    }
  },
};
