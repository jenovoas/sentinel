import { useState, useEffect, useCallback, useRef } from "react";
import { LatticeHologramData, HologramNode } from "../lib/types";

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
  const [activeCyclePhase, setActiveCyclePhase] = useState<number>(0);

  const isMountedRef = useRef<boolean>(true);

  const generateSyntheticNodes = useCallback((count: number): HologramNode[] => {
    const time = Date.now() / 1000;
    const pulse17 = Math.sin((time * 2 * Math.PI) / 17);
    const nodes: HologramNode[] = [];
    const SCALE_0 = 12960000;

    for (let i = 0; i < count; i++) {
      const spatialPhase = (i * 17 * 2 * Math.PI) / count;
      const wave = Math.sin(time * 1.5 + spatialPhase) * 0.5 + 0.5;
      const ampRaw = Math.floor((wave * 0.8 + pulse17 * 0.2) * SCALE_0);
      const phaseRaw = Math.floor((time * 1000 + i * 200) % SCALE_0);

      nodes.push({
        index: i,
        amplitude_raw: Math.max(0, ampRaw),
        phase_raw: phaseRaw,
        amplitude_u16: Math.floor(Math.min(65535, (Math.abs(ampRaw) * 65535) / SCALE_0)),
        phase_u16: Math.floor(((phaseRaw % SCALE_0) * 65535) / SCALE_0),
      });
    }
    return nodes;
  }, []);

  const fetchHologram = useCallback(async () => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const endpoints = [`/api/v1/lattice/hologram`, `${baseUrl}/api/v1/lattice/hologram`];

      let response: Response | null = null;
      for (const endpoint of endpoints) {
        try {
          const res = await fetch(endpoint, { cache: "no-store" });
          if (res.ok) {
            response = res;
            break;
          }
        } catch {
          // Try next endpoint
        }
      }

      if (!response || !response.ok) {
        throw new Error("Cortex backend unreachable");
      }

      const json = (await response.json()) as LatticeHologramData;
      if (!isMountedRef.current) return;

      const trimmedNodes = json.nodes && json.nodes.length > maxNodes 
        ? json.nodes.slice(0, maxNodes) 
        : json.nodes || [];

      setData({
        ...json,
        nodes: trimmedNodes,
      });
      setIsConnected(true);
      setError(null);
      setLastUpdated(new Date());
    } catch (err: unknown) {
      if (!isMountedRef.current) return;
      setIsConnected(false);
      const fallbackNodes = generateSyntheticNodes(maxNodes);
      setData({
        total_energy: 426291938943,
        node_count: maxNodes,
        coherence_raw: 9500000,
        nodes: fallbackNodes,
      });
      setError(err instanceof Error ? err.message : "Error connecting to Lattice Cortex");
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [maxNodes, generateSyntheticNodes]);

  useEffect(() => {
    isMountedRef.current = true;
    void fetchHologram();

    let intervalId: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      intervalId = setInterval(() => {
        void fetchHologram();
      }, pollingIntervalMs);
    }

    const phaseInterval = setInterval(() => {
      const sec = (Date.now() / 1000) % 17;
      setActiveCyclePhase(Number((sec / 17).toFixed(3)));
    }, 100);

    return () => {
      isMountedRef.current = false;
      if (intervalId) clearInterval(intervalId);
      clearInterval(phaseInterval);
    };
  }, [autoRefresh, pollingIntervalMs, fetchHologram]);

  return {
    data,
    isLoading,
    error,
    isConnected,
    lastUpdated,
    activeCyclePhase,
    refetch: fetchHologram,
  };
}
