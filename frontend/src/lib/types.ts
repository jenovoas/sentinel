/**
 * Shared types for Sentinel Dashboard
 */

export type AnomalyType = 
  | "cpu_spike"
  | "memory_spike"
  | "network_spike"
  | "port_open"
  | "connection_surge"
  | "lock_detected"
  | "query_slow"
  | "gpu_overheat"
  | "unauthorized_access";

export type SeverityLevel = "info" | "warning" | "critical";

export type MetricValue = {
  timestamp: number;
  value: number;
};

export type MetricHistory = MetricValue[];

export type HistoryState = {
  cpu: MetricHistory;
  memory: MetricHistory;
  gpu: MetricHistory;
  network: MetricHistory;
};

export type AnomalyPoint = {
  id: string;
  timestamp: number;
  severity: SeverityLevel;
  title: string;
  type: AnomalyType;
  metric: keyof HistoryState;
  metricValue?: number;
};

export type StorageSummary = {
  metrics_count: number;
  anomalies_count: number;
  latest_metric_at: string | null;
  latest_anomaly_at: string | null;
  db_size_bytes: number;
  status: "healthy" | "no_data";
};

export type AnalyticsSample = {
  sampled_at: string;
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  gpu_percent: number | null;
  network_bytes_sent: number;
  network_bytes_recv: number;
  db_connections_active: number;
  db_locks: number;
};

export type DetailModalType = "metrics" | "anomalies" | "database" | null;
