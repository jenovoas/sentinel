"use client";

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface MandalaProps {
    data?: {
        zones: Array<{
            residue: number;
            threat: number; // 0.0 to 1.0
            isDissonant: boolean;
        }>;
    };
    resonance?: number; // 0.0 to 1.0
}

const MandalaUI: React.FC<MandalaProps> = ({ data, resonance = 0.8 }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [hoverInfo, setHoverInfo] = useState<string | null>(null);

    // Default mockup data if none provided - Uses Base-60 architecture
    const zonesData = data?.zones || Array.from({ length: 60 }, (_, i) => {
        const isPrime = [1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59].includes(i);
        return {
            residue: i,
            threat: isPrime ? Math.random() * 0.4 : Math.random() * 0.1,
            isDissonant: isPrime
        };
    });

    useEffect(() => {
        if (!svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove(); // Clean previous render

        const width = 600;
        const height = 600;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = 260;

        // Define Gradients and Filters
        const defs = svg.append("defs");

        // Glow Filter
        const filter = defs.append("filter").attr("id", "glow");
        filter.append("feGaussianBlur").attr("stdDeviation", "3.5").attr("result", "coloredBlur");
        const feMerge = filter.append("feMerge");
        feMerge.append("feMergeNode").attr("in", "coloredBlur");
        feMerge.append("feMergeNode").attr("in", "SourceGraphic");

        // Sovereign Purple Gradient
        const gradPurple = defs.append("radialGradient").attr("id", "gradPurple");
        gradPurple.append("stop").attr("offset", "0%").attr("stop-color", "#A855F7").attr("stop-opacity", 0.9);
        gradPurple.append("stop").attr("offset", "100%").attr("stop-color", "#7E22CE").attr("stop-opacity", 0.5);

        // Sovereign Cyan Gradient
        const gradCyan = defs.append("radialGradient").attr("id", "gradCyan");
        gradCyan.append("stop").attr("offset", "0%").attr("stop-color", "#22D3EE").attr("stop-opacity", 0.9);
        gradCyan.append("stop").attr("offset", "100%").attr("stop-color", "#0891B2").attr("stop-opacity", 0.5);

        // Gold Resonance
        const gradGold = defs.append("radialGradient").attr("id", "gradGold");
        gradGold.append("stop").attr("offset", "0%").attr("stop-color", "#FDE047").attr("stop-opacity", 0.9);
        gradGold.append("stop").attr("offset", "100%").attr("stop-color", "#EAB308").attr("stop-opacity", 0.6);

        // Draw Recursive Orbits
        const orbitsGroup = svg.append("g").attr("class", "orbits");
        for (let i = 1; i <= 3; i++) {
            orbitsGroup.append("circle")
                .attr("cx", centerX)
                .attr("cy", centerY)
                .attr("r", radius * (i * 0.3))
                .attr("fill", "none")
                .attr("stroke", "white")
                .attr("stroke-opacity", 0.05)
                .attr("stroke-width", 1)
                .attr("stroke-dasharray", "4,4")
                .append("animateTransform")
                .attr("attributeName", "transform")
                .attr("type", "rotate")
                .attr("from", `${i % 2 === 0 ? 0 : 360} ${centerX} ${centerY}`)
                .attr("to", `${i % 2 === 0 ? 360 : 0} ${centerX} ${centerY}`)
                .attr("dur", `${30 / i}s`)
                .attr("repeatCount", "indefinite");
        }

        // Draw Akasha Nodes (The Flower of Perception)
        const nodesGroup = svg.append("g").attr("class", "nodes");

        zonesData.forEach((zone, i) => {
            const angle = (i / 60) * 2 * Math.PI - (Math.PI / 2);
            const r = radius * 0.85;
            const x = centerX + Math.cos(angle) * r;
            const y = centerY + Math.sin(angle) * r;

            const isPrime = zone.isDissonant;
            const nodeR = isPrime ? 5 : 3;
            const color = isPrime ? "url(#gradGold)" : (i % 2 === 0 ? "url(#gradCyan)" : "url(#gradPurple)");

            // Connection Lines (Neural Paths)
            if (i % 5 === 0) {
                nodesGroup.append("line")
                    .attr("x1", centerX)
                    .attr("y1", centerY)
                    .attr("x2", x)
                    .attr("y2", y)
                    .attr("stroke", isPrime ? "#FDE047" : "white")
                    .attr("stroke-opacity", isPrime ? 0.2 : 0.05)
                    .attr("stroke-width", isPrime ? 1.5 : 0.5)
                    .style("filter", isPrime ? "url(#glow)" : "none");
            }

            // The Node itself
            nodesGroup.append("circle")
                .attr("cx", x)
                .attr("cy", y)
                .attr("r", nodeR)
                .attr("fill", color)
                .style("filter", isPrime ? "url(#glow)" : "none")
                .style("cursor", "pointer")
                .on("mouseenter", (event) => {
                    setHoverInfo(`Base-60 Neuron: ${i} | Depth: ${(resonance * 100).toFixed(1)}% | ${isPrime ? "SYNC_PRIMARY" : "SYNC_NODE"}`);
                    d3.select(event.currentTarget).transition().duration(200).attr("r", nodeR * 2.5).attr("fill", "#FFF");
                })
                .on("mouseleave", (event) => {
                    setHoverInfo(null);
                    d3.select(event.currentTarget).transition().duration(200).attr("r", nodeR).attr("fill", color);
                });

            // Pulsing secondary circles for primes
            if (isPrime) {
                nodesGroup.append("circle")
                    .attr("cx", x)
                    .attr("cy", y)
                    .attr("r", nodeR)
                    .attr("fill", "none")
                    .attr("stroke", "#FDE047")
                    .attr("stroke-opacity", 0.5)
                    .append("animate")
                    .attr("attributeName", "r")
                    .attr("values", `${nodeR};${nodeR * 4};${nodeR}`)
                    .attr("dur", "3s")
                    .attr("repeatCount", "indefinite");
            }
        });

        // The Central Sovereign Singularity
        const core = svg.append("g").attr("class", "core");

        // Background Glow
        core.append("circle")
            .attr("cx", centerX)
            .attr("cy", centerY)
            .attr("r", 40)
            .attr("fill", "url(#gradPurple)")
            .attr("opacity", 0.2)
            .style("filter", "blur(20px)");

        // Main Core
        core.append("circle")
            .attr("cx", centerX)
            .attr("cy", centerY)
            .attr("r", 25)
            .attr("fill", "url(#gradCyan)")
            .style("filter", "url(#glow)")
            .append("animate")
            .attr("attributeName", "r")
            .attr("values", "25;30;25")
            .attr("dur", "4s")
            .attr("repeatCount", "indefinite");

        // The Eye of Synthesis
        core.append("circle")
            .attr("cx", centerX)
            .attr("cy", centerY)
            .attr("r", 8)
            .attr("fill", "#FFF")
            .style("filter", "url(#glow)");

    }, [zonesData, resonance]);

    return (
        <div className="relative flex items-center justify-center">
            <svg ref={svgRef} width={600} height={600} className="w-full h-full max-w-[600px] max-h-[600px] drop-shadow-[0_0_30px_rgba(34,211,238,0.15)]" />

            <AnimatePresence>
                {hoverInfo && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-950/90 border border-cyan-500/50 px-6 py-3 rounded-2xl text-[10px] font-black text-cyan-400 pointer-events-none backdrop-blur-3xl shadow-2xl uppercase tracking-[0.2em] italic z-20"
                    >
                        {hoverInfo}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Neural Legend Overlay */}
            <div className="absolute -bottom-4 flex gap-8 text-[8px] font-black text-gray-500 uppercase tracking-widest italic animate-pulse">
                <span className="flex items-center"><div className="w-1.5 h-1.5 rounded-full bg-cyan-400 mr-2 shadow-[0_0_5px_rgba(34,211,238,0.5)]" /> Human Ingress</span>
                <span className="flex items-center"><div className="w-1.5 h-1.5 rounded-full bg-purple-400 mr-2 shadow-[0_0_5px_rgba(168,85,247,0.5)]" /> AI Synthesis</span>
                <span className="flex items-center"><div className="w-1.5 h-1.5 rounded-full bg-yellow-400 mr-2 shadow-[0_0_5px_rgba(253,224,71,0.5)]" /> Resonance Point</span>
            </div>
        </div>
    );
};

export default MandalaUI;
