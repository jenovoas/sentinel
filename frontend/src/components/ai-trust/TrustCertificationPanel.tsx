"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Shield, CheckCircle, AlertTriangle, XCircle, TrendingUp, Database, Hash, Activity } from "lucide-react";

interface TrustMetrics {
    overallScore: number; // 0-100
    dataSupport: number; // 0-100
    base60Checksum: boolean;
    feedbackLoopHealth: number; // 0-100
    latency: number; // microseconds
    hallucinationRate: number; // 0-1
    evidenceCount: number;
    lastUpdate: string;
}

interface TrustCertificationPanelProps {
    refreshInterval: number;
    isPaused: boolean;
}

export function TrustCertificationPanel({ refreshInterval, isPaused }: TrustCertificationPanelProps) {
    const [metrics, setMetrics] = useState<TrustMetrics>({
        overallScore: 0,
        dataSupport: 0,
        base60Checksum: false,
        feedbackLoopHealth: 0,
        latency: 0,
        hallucinationRate: 0,
        evidenceCount: 0,
        lastUpdate: new Date().toISOString(),
    });

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (isPaused) return;

        const fetchMetrics = async () => {
            try {
                setIsLoading(true);
                setError(null);

                // Fetch from TruthSync API
                const truthSyncResponse = await fetch("/api/v1/truthsync/stats");
                const truthSyncData = await truthSyncResponse.json();

                // Fetch from Guardian Alpha (eBPF metrics)
                const guardianResponse = await fetch("/api/v1/guardian/metrics");
                const guardianData = await guardianResponse.json();

                // Calculate overall trust score
                const overallScore = calculateTrustScore(truthSyncData, guardianData);

                setMetrics({
                    overallScore,
                    dataSupport: truthSyncData.data_support || 0,
                    base60Checksum: truthSyncData.base60_valid || false,
                    feedbackLoopHealth: truthSyncData.feedback_health || 0,
                    latency: truthSyncData.latency_us || 0,
                    hallucinationRate: truthSyncData.hallucination_rate || 0,
                    evidenceCount: guardianData.evidence_count || 0,
                    lastUpdate: new Date().toISOString(),
                });

                setIsLoading(false);
            } catch (err) {
                console.error("Failed to fetch trust metrics:", err);
                setError("Failed to connect to trust validation services");
                setIsLoading(false);

                // Use simulated data for development
                setMetrics(getSimulatedMetrics());
            }
        };

        fetchMetrics();
        const interval = setInterval(fetchMetrics, refreshInterval);

        return () => clearInterval(interval);
    }, [refreshInterval, isPaused]);

    const trustLevel = getTrustLevel(metrics.overallScore);

    return (
        <div className="bg-slate-900/40 backdrop-blur-3xl border border-purple-500/20 rounded-[40px] p-8 shadow-[0_0_60px_rgba(168,85,247,0.1)]">
            {/* Main Trust Score */}
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-6">
                    <motion.div
                        className={`relative w-32 h-32 rounded-full flex items-center justify-center ${trustLevel.bgClass}`}
                        animate={{ scale: [1, 1.02, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/10 to-transparent" />
                        <div className="text-center z-10">
                            <div className={`text-4xl font-black ${trustLevel.textClass}`}>
                                {isLoading ? "..." : Math.round(metrics.overallScore)}
                            </div>
                            <div className="text-[9px] font-black text-gray-400 uppercase tracking-wider">
                                Trust Score
                            </div>
                        </div>
                        {!isLoading && (
                            <motion.div
                                className={`absolute inset-0 rounded-full border-4 ${trustLevel.borderClass}`}
                                initial={{ scale: 1, opacity: 0.5 }}
                                animate={{ scale: 1.2, opacity: 0 }}
                                transition={{ duration: 2, repeat: Infinity }}
                            />
                        )}
                    </motion.div>

                    <div>
                        <h3 className={`text-3xl font-black uppercase tracking-tight ${trustLevel.textClass}`}>
                            {trustLevel.label}
                        </h3>
                        <p className="text-sm text-gray-400 font-black uppercase tracking-wider italic mt-1">
                            {trustLevel.description}
                        </p>
                        <div className="flex items-center gap-2 mt-3">
                            {trustLevel.icon}
                            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">
                                Last Update: {new Date(metrics.lastUpdate).toLocaleTimeString()}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Status Badge */}
                <div className={`px-6 py-3 rounded-2xl border-2 ${trustLevel.borderClass} ${trustLevel.bgClass}`}>
                    <div className="flex items-center gap-3">
                        {trustLevel.statusIcon}
                        <div>
                            <div className={`text-xs font-black uppercase tracking-wider ${trustLevel.textClass}`}>
                                {metrics.overallScore >= 90 ? "CERTIFIED" : metrics.overallScore >= 70 ? "CAUTION" : "BLOCKED"}
                            </div>
                            <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest">
                                {metrics.overallScore >= 90 ? "Safe to Trust" : metrics.overallScore >= 70 ? "Verify Manually" : "Do Not Trust"}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center gap-3"
                >
                    <AlertTriangle size={20} className="text-rose-400" />
                    <div>
                        <div className="text-sm font-black text-rose-400">{error}</div>
                        <div className="text-xs text-gray-500">Using simulated data for demonstration</div>
                    </div>
                </motion.div>
            )}

            {/* Detailed Metrics Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    icon={<Database size={20} />}
                    label="Data Support"
                    value={`${Math.round(metrics.dataSupport)}%`}
                    status={metrics.dataSupport >= 80 ? "good" : metrics.dataSupport >= 60 ? "warning" : "critical"}
                    description="Prometheus/Loki validation"
                />

                <MetricCard
                    icon={<Hash size={20} />}
                    label="Base-60 Checksum"
                    value={metrics.base60Checksum ? "VALID" : "INVALID"}
                    status={metrics.base60Checksum ? "good" : "critical"}
                    description="Mathematical harmony check"
                />

                <MetricCard
                    icon={<Activity size={20} />}
                    label="Feedback Loop"
                    value={`${Math.round(metrics.feedbackLoopHealth)}%`}
                    status={metrics.feedbackLoopHealth >= 90 ? "good" : metrics.feedbackLoopHealth >= 70 ? "warning" : "critical"}
                    description="TruthSync responsiveness"
                />

                <MetricCard
                    icon={<TrendingUp size={20} />}
                    label="Latency"
                    value={`${metrics.latency.toFixed(2)}μs`}
                    status={metrics.latency < 5 ? "good" : metrics.latency < 10 ? "warning" : "critical"}
                    description="Validation speed"
                />
            </div>

            {/* Additional Stats */}
            <div className="mt-6 pt-6 border-t border-white/5 grid grid-cols-3 gap-6">
                <StatItem label="Hallucination Rate" value={`${(metrics.hallucinationRate * 100).toFixed(2)}%`} />
                <StatItem label="Evidence Records" value={metrics.evidenceCount.toLocaleString()} />
                <StatItem label="Trust Threshold" value="90%" />
            </div>
        </div>
    );
}

// Helper Components

interface MetricCardProps {
    icon: React.ReactNode;
    label: string;
    value: string;
    status: "good" | "warning" | "critical";
    description: string;
}

function MetricCard({ icon, label, value, status, description }: MetricCardProps) {
    const statusConfig = {
        good: {
            bg: "bg-emerald-500/10",
            border: "border-emerald-500/30",
            text: "text-emerald-400",
            icon: "text-emerald-400",
        },
        warning: {
            bg: "bg-amber-500/10",
            border: "border-amber-500/30",
            text: "text-amber-400",
            icon: "text-amber-400",
        },
        critical: {
            bg: "bg-rose-500/10",
            border: "border-rose-500/30",
            text: "text-rose-400",
            icon: "text-rose-400",
        },
    };

    const config = statusConfig[status];

    return (
        <div className={`p-4 rounded-2xl border ${config.border} ${config.bg}`}>
            <div className="flex items-center gap-3 mb-2">
                <div className={config.icon}>{icon}</div>
                <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">{label}</span>
            </div>
            <div className={`text-2xl font-black font-mono ${config.text} mb-1`}>{value}</div>
            <div className="text-[9px] text-gray-600 uppercase tracking-wider">{description}</div>
        </div>
    );
}

function StatItem({ label, value }: { label: string; value: string }) {
    return (
        <div className="text-center">
            <div className="text-xs font-black text-gray-500 uppercase tracking-widest mb-1">{label}</div>
            <div className="text-lg font-black text-white font-mono">{value}</div>
        </div>
    );
}

// Helper Functions

function getTrustLevel(score: number) {
    if (score >= 95) {
        return {
            label: "CERTIFIED TRUSTED",
            description: "All validation layers passed",
            textClass: "text-emerald-400",
            bgClass: "bg-emerald-500/10",
            borderClass: "border-emerald-500/30",
            icon: <CheckCircle size={16} className="text-emerald-400" />,
            statusIcon: <Shield size={24} className="text-emerald-400" />,
        };
    } else if (score >= 90) {
        return {
            label: "TRUSTED",
            description: "Safe to proceed with confidence",
            textClass: "text-cyan-400",
            bgClass: "bg-cyan-500/10",
            borderClass: "border-cyan-500/30",
            icon: <CheckCircle size={16} className="text-cyan-400" />,
            statusIcon: <Shield size={24} className="text-cyan-400" />,
        };
    } else if (score >= 70) {
        return {
            label: "CAUTION",
            description: "Manual verification recommended",
            textClass: "text-amber-400",
            bgClass: "bg-amber-500/10",
            borderClass: "border-amber-500/30",
            icon: <AlertTriangle size={16} className="text-amber-400" />,
            statusIcon: <AlertTriangle size={24} className="text-amber-400" />,
        };
    } else {
        return {
            label: "UNTRUSTED",
            description: "Do not rely on AI output",
            textClass: "text-rose-400",
            bgClass: "bg-rose-500/10",
            borderClass: "border-rose-500/30",
            icon: <XCircle size={16} className="text-rose-400" />,
            statusIcon: <XCircle size={24} className="text-rose-400" />,
        };
    }
}

function calculateTrustScore(truthSync: any, guardian: any): number {
    // Weighted calculation based on multiple factors
    const weights = {
        dataSupport: 0.3,
        base60: 0.25,
        feedbackLoop: 0.2,
        latency: 0.15,
        hallucination: 0.1,
    };

    let score = 0;

    // Data support (0-100)
    score += (truthSync.data_support || 0) * weights.dataSupport;

    // Base-60 checksum (0 or 100)
    score += (truthSync.base60_valid ? 100 : 0) * weights.base60;

    // Feedback loop health (0-100)
    score += (truthSync.feedback_health || 0) * weights.feedbackLoop;

    // Latency score (inverse - lower is better)
    const latencyScore = Math.max(0, 100 - (truthSync.latency_us || 0) * 10);
    score += latencyScore * weights.latency;

    // Hallucination rate (inverse - lower is better)
    const hallucinationScore = Math.max(0, 100 - (truthSync.hallucination_rate || 0) * 100);
    score += hallucinationScore * weights.hallucination;

    return Math.min(100, Math.max(0, score));
}

function getSimulatedMetrics(): TrustMetrics {
    return {
        overallScore: 92.5,
        dataSupport: 88.3,
        base60Checksum: true,
        feedbackLoopHealth: 94.7,
        latency: 1.69,
        hallucinationRate: 0.0,
        evidenceCount: 1387,
        lastUpdate: new Date().toISOString(),
    };
}
