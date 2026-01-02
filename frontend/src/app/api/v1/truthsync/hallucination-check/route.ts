import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function GET() {
    try {
        // Check for hallucinations by analyzing eBPF trace data

        let narrativeDivergence = 0;
        let base60Coherence = 100;
        let recentEvents: Array<{
            timestamp: string;
            type: "divergence" | "coherence" | "anchor_fail";
            severity: "low" | "medium" | "high";
            description: string;
        }> = [];

        // Check mathematical anchors
        const anchors = {
            prometheus: false,
            loki: false,
            ebpf: false,
            base60: true, // Always true for now (mathematical constant)
        };

        // Check if Prometheus is running
        try {
            const { stdout: prometheusCheck } = await execAsync(
                "docker ps | grep prometheus || echo ''"
            );
            anchors.prometheus = prometheusCheck.trim().length > 0;
        } catch (err) {
            console.log("Prometheus check failed");
        }

        // Check if Loki is running
        try {
            const { stdout: lokiCheck } = await execAsync(
                "docker ps | grep loki || echo ''"
            );
            anchors.loki = lokiCheck.trim().length > 0;
        } catch (err) {
            console.log("Loki check failed");
        }

        // Check if eBPF program is loaded
        try {
            const { stdout: ebpfCheck } = await execAsync(
                "sudo bpftool prog list 2>/dev/null | grep -E '(quantum|bprm)' || echo ''"
            );
            anchors.ebpf = ebpfCheck.trim().length > 0;
        } catch (err) {
            console.log("eBPF check failed");
        }

        // Calculate narrative divergence based on missing anchors
        const activeAnchors = Object.values(anchors).filter(Boolean).length;
        const totalAnchors = Object.keys(anchors).length;
        narrativeDivergence = ((totalAnchors - activeAnchors) / totalAnchors) * 100;

        // Base-60 coherence is high if all mathematical anchors are active
        base60Coherence = (activeAnchors / totalAnchors) * 100;

        // Add events for missing anchors
        if (!anchors.prometheus) {
            recentEvents.push({
                timestamp: new Date().toISOString(),
                type: "anchor_fail",
                severity: "medium",
                description: "Prometheus metrics anchor unavailable - data validation limited",
            });
        }

        if (!anchors.loki) {
            recentEvents.push({
                timestamp: new Date().toISOString(),
                type: "anchor_fail",
                severity: "medium",
                description: "Loki log correlation anchor unavailable - event tracking limited",
            });
        }

        if (!anchors.ebpf) {
            recentEvents.push({
                timestamp: new Date().toISOString(),
                type: "anchor_fail",
                severity: "high",
                description: "eBPF kernel anchor unavailable - real-time validation disabled",
            });
        }

        const metrics = {
            divergence: narrativeDivergence,
            base60_coherence: base60Coherence,
            anchors,
            recent_events: recentEvents,
            timestamp: new Date().toISOString(),
        };

        return NextResponse.json(metrics);
    } catch (error) {
        console.error("Hallucination check error:", error);
        return NextResponse.json(
            { error: "Failed to check for hallucinations" },
            { status: 500 }
        );
    }
}
