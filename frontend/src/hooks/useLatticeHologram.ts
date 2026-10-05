import { useState, useEffect, useCallback, useRef } from "react";
import { LatticeHologramData } from "../lib/types";

interface UseLatticeHologramOptions {
  pollingIntervalMs?: number;
  autoRefresh?: boolean;
  maxNodes?: number;
}

export function useLatticeHologram({
  pollingIntervalMs = 500,
  autoRefresh = true,
  maxNodes = 64,
}: UseLatticeHologramOptions = {}) {
  const [data, setData] = useState<LatticeHologramData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const isMountedRef = useRef<boolean>(true);

  const fetchHologram = useCallback(async () => {
    try {
      const response = await fetch("/api/v1/lattice/hologram", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const json = (await response.json()) as LatticeHologramData;
      if (!isMountedRef.current) return;

      setData({
        ...json,
        nodes: Array.isArray(json.nodes) ? json.nodes.slice(0, maxNodes) : [],
      });
      setIsConnected(true);
      setError(null);
      setLastUpdated(new Date());
    } catch (err: unknown) {
      if (!isMountedRef.current) return;
      setIsConnected(false);
      setError(err instanceof Error ? err.message : "Error connecting to Lattice Cortex");
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [maxNodes]);

  useEffect(() => {
    isMountedRef.current = true;
    void fetchHologram();

    let intervalId: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      intervalId = setInterval(() => {
        void fetchHologram();
      }, pollingIntervalMs);
    }

    return () => {
      isMountedRef.current = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefresh, pollingIntervalMs, fetchHologram]);

  return {
    data,
    isLoading,
    error,
    isConnected,
    lastUpdated,
    refetch: fetchHologram,
  };
}
