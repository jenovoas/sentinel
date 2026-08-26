import React, { useRef, useEffect, useState, useMemo, useCallback } from "react";
import { HologramNode } from "../../lib/types";

interface HexagonalLatticeViewerProps {
  nodes: HologramNode[];
  totalEnergy: number;
  coherenceRaw: number;
  activeCyclePhase: number;
  isConnected: boolean;
  onSelectNode?: (node: HologramNode | null) => void;
  selectedNodeIndex?: number | null;
}

interface NodeLayout {
  node: HologramNode;
  x: number;
  y: number;
  ring: number;
  angle: number;
}

export const HexagonalLatticeViewer: React.FC<HexagonalLatticeViewerProps> = ({
  nodes,
  totalEnergy,
  coherenceRaw,
  activeCyclePhase,
  isConnected,
  onSelectNode,
  selectedNodeIndex = null,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [hoveredNode, setHoveredNode] = useState<HologramNode | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  const layout = useMemo<NodeLayout[]>(() => {
    if (!nodes || nodes.length === 0) return [];

    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    const spacing = Math.min(dimensions.width, dimensions.height) / 12;

    const result: NodeLayout[] = [];
    let nodeIdx = 0;

    if (nodes.length > 0) {
      result.push({
        node: nodes[0],
        x: centerX,
        y: centerY,
        ring: 0,
        angle: 0,
      });
      nodeIdx++;
    }

    let ring = 1;
    while (nodeIdx < nodes.length && ring < 10) {
      const countInRing = 6 * ring;
      for (let i = 0; i < countInRing && nodeIdx < nodes.length; i++) {
        const angle = (i * 2 * Math.PI) / countInRing - Math.PI / 2;
        const radius = ring * spacing;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);

        result.push({
          node: nodes[nodeIdx],
          x,
          y,
          ring,
          angle,
        });
        nodeIdx++;
      }
      ring++;
    }

    return result;
  }, [nodes, dimensions]);

  const handleResize = useCallback(() => {
    if (containerRef.current) {
      const { clientWidth, clientHeight } = containerRef.current;
      setDimensions({
        width: clientWidth || 800,
        height: clientHeight || 600,
      });
    }
  }, []);

  useEffect(() => {
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [handleResize]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animFrameId: number;

    const render = () => {
      const { width, height } = dimensions;
      ctx.clearRect(0, 0, width, height);

      // Background ambient glow
      const bgGrad = ctx.createRadialGradient(
        width / 2,
        height / 2,
        20,
        width / 2,
        height / 2,
        Math.max(width, height) / 1.5
      );
      bgGrad.addColorStop(0, "rgba(10, 25, 40, 0.4)");
      bgGrad.addColorStop(0.5, "rgba(5, 12, 20, 0.6)");
      bgGrad.addColorStop(1, "rgba(2, 4, 8, 0.95)");
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Draw connecting flux lines
      ctx.lineWidth = 1;
      for (let i = 0; i < layout.length; i++) {
        for (let j = i + 1; j < layout.length; j++) {
          const dx = layout[i].x - layout[j].x;
          const dy = layout[i].y - layout[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const maxConnDist = (Math.min(width, height) / 12) * 1.5;

          if (dist <= maxConnDist) {
            const avgAmp = (layout[i].node.amplitude_u16 + layout[j].node.amplitude_u16) / 2;
            const alpha = Math.min(0.6, (avgAmp / 65535) * 0.5 + 0.05);

            ctx.beginPath();
            ctx.strokeStyle = `rgba(0, 229, 255, ${alpha})`;
            ctx.moveTo(layout[i].x, layout[i].y);
            ctx.lineTo(layout[j].x, layout[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw each crystal node
      const time = Date.now() / 1000;
      for (const item of layout) {
        const { node, x, y } = item;
        const normAmp = node.amplitude_u16 / 65535;
        const isSelected = selectedNodeIndex === node.index;
        const isHovered = hoveredNode?.index === node.index;

        const pulseScale = 1 + 0.15 * Math.sin(time * 2 + (node.index * 17) / 10);
        const baseRadius = 6 + normAmp * 8;
        const nodeRadius = (isSelected || isHovered ? baseRadius * 1.3 : baseRadius) * pulseScale;

        // Outer aura gradient
        const auraGrad = ctx.createRadialGradient(x, y, 1, x, y, nodeRadius * 2.8);
        if (normAmp > 0.75) {
          auraGrad.addColorStop(0, "rgba(255, 255, 255, 0.9)");
          auraGrad.addColorStop(0.3, "rgba(255, 170, 0, 0.6)");
          auraGrad.addColorStop(0.7, "rgba(0, 229, 255, 0.2)");
          auraGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
        } else if (normAmp > 0.4) {
          auraGrad.addColorStop(0, "rgba(0, 229, 255, 0.9)");
          auraGrad.addColorStop(0.5, "rgba(0, 150, 255, 0.4)");
          auraGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
        } else {
          auraGrad.addColorStop(0, "rgba(0, 180, 216, 0.6)");
          auraGrad.addColorStop(0.6, "rgba(2, 62, 138, 0.2)");
          auraGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
        }

        ctx.fillStyle = auraGrad;
        ctx.beginPath();
        ctx.arc(x, y, nodeRadius * 2.8, 0, 2 * Math.PI);
        ctx.fill();

        // Node core
        ctx.fillStyle = isSelected
          ? "#ffea00"
          : normAmp > 0.7
          ? "#ffffff"
          : normAmp > 0.3
          ? "#00e5ff"
          : "#0077b6";
        ctx.beginPath();
        ctx.arc(x, y, nodeRadius, 0, 2 * Math.PI);
        ctx.fill();

        // Selection ring
        if (isSelected || isHovered) {
          ctx.strokeStyle = "#ffea00";
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(x, y, nodeRadius + 4, 0, 2 * Math.PI);
          ctx.stroke();
        }

        // Node index text (center node or high zoom)
        if (layout.length <= 64 || isSelected || isHovered) {
          ctx.fillStyle = "rgba(255, 255, 255, 0.75)";
          ctx.font = "9px monospace";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(`${node.index}`, x, y);
        }
      }

      animFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animFrameId);
    };
  }, [layout, dimensions, selectedNodeIndex, hoveredNode]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let found: HologramNode | null = null;
    for (const item of layout) {
      const dx = mouseX - item.x;
      const dy = mouseY - item.y;
      if (Math.sqrt(dx * dx + dy * dy) <= 15) {
        found = item.node;
        break;
      }
    }
    setHoveredNode(found);
  };

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    for (const item of layout) {
      const dx = mouseX - item.x;
      const dy = mouseY - item.y;
      if (Math.sqrt(dx * dx + dy * dy) <= 18) {
        onSelectNode?.(item.node);
        return;
      }
    }
    onSelectNode?.(null);
  };

  return (
    <div ref={containerRef} className="relative w-full h-full min-h-[500px] overflow-hidden rounded-3xl border border-white/10 bg-black/90 shadow-2xl">
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoveredNode(null)}
        onClick={handleClick}
        className="w-full h-full cursor-crosshair block"
      />

      {/* Live Telemetry HUD Overlay */}
      <div className="absolute top-4 left-4 pointer-events-none flex flex-col gap-2">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/60 backdrop-blur-md border border-white/10 text-xs text-white">
          <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
          <span className="font-mono font-bold tracking-wider uppercase">
            {isConnected ? "Cortex Live SHM" : "Lattice Emulation"}
          </span>
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-black/60 backdrop-blur-md border border-white/10 text-[11px] text-gray-300 font-mono">
          <span>Nodos: </span>
          <span className="text-cyan-400 font-bold">{nodes.length}</span>
          <span className="mx-2">·</span>
          <span>Coherencia: </span>
          <span className="text-emerald-400 font-bold">{((coherenceRaw / 12960000) * 100).toFixed(1)}%</span>
          <span className="mx-2">·</span>
          <span>Energía: </span>
          <span className="text-amber-400 font-bold">{totalEnergy.toLocaleString()}</span>
        </div>
      </div>

      {/* 17s Breathing Phase Indicator */}
      <div className="absolute top-4 right-4 pointer-events-none flex items-center gap-3 px-4 py-2 rounded-xl bg-black/60 backdrop-blur-md border border-white/10">
        <div className="flex flex-col items-end">
          <span className="text-[10px] uppercase font-mono tracking-widest text-gray-400">Pulso Armónico 17s</span>
          <span className="text-sm font-mono font-bold text-cyan-300">
            {(activeCyclePhase * 17).toFixed(1)}s / 17.0s
          </span>
        </div>
        <div className="w-8 h-8 relative flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <path
              className="text-gray-800"
              strokeWidth="3"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className="text-cyan-400 transition-all duration-100"
              strokeDasharray={`${activeCyclePhase * 100}, 100`}
              strokeWidth="3"
              strokeLinecap="round"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
        </div>
      </div>

      {/* Hover Node Tooltip */}
      {hoveredNode && (
        <div className="absolute bottom-4 left-4 pointer-events-none px-4 py-3 rounded-2xl bg-black/80 backdrop-blur-md border border-cyan-500/30 text-white font-mono text-xs shadow-xl space-y-1">
          <div className="text-cyan-400 font-bold flex items-center gap-2">
            <span>Cristal #{hoveredNode.index}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">SPA 60⁴</span>
          </div>
          <p className="text-gray-400">Amplitud Raw: <span className="text-white font-bold">{hoveredNode.amplitude_raw.toLocaleString()}</span></p>
          <p className="text-gray-400">Amplitud u16: <span className="text-amber-400 font-bold">{hoveredNode.amplitude_u16}</span></p>
          <p className="text-gray-400">Fase Raw: <span className="text-white font-bold">{hoveredNode.phase_raw.toLocaleString()}</span></p>
        </div>
      )}
    </div>
  );
};
