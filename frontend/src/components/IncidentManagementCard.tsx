/**
 * Incident Management Dashboard Component
 * 
 * ITIL v4 compliant incident management with calm design principles:
 * - Green/Blue for "all good" states
 * - Amber for P2/P3 (attention, not alarm)
 * - Red ONLY for P1 critical
 * - Generous spacing, progressive disclosure
 * - Matches existing Sentinel dark theme
 */

"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface IncidentStats {
    total_incidents: number;
    open_incidents: number;
    critical_incidents: number;
    p1_count: number;
    p2_count: number;
    p3_count: number;
    p4_count: number;
}

interface Incident {
    id: number;
    incident_id: string;
    title: string;
    category: string;
    priority: string;
    status: string;
    assigned_team: string | null;
    detection_time: string;
}

export function IncidentManagementCard() {
    const [stats, setStats] = useState<IncidentStats | null>(null);
    const [recentIncidents, setRecentIncidents] = useState<Incident[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            // Fetch stats
            const statsRes = await fetch("/api/v1/incidents/stats");
            if (statsRes.ok) {
                const statsData = await statsRes.json();
                setStats(statsData);
            }

            // Fetch recent incidents (last 5)
            const incidentsRes = await fetch("/api/v1/incidents?page=1&page_size=5&sort_by=created_at&sort_order=desc");
            if (incidentsRes.ok) {
                const incidentsData = await incidentsRes.json();
                setRecentIncidents(incidentsData.incidents || []);
            }
        } catch (error) {
            console.error("Error fetching incident data:", error);
        } finally {
            setLoading(false);
        }
    };

    // Calm Design: Only show red for P1, otherwise calm colors
    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case "P1":
                return "bg-rose-500/10 text-rose-400 border-rose-500/20"; // Red for critical
            case "P2":
                return "bg-amber-500/10 text-amber-400 border-amber-500/20"; // Amber for high
            case "P3":
                return "bg-blue-500/10 text-blue-400 border-blue-500/20"; // Blue for medium
            case "P4":
                return "bg-slate-500/10 text-slate-400 border-slate-500/20"; // Gray for low
            default:
                return "bg-slate-500/10 text-slate-400 border-slate-500/20";
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "new":
                return "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
            case "assigned":
                return "bg-blue-500/10 text-blue-400 border-blue-500/20";
            case "in_progress":
                return "bg-purple-500/10 text-purple-400 border-purple-500/20";
            case "resolved":
                return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
            case "closed":
                return "bg-slate-500/10 text-slate-400 border-slate-500/20";
            default:
                return "bg-slate-500/10 text-slate-400 border-slate-500/20";
        }
    };

    // Calm Design: Determine overall health (only show concern if P1 exists)
    const getOverallHealth = () => {
        if (!stats) return { status: "loading", color: "text-slate-400", icon: "⏳", message: "Loading..." };

        if (stats.p1_count > 0) {
            return {
                status: "critical",
                color: "text-rose-400 bg-rose-500/10 border-rose-500/20",
                icon: "🔴",
                message: `${stats.p1_count} Critical Incident${stats.p1_count > 1 ? 's' : ''}`
            };
        }

        if (stats.p2_count > 0) {
            return {
                status: "attention",
                color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
                icon: "🟡",
                message: `${stats.p2_count} High Priority Incident${stats.p2_count > 1 ? 's' : ''}`
            };
        }

        // Calm Design: Emphasize "all good" state
        return {
            status: "healthy",
            color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
            icon: "✅",
            message: stats.open_incidents > 0
                ? `${stats.open_incidents} Open Incident${stats.open_incidents > 1 ? 's' : ''} - All Under Control`
                : "No Active Incidents"
        };
    };

    const health = getOverallHealth();

    if (loading) {
        return (
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
                <CardContent className="p-6 text-center">
                    <p className="text-gray-400">Loading incident data...</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                        <span className="text-amber-400">📋</span>
                        Incident Management
                    </CardTitle>
                    <Badge variant="outline" className={health.color}>
                        {health.icon} {health.message}
                    </Badge>
                </div>
                <CardDescription>ITIL v4 Compliant Incident Tracking</CardDescription>
            </CardHeader>
            <CardContent>
                {/* Stats Summary - Calm Design: Generous spacing */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                        <p className="text-2xl font-bold text-white">{stats?.total_incidents || 0}</p>
                        <p className="text-xs text-gray-400">Total</p>
                    </div>
                    <div className="text-center">
                        <p className="text-2xl font-bold text-cyan-400">{stats?.open_incidents || 0}</p>
                        <p className="text-xs text-gray-400">Open</p>
                    </div>
                    <div className="text-center">
                        <p className={`text-2xl font-bold ${stats?.p1_count ? 'text-rose-400' : 'text-emerald-400'}`}>
                            {stats?.p1_count || 0}
                        </p>
                        <p className="text-xs text-gray-400">Critical (P1)</p>
                    </div>
                    <div className="text-center">
                        <p className="text-2xl font-bold text-amber-400">{stats?.p2_count || 0}</p>
                        <p className="text-xs text-gray-400">High (P2)</p>
                    </div>
                </div>

                {/* Recent Incidents - Calm Design: Only show if there are incidents */}
                {recentIncidents.length > 0 ? (
                    <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-gray-300 mb-3">Recent Incidents</h4>
                        {recentIncidents.map((incident) => (
                            <div
                                key={incident.id}
                                className="rounded-lg p-3 border border-white/5 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer"
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <Badge variant="outline" className={getPriorityColor(incident.priority)}>
                                                {incident.priority}
                                            </Badge>
                                            <Badge variant="outline" className={getStatusColor(incident.status)}>
                                                {incident.status}
                                            </Badge>
                                        </div>
                                        <p className="text-sm text-gray-300 font-medium truncate">
                                            {incident.title}
                                        </p>
                                        <p className="text-xs text-gray-500 mt-1">
                                            {incident.incident_id} • {new Date(incident.detection_time).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    // Calm Design: Positive empty state
                    <div className="text-center py-8">
                        <span className="text-4xl mb-2 block">✨</span>
                        <p className="text-emerald-400 font-semibold">All Clear!</p>
                        <p className="text-sm text-gray-400 mt-1">No incidents to report</p>
                    </div>
                )}

                {/* Actions */}
                <div className="mt-6 flex gap-2">
                    <Button
                        variant="outline"
                        className="flex-1 bg-cyan-500/10 border-cyan-500/20 hover:bg-cyan-500/20 text-cyan-400"
                    >
                        View All Incidents
                    </Button>
                    <Button
                        variant="outline"
                        className="flex-1 bg-purple-500/10 border-purple-500/20 hover:bg-purple-500/20 text-purple-400"
                    >
                        Create Incident
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
