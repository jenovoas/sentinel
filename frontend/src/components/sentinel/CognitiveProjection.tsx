"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Zap, ShieldAlert, Cpu } from "lucide-react";

interface EventNode {
    x: number;
    y: number;
    size: number;
    speed: number;
    opacity: number;
    type: "gold" | "anomaly" | "noise";
    label: string;
    pulse: number;
}

import { useSentinelStatus } from "@/hooks/useSentinelStatus";

export const CognitiveProjection = () => {
    const { status } = useSentinelStatus();
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [stats, setStats] = useState({ events: 1248, correlations: 85 });
    const nodesRef = useRef<EventNode[]>([]);
    const animationRef = useRef<number>(0);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const resize = () => {
            const rect = canvas.parentElement?.getBoundingClientRect();
            if (rect) {
                canvas.width = rect.width;
                canvas.height = 400;
            }
        };

        window.addEventListener("resize", resize);
        resize();

        // Initialize some nodes
        const types: ("gold" | "anomaly" | "noise")[] = ["gold", "anomaly", "noise"];
        const labels = [
            "SYS_CALL_INT", "MEM_ALLOC_VIO", "NET_PKT_RECV",
            "EBPF_PROBE_HIT", "RING0_AUTH_FAIL", "GOLD_TRUTH_SYNC"
        ];

        const createNode = (isInitial = false): EventNode => ({
            x: isInitial ? Math.random() * canvas.width : canvas.width + 50,
            y: Math.random() * canvas.height,
            size: Math.random() * 3 + 2,
            speed: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.5,
            type: types[Math.floor(Math.random() * types.length)],
            label: labels[Math.floor(Math.random() * labels.length)],
            pulse: 0
        });

        nodesRef.current = Array.from({ length: 30 }, () => createNode(true));

        const render = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw background grid
            ctx.strokeStyle = "rgba(34, 211, 238, 0.05)";
            ctx.lineWidth = 0.5;
            const step = 40;
            for (let x = 0; x < canvas.width; x += step) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += step) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }

            // Update and draw nodes
            nodesRef.current.forEach((node, index) => {
                node.x -= node.speed;
                node.pulse += 0.05;

                // Reset node if out of bounds
                if (node.x < -100) {
                    nodesRef.current[index] = createNode();
                }

                const color =
                    node.type === "gold" ? "34, 211, 238" :
                        node.type === "anomaly" ? "244, 63, 94" :
                            "148, 163, 184";

                const glowSize = node.type === "anomaly" ? 15 + Math.sin(node.pulse) * 5 : 8;

                // Draw Glow
                ctx.shadowBlur = glowSize;
                ctx.shadowColor = `rgba(${color}, ${node.opacity})`;
                ctx.fillStyle = `rgba(${color}, ${node.opacity})`;

                ctx.beginPath();
                ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;

                // Draw Label for important nodes
                if (node.type !== "noise") {
                    ctx.font = "10px monospace";
                    ctx.fillStyle = `rgba(${color}, ${node.opacity * 0.7})`;
                    ctx.fillText(node.label, node.x + 10, node.y + 4);

                    // Connection lines to nearby nodes
                    nodesRef.current.forEach((other, otherIdx) => {
                        if (index === otherIdx) return;
                        const dist = Math.hypot(node.x - other.x, node.y - other.y);
                        if (dist < 100 && (node.type === "gold" || node.type === "anomaly")) {
                            ctx.strokeStyle = `rgba(${color}, ${0.1 * (1 - dist / 100)})`;
                            ctx.beginPath();
                            ctx.moveTo(node.x, node.y);
                            ctx.lineTo(other.x, other.y);
                            ctx.stroke();
                        }
                    });
                }
            });

            animationRef.current = requestAnimationFrame(render);
        };

        render();

        return () => {
            window.removeEventListener("resize", resize);
            cancelAnimationFrame(animationRef.current);
        };
    }, []);

    return (
        <Card className="bg-slate-950/50 backdrop-blur-2xl border-white/5 overflow-hidden relative group h-[500px]">
            <div className="absolute inset-0 bg-gradient-to-t from-[#020617] via-transparent to-transparent pointer-events-none z-10" />

            <CardHeader className="relative z-20 pb-0 flex flex-row items-center justify-between">
                <div>
                    <CardTitle className="text-sm font-medium text-cyan-200/50 uppercase tracking-[0.3em] flex items-center gap-2">
                        <Cpu className="w-4 h-4 text-cyan-400" />
                        AI Cognitive Projection
                    </CardTitle>
                    <p className="text-[10px] text-gray-500 font-mono mt-1 uppercase tracking-widest">
                        Neural Synapse Stream // Latency: 0.8ms // Mode: Deep Observation
                    </p>
                </div>
                <div className="flex gap-4">
                    <div className="text-right">
                        <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-tighter">Gold Events</p>
                        <p className="text-lg font-mono text-white">{status?.db_transactions || "1.2k"}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-[10px] text-rose-400 font-bold uppercase tracking-tighter">Anomalies</p>
                        <p className="text-lg font-mono text-white">{status?.active_threats || "0"}</p>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="p-0 relative h-full">
                <canvas
                    ref={canvasRef}
                    className="w-full h-full cursor-crosshair opacity-80"
                />

                {/* HUD Overlays */}
                <div className="absolute bottom-12 left-6 z-20 space-y-2">
                    <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-md px-3 py-1.5 backdrop-blur-md">
                        <Activity className="w-3 h-3 text-cyan-400 animate-pulse" />
                        <span className="text-[10px] font-mono text-cyan-100 uppercase tracking-widest">Processing Kernel Pulse...</span>
                    </div>
                    <div className="flex items-center gap-3 bg-rose-500/10 border border-rose-500/20 rounded-md px-3 py-1.5 backdrop-blur-md">
                        <ShieldAlert className="w-3 h-3 text-rose-400" />
                        <span className="text-[10px] font-mono text-rose-100 uppercase tracking-widest text-shadow-glow">Potential Stack Overflow in PID 821</span>
                    </div>
                </div>

                <div className="absolute right-6 bottom-12 z-20 bg-black/40 border border-white/5 p-4 rounded-xl backdrop-blur-xl">
                    <p className="text-[10px] text-gray-400 uppercase font-black mb-3 tracking-widest">Cognitive Mapping</p>
                    <div className="space-y-3">
                        <div className="flex items-center gap-4">
                            <div className="w-24 h-1 bg-white/10 rounded-full overflow-hidden">
                                <div className="w-[85%] h-full bg-cyan-500 glow-cyan" />
                            </div>
                            <span className="text-[9px] font-mono text-gray-300">PATTERN MATCH</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="w-24 h-1 bg-white/10 rounded-full overflow-hidden">
                                <div className="w-[45%] h-full bg-purple-500 glow-purple" />
                            </div>
                            <span className="text-[9px] font-mono text-gray-300">HEURISTIC FLOW</span>
                        </div>
                    </div>
                </div>
            </CardContent>

            <div className="absolute inset-0 border border-cyan-500/10 pointer-events-none z-30 m-px rounded-xl" />
        </Card>
    );
};
