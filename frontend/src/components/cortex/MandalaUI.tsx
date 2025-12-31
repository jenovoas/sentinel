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
}

const MandalaUI: React.FC<MandalaProps> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [hoverInfo, setHoverInfo] = useState<string | null>(null);

    // Default mockup data if none provided
    const zonesData = data?.zones || Array.from({ length: 60 }, (_, i) => {
        const isPrime = [1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59].includes(i);
        return {
            residue: i,
            threat: isPrime ? 0.8 : 0.2, // Simulated threat
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
        const radius = 250;

        // Define Gradients
        const defs = svg.append("defs");

        // Gold Glow
        const gradientGold = defs.append("radialGradient")
            .attr("id", "gradGold")
            .attr("cx", "50%")
            .attr("cy", "50%")
            .attr("r", "50%");
        gradientGold.append("stop").attr("offset", "0%").attr("stop-color", "#FFD700").attr("stop-opacity", 0.8);
        gradientGold.append("stop").attr("offset", "100%").attr("stop-color", "#B8860B").attr("stop-opacity", 0.6);

        // Red Warning
        const gradientRed = defs.append("radialGradient")
            .attr("id", "gradRed")
            .attr("cx", "50%")
            .attr("cy", "50%")
            .attr("r", "50%");
        gradientRed.append("stop").attr("offset", "0%").attr("stop-color", "#FF4444").attr("stop-opacity", 0.9);
        gradientRed.append("stop").attr("offset", "100%").attr("stop-color", "#8B0000").attr("stop-opacity", 0.7);

        // Green Safe
        const gradientGreen = defs.append("radialGradient")
            .attr("id", "gradGreen")
            .attr("cx", "50%")
            .attr("cy", "50%")
            .attr("r", "50%");
        gradientGreen.append("stop").attr("offset", "0%").attr("stop-color", "#00FF7F").attr("stop-opacity", 0.8);
        gradientGreen.append("stop").attr("offset", "100%").attr("stop-color", "#006400").attr("stop-opacity", 0.6);

        // Background Circle (Void)
        svg.append("circle")
            .attr("cx", centerX)
            .attr("cy", centerY)
            .attr("r", radius + 20)
            .attr("fill", "#050505")
            .attr("stroke", "#333")
            .attr("stroke-width", 1);

        // Draw 60 Zones (The Flower of Life / Akasha)
        const zonesGroup = svg.append("g");

        zonesData.forEach((zone, i) => {
            const angle = (i / 60) * 2 * Math.PI - (Math.PI / 2); // Start at 12 o'clock
            const x = centerX + Math.cos(angle) * (radius * 0.8);
            const y = centerY + Math.sin(angle) * (radius * 0.8);

            const nodeSize = 8 + (zone.threat * 10);
            const colorUrl = zone.threat > 0.6 ? "url(#gradRed)" : zone.isDissonant ? "url(#gradGold)" : "url(#gradGreen)";

            zonesGroup.append("circle")
                .attr("cx", x)
                .attr("cy", y)
                .attr("r", nodeSize)
                .attr("fill", colorUrl)
                .attr("stroke", zone.isDissonant ? "#FFD700" : "none")
                .attr("stroke-width", zone.isDissonant ? 2 : 0)
                .style("cursor", "pointer")
                .style("filter", "drop-shadow(0px 0px 4px rgba(255,255,255,0.2))")
                .on("mouseenter", () => {
                    setHoverInfo(`Base-60: ${i} | Threat: ${(zone.threat * 100).toFixed(1)}% | ${zone.isDissonant ? "DISSONANT" : "HARMONIC"}`);
                    d3.select(event?.target as Element).transition().duration(200).attr("r", nodeSize * 1.5);
                })
                .on("mouseleave", () => {
                    setHoverInfo(null);
                    d3.select(event?.target as Element).transition().duration(200).attr("r", nodeSize);
                });

            // Connecting lines for Phi relationships (visual aesthetic)
            if (i % 5 === 0) {
                zonesGroup.append("line")
                    .attr("x1", centerX)
                    .attr("y1", centerY)
                    .attr("x2", x)
                    .attr("y2", y)
                    .attr("stroke", "#FFFFFF")
                    .attr("stroke-opacity", 0.1)
                    .attr("stroke-width", 1);
            }
        });

        // Central Akasha Core
        svg.append("circle")
            .attr("cx", centerX)
            .attr("cy", centerY)
            .attr("r", 30)
            .attr("fill", "none")
            .attr("stroke", "#FFD700")
            .attr("stroke-width", 2)
            .style("opacity", 0.8);

        // Pulsing animation for core
        svg.append("circle")
            .attr("cx", centerX)
            .attr("cy", centerY)
            .attr("r", 10)
            .attr("fill", "#FFD700")
            .append("animate")
            .attr("attributeName", "r")
            .attr("values", "10;25;10")
            .attr("dur", "4s")
            .attr("repeatCount", "indefinite");

    }, [zonesData]);

    return (
        <div className="flex flex-col items-center justify-center bg-black/90 p-4 border border-zinc-800 rounded-xl relative">
            <h3 className="text-yellow-500 font-mono mb-2 text-lg tracking-widest">SENTINEL AKASHA MANDALA</h3>
            <div className="relative">
                <svg ref={svgRef} width={600} height={600} className="w-full max-w-[600px] h-auto" />
                {hoverInfo && (
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-black/80 border border-yellow-500/50 px-4 py-2 rounded text-xs text-white pointer-events-none backdrop-blur-sm">
                        {hoverInfo}
                    </div>
                )}
            </div>
            <div className="flex gap-4 mt-4 text-xs font-mono text-zinc-500">
                <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>HARMONIC (Safe)</span>
                <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>PRIME (Resonance)</span>
                <span className="flex items-center"><span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>THREAT (Blocked)</span>
            </div>
        </div>
    );
};

export default MandalaUI;
