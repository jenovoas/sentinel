/**
 * Trinity Resonance Architecture - Immersive 3D Experience
 * Live monitoring with Three.js visualization
 */

'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import TrinityScene3D to avoid SSR issues
const TrinityScene3D = dynamic(() => import('./components/TrinityScene3D'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-black">
      <div className="text-white text-xl">Loading Trinity Experience...</div>
    </div>
  ),
});

interface CoherenceData {
  micro: number;
  macro: number;
  coherence: number;
  state: 'THERMAL' | 'SYNCING' | 'RESONANT' | 'MERKABAH';
}

interface HierarchyLevel {
  name: string;
  alpha: number;
  beta: number;
  status: 'OK' | 'WARN' | 'ERROR';
}

interface Component {
  name: string;
  utilization: number;
  status: 'OK' | 'WARN' | 'ERROR';
}

export default function TrinityDashboard() {
  const [coherence, setCoherence] = useState<CoherenceData>({
    micro: 0.062,
    macro: 0.45,
    coherence: 0.0,
    state: 'THERMAL'
  });

  const [audioEnabled, setAudioEnabled] = useState(false);
  const [view3D, setView3D] = useState(true);

  const [hierarchy] = useState<HierarchyLevel[]>([
    { name: 'Systems', alpha: 0.95, beta: 0.92, status: 'OK' },
    { name: 'Areas', alpha: 0.88, beta: 0.91, status: 'OK' },
    { name: 'Columns', alpha: 0.72, beta: 0.85, status: 'WARN' },
    { name: 'Circuits', alpha: 0.94, beta: 0.89, status: 'OK' },
    { name: 'Neurons', alpha: 0.91, beta: 0.93, status: 'OK' },
    { name: 'Synapses', alpha: 0.87, beta: 0.88, status: 'OK' },
    { name: 'Molecules', alpha: 0.96, beta: 0.94, status: 'OK' }
  ]);

  const [components] = useState<Component[]>([
    { name: 'Buffer', utilization: 0.67, status: 'OK' },
    { name: 'Thread', utilization: 0.45, status: 'OK' },
    { name: 'Memory', utilization: 0.82, status: 'WARN' },
    { name: 'Network', utilization: 0.34, status: 'OK' },
    { name: 'CPU', utilization: 0.91, status: 'WARN' },
    { name: 'Disk', utilization: 0.23, status: 'OK' },
    { name: 'API', utilization: 0.56, status: 'OK' }
  ]);

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      const newCoherence = Math.random();
      let state: CoherenceData['state'] = 'THERMAL';

      if (newCoherence >= 0.95) state = 'MERKABAH';
      else if (newCoherence >= 0.75) state = 'RESONANT';
      else if (newCoherence >= 0.50) state = 'SYNCING';

      setCoherence({
        micro: 0.05 + Math.random() * 0.05,
        macro: 0.3 + Math.random() * 0.3,
        coherence: newCoherence,
        state
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStateColor = (state: string) => {
    const colors = {
      THERMAL: '#FF3366',
      SYNCING: '#FFCC33',
      RESONANT: '#33FF99',
      MERKABAH: '#FFD700'
    };
    return colors[state as keyof typeof colors] || '#888888';
  };

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      {/* 3D Trinity Scene */}
      {view3D && (
        <div className="absolute inset-0" style={{ minHeight: '100vh' }}>
          <TrinityScene3D
            coherence={coherence.coherence}
            audioEnabled={audioEnabled}
            onAudioToggle={setAudioEnabled}
          />
        </div>
      )}

      {/* Header Overlay */}
      <div className="absolute top-0 left-0 right-0 p-6 pointer-events-none z-10">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2 opacity-90">
            THE ARCHITECTURE OF RESONANCE
          </h1>
          <p className="text-white/60">Universal Optimization Pattern - Live Monitoring</p>
        </div>
      </div>

      {/* Controls */}
      <div className="absolute top-6 right-6 flex gap-2 z-20">
        <button
          onClick={() => setView3D(!view3D)}
          className="px-4 py-2 bg-blue-600/80 hover:bg-blue-600 text-white rounded backdrop-blur-sm transition-colors"
        >
          {view3D ? '2D View' : '3D View'}
        </button>
        <button
          onClick={() => setAudioEnabled(!audioEnabled)}
          className={`px-4 py-2 rounded backdrop-blur-sm transition-colors ${audioEnabled
            ? 'bg-green-600/80 hover:bg-green-600 text-white'
            : 'bg-gray-600/80 hover:bg-gray-600 text-white'
            }`}
        >
          🎤 {audioEnabled ? 'Audio ON' : 'Audio OFF'}
        </button>
      </div>

      {/* Metrics Overlay */}
      <div className="absolute bottom-0 left-0 right-0 p-6 pointer-events-none z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-6xl mx-auto">
          {/* Coherence Card */}
          <div className="bg-black/50 backdrop-blur-sm rounded-lg p-4 border border-white/10">
            <div className="text-white/60 text-sm mb-2">COHERENCE STATE</div>
            <div
              className="text-3xl font-bold mb-2"
              style={{ color: getStateColor(coherence.state) }}
            >
              {coherence.state}
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-white/60">Micro: {coherence.micro.toFixed(3)}</span>
              <span className="text-white/60">Macro: {coherence.macro.toFixed(3)}</span>
            </div>
            <div className="w-full h-2 bg-gray-800 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full transition-all duration-300"
                style={{
                  width: `${coherence.coherence * 100}%`,
                  backgroundColor: getStateColor(coherence.state)
                }}
              />
            </div>
          </div>

          {/* Hierarchy Card */}
          <div className="bg-black/50 backdrop-blur-sm rounded-lg p-4 border border-white/10">
            <div className="text-white/60 text-sm mb-2">NEURAL HIERARCHY</div>
            <div className="text-white text-sm space-y-1">
              {hierarchy.slice(0, 3).map((level, i) => (
                <div key={i} className="flex justify-between">
                  <span>{level.name}</span>
                  <span className="text-white/60">
                    α:{(level.alpha * 100).toFixed(0)}% β:{(level.beta * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
              <div className="text-white/40 text-xs">+4 more levels...</div>
            </div>
          </div>

          {/* Components Card */}
          <div className="bg-black/50 backdrop-blur-sm rounded-lg p-4 border border-white/10">
            <div className="text-white/60 text-sm mb-2">SYSTEM COMPONENTS</div>
            <div className="text-white text-sm space-y-1">
              {components.slice(0, 4).map((comp, i) => (
                <div key={i} className="flex justify-between">
                  <span>{comp.name}</span>
                  <span className={comp.utilization > 0.8 ? 'text-yellow-400' : 'text-green-400'}>
                    {(comp.utilization * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
              <div className="text-white/40 text-xs">+{components.length - 4} more...</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="absolute bottom-4 left-0 right-0 text-center text-white/40 text-xs pointer-events-none z-10">
        <p>Sentinel Cortex™ 2025 - Minimize Entropy = Maximize Coherence</p>
      </div>
    </div>
  );
}
