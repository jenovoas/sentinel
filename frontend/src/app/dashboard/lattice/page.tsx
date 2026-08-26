"use client";

import { useState } from "react";
import { useLatticeHologram } from "../../../hooks/useLatticeHologram";
import { HexagonalLatticeViewer } from "../../../components/lattice/HexagonalLatticeViewer";
import { HologramNode } from "../../../lib/types";
import { 
  Activity, 
  Flame, 
  RefreshCw, 
  Zap, 
  ShieldCheck, 
  Cpu, 
  Layers,
  Sparkles
} from "lucide-react";

export default function LatticeDashboardPage() {
  const [pollingRate, setPollingRate] = useState<number>(500);
  const [isAutoRefresh, setIsAutoRefresh] = useState<boolean>(true);
  const [selectedNode, setSelectedNode] = useState<HologramNode | null>(null);

  const {
    data,
    isLoading,
    isConnected,
    lastUpdated,
    activeCyclePhase,
    refetch,
  } = useLatticeHologram({
    pollingIntervalMs: pollingRate,
    autoRefresh: isAutoRefresh,
    maxNodes: 91,
  });

  const nodes = data?.nodes || [];
  const totalEnergy = data?.total_energy || 0;
  const coherenceRaw = data?.coherence_raw || 0;
  const coherenceNorm = (coherenceRaw / 12960000).toFixed(4);

  return (
    <div className="min-h-screen bg-[#06090e] text-white p-6 md:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Flame className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-black uppercase tracking-tight italic">
              Retículo <span className="text-cyan-400">Resonante S60</span>
            </h1>
          </div>
          <p className="text-gray-400 text-sm mt-1">
            Visualizador de Fase y Amplitud de Cristales de Tiempo · Shm Zero-Copy · Plimpton 322
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-black/40 border border-white/10 rounded-2xl p-1">
            {[250, 500, 1000].map((rate) => (
              <button
                key={rate}
                onClick={() => setPollingRate(rate)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                  pollingRate === rate
                    ? "bg-cyan-500 text-black shadow-lg shadow-cyan-500/20"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {rate}ms
              </button>
            ))}
          </div>

          <button
            onClick={() => setIsAutoRefresh(!isAutoRefresh)}
            className={`px-4 py-2 rounded-2xl text-xs font-mono font-bold border transition-all ${
              isAutoRefresh
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                : "bg-white/5 border-white/10 text-gray-400"
            }`}
          >
            {isAutoRefresh ? "Live Sync ON" : "Pausado"}
          </button>

          <button
            onClick={() => refetch()}
            className="p-2.5 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 text-gray-300 hover:text-white transition-all"
            title="Refrescar manual"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0b1017]/80 border border-white/10 rounded-3xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono">
            <span>COHERENCIA S60</span>
            <Sparkles className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-mono font-black text-cyan-300 mt-2">
            {coherenceNorm}
          </div>
          <p className="text-[11px] text-gray-500 mt-1">Raw: {coherenceRaw.toLocaleString()} u</p>
        </div>

        <div className="bg-[#0b1017]/80 border border-white/10 rounded-3xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono">
            <span>ENERGÍA RETÍCULO</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-mono font-black text-amber-300 mt-2">
            {(totalEnergy / 1000000).toFixed(2)}M
          </div>
          <p className="text-[11px] text-gray-500 mt-1">Total SPA: {totalEnergy.toLocaleString()}</p>
        </div>

        <div className="bg-[#0b1017]/80 border border-white/10 rounded-3xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono">
            <span>NODOS ACTIVOS</span>
            <Layers className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-mono font-black text-emerald-300 mt-2">
            {nodes.length} Nodos
          </div>
          <p className="text-[11px] text-gray-500 mt-1">Hex Ring Topología 60⁴</p>
        </div>

        <div className="bg-[#0b1017]/80 border border-white/10 rounded-3xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono">
            <span>VENTANA DE FASE 17s</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-mono font-black text-purple-300 mt-2">
            {(activeCyclePhase * 17).toFixed(1)}s / 17s
          </div>
          <p className="text-[11px] text-gray-500 mt-1">Ciclo armónico maestro</p>
        </div>
      </div>

      {/* Main Visualizer Area + Inspector Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 h-[620px]">
          <HexagonalLatticeViewer
            nodes={nodes}
            totalEnergy={totalEnergy}
            coherenceRaw={coherenceRaw}
            activeCyclePhase={activeCyclePhase}
            isConnected={isConnected}
            onSelectNode={setSelectedNode}
            selectedNodeIndex={selectedNode?.index}
          />
        </div>

        {/* Right Inspector Sidebar */}
        <div className="lg:col-span-1 bg-[#0b1017]/80 border border-white/10 rounded-3xl p-6 flex flex-col justify-between backdrop-blur-md space-y-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-cyan-400 border-b border-white/10 pb-3">
              <Cpu className="w-4 h-4" />
              <span>Inspector de Cristal</span>
            </div>

            {selectedNode ? (
              <div className="space-y-4 font-mono text-xs">
                <div className="p-3 bg-cyan-950/30 border border-cyan-500/20 rounded-2xl">
                  <div className="text-gray-400 text-[10px] uppercase">Identificador</div>
                  <div className="text-lg font-bold text-white mt-1">Cristal #{selectedNode.index}</div>
                  <div className="text-[11px] text-cyan-400">Posición Hexagonal Anular</div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between p-2 rounded-xl bg-white/5">
                    <span className="text-gray-400">Amplitud Raw:</span>
                    <span className="text-amber-300 font-bold">{selectedNode.amplitude_raw.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded-xl bg-white/5">
                    <span className="text-gray-400">Nivel u16 (0-65k):</span>
                    <span className="text-amber-400 font-bold">{selectedNode.amplitude_u16}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded-xl bg-white/5">
                    <span className="text-gray-400">Fase Raw:</span>
                    <span className="text-cyan-300 font-bold">{selectedNode.phase_raw.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded-xl bg-white/5">
                    <span className="text-gray-400">Fase u16:</span>
                    <span className="text-cyan-400 font-bold">{selectedNode.phase_u16}</span>
                  </div>
                </div>

                <div className="p-3 bg-black/40 rounded-2xl border border-white/5 space-y-1">
                  <div className="text-[10px] text-gray-500 uppercase">Frecuencia Base</div>
                  <div className="text-gray-300">1;32,2,24 (Plimpton Fila 12)</div>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center space-y-2 text-gray-500 text-xs">
                <Sparkles className="w-8 h-8 mx-auto text-gray-600 opacity-60" />
                <p>Haz clic en cualquier nodo del retículo para inspeccionar su telemetría cuántica en tiempo real.</p>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-white/10 text-[11px] font-mono text-gray-500 space-y-1">
            <div className="flex items-center justify-between">
              <span>Última sincronía:</span>
              <span className="text-gray-400">{lastUpdated ? lastUpdated.toLocaleTimeString() : "--:--:--"}</span>
            </div>
            <div className="flex items-center gap-1.5 text-emerald-400/80">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Candado YATRA Activo</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
