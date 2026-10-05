/**
 * Analytics API Service
 * Centralized data fetching logic following Single Responsibility Principle
 */

import { 
  AnalyticsSample, 
  AnomalyPoint, 
  StorageSummary,
  HistoryState,
  AnalyticsAnomalyFeed,
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
   * Fetches the current CPU and memory pressure snapshot.
   */
  async getAnomalies(limit = 200): Promise<AnalyticsAnomalyFeed> {
    try {
      const res = await fetch(
        `${API_BASE}/api/v1/analytics/anomalies?limit=${limit}`,
        { cache: "no-store" }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as {
        available: boolean;
        scope: "current_snapshot";
        anomalies: Array<{
          id: string;
          detected_at: string;
          severity: AnomalyPoint["severity"];
          title: string;
          type: AnomalyPoint["type"];
          metric_value?: number;
        }>;
      };

      const metricForType: Partial<Record<AnomalyPoint["type"], keyof HistoryState>> = {
        cpu_spike: "cpu",
        memory_spike: "memory",
      };
      const anomalies = (json.anomalies ?? []).flatMap((anomaly) => {
        const timestamp = new Date(anomaly.detected_at).getTime();
        const metric = metricForType[anomaly.type];
        if (!metric || !Number.isFinite(timestamp)) return [];
        return [{
          id: anomaly.id,
          timestamp,
          severity: anomaly.severity,
          title: anomaly.title,
          type: anomaly.type,
          metric,
          metricValue: anomaly.metric_value,
        }];
      });

      return {
        available: json.available === true,
        scope: "current_snapshot",
        anomalies,
      };
    } catch (err) {
      console.error("[AnalyticsAPI] getAnomalies error:", err);
      return { available: false, scope: "current_snapshot", anomalies: [] };
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
