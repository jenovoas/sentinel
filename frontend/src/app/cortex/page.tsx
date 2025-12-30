import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, Shield, AlertTriangle, CheckCircle, XCircle, Clock, Zap } from 'lucide-react';
import EventTester from '@/components/cortex/EventTester';
import BattlefieldStats from '@/components/cortex/BattlefieldStats';

interface Pattern {
    name: string;
    display_name: string;
    severity: string;
    weight: number;
    enabled: boolean;
    detection_count: number;
}

interface Decision {
    id: number;
    decision_type: string;
    confidence: number;
    patterns: string[];
    created_at: string;
}

interface Stats {
    time_window_hours: number;
    total_events: number;
    total_decisions: number;
    decisions_by_type: {
        [key: string]: {
            count: number;
            avg_confidence: number;
            avg_processing_time_ms: number;
        };
    };
}

export default function CortexDashboard() {
    const [patterns, setPatterns] = useState<Pattern[]>([]);
    const [decisions, setDecisions] = useState<Decision[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            const baseUrl = '';
            const [patternsRes, decisionsRes, statsRes] = await Promise.all([
                fetch(`${baseUrl}/api/v1/cortex/patterns`),
                fetch(`${baseUrl}/api/v1/cortex/decisions?limit=10`),
                fetch(`${baseUrl}/api/v1/cortex/stats?hours=24`),
            ]);

            const patternsData = patternsRes.ok ? await patternsRes.json() : { patterns: [] };
            const decisionsData = decisionsRes.ok ? await decisionsRes.json() : { decisions: [] };
            const statsData = statsRes.ok ? await statsRes.json() : null;

            setPatterns(patternsData.patterns || []);
            setDecisions(decisionsData.decisions || []);
            setStats(statsData);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching Cortex data:', error);
            setLoading(false);
        }
    };

    const getDecisionIcon = (type: string) => {
        switch (type) {
            case 'block':
                return <XCircle className="h-5 w-5 text-red-500" />;
            case 'allow':
                return <CheckCircle className="h-5 w-5 text-green-500" />;
            case 'escalate':
                return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
            default:
                return <Activity className="h-5 w-5 text-gray-500" />;
        }
    };

    const getDecisionColor = (type: string) => {
        switch (type) {
            case 'block':
                return 'bg-red-100 text-red-800 border-red-200';
            case 'allow':
                return 'bg-green-100 text-green-800 border-green-200';
            case 'escalate':
                return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical':
                return 'bg-red-500';
            case 'high':
                return 'bg-orange-500';
            case 'medium':
                return 'bg-yellow-500';
            case 'low':
                return 'bg-blue-500';
            default:
                return 'bg-gray-500';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white p-6 selection:bg-blue-500/30">
            {/* Ambient Background Glow */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-600/10 blur-[120px] rounded-full" />
            </div>

            <div className="max-w-7xl mx-auto space-y-8 relative z-10">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-blue-400 border-blue-400/50 uppercase tracking-widest text-[10px]">
                                v3.9.0 Production Ready
                            </Badge>
                        </div>
                        <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-3">
                            <Shield className="h-10 w-10 text-blue-500 animate-pulse" />
                            Sentinel <span className="text-blue-500">Cortex™</span>
                        </h1>
                        <p className="text-slate-400 mt-2 max-w-xl">
                            Infraestructura de Inmunidad Matemática basada en eBPF LSM.
                            Protección de Ring 0 con verificación formal.
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <Button onClick={fetchData} variant="ghost" className="gap-2 bg-white/5 hover:bg-white/10 border-white/10 text-white">
                            <Activity className="h-4 w-4" />
                            Live Telemetry
                        </Button>
                        <Button className="gap-2 shadow-lg shadow-blue-500/20 bg-blue-600 hover:bg-blue-500 text-white border-none">
                            <Zap className="h-4 w-4" />
                            Battlefield Mode
                        </Button>
                    </div>
                </div>

                {/* Tactical Metrics (Pitch Component) */}
                <BattlefieldStats />

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="border-l-4 border-l-blue-500">
                        <CardHeader className="pb-2">
                            <CardDescription>Total Events (24h)</CardDescription>
                            <CardTitle className="text-3xl">{stats?.total_events || 0}</CardTitle>
                        </CardHeader>
                    </Card>

                    <Card className="border-l-4 border-l-green-500">
                        <CardHeader className="pb-2">
                            <CardDescription>Allowed</CardDescription>
                            <CardTitle className="text-3xl text-green-600">
                                {stats?.decisions_by_type?.allow?.count || 0}
                            </CardTitle>
                        </CardHeader>
                    </Card>

                    <Card className="border-l-4 border-l-red-500">
                        <CardHeader className="pb-2">
                            <CardDescription>Blocked</CardDescription>
                            <CardTitle className="text-3xl text-red-600">
                                {stats?.decisions_by_type?.block?.count || 0}
                            </CardTitle>
                        </CardHeader>
                    </Card>

                    <Card className="border-l-4 border-l-yellow-500">
                        <CardHeader className="pb-2">
                            <CardDescription>Escalated</CardDescription>
                            <CardTitle className="text-3xl text-yellow-600">
                                {stats?.decisions_by_type?.escalate?.count || 0}
                            </CardTitle>
                        </CardHeader>
                    </Card>
                </div>

                {/* Event Tester */}
                <EventTester />

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Security Patterns */}
                    <Card className="bg-slate-900/40 border-slate-800 backdrop-blur-xl shadow-2xl overflow-hidden">
                        <CardHeader className="border-b border-slate-800/50">
                            <CardTitle className="flex items-center gap-2 text-white">
                                <Shield className="h-5 w-5 text-blue-500" />
                                Security Patterns
                            </CardTitle>
                            <CardDescription className="text-slate-400">
                                {patterns.length} active threat detection patterns
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="p-0">
                            <div className="divide-y divide-slate-800/50">
                                {patterns.map((pattern) => (
                                    <div
                                        key={pattern.name}
                                        className="flex items-center justify-between p-4 bg-transparent hover:bg-white/5 transition-colors"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={`w-1.5 h-1.5 rounded-full ${getSeverityColor(pattern.severity)} shadow-[0_0_8px_rgba(59,130,246,0.5)]`} />
                                            <div>
                                                <p className="font-semibold text-slate-100">
                                                    {pattern.display_name}
                                                </p>
                                                <p className="text-xs text-slate-500 mt-1">
                                                    Weight: {(pattern.weight * 100).toFixed(0)}% | Detections: {pattern.detection_count}
                                                </p>
                                            </div>
                                        </div>
                                        <Badge variant="outline" className={`${pattern.enabled ? 'border-blue-500/50 text-blue-400' : 'border-slate-700 text-slate-500'} bg-transparent`}>
                                            {pattern.enabled ? 'Active' : 'Disabled'}
                                        </Badge>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recent Decisions */}
                    <Card className="bg-slate-900/40 border-slate-800 backdrop-blur-xl shadow-2xl overflow-hidden">
                        <CardHeader className="border-b border-slate-800/50">
                            <CardTitle className="flex items-center gap-2 text-white">
                                <Activity className="h-5 w-5 text-blue-500" />
                                Recent Decisions
                            </CardTitle>
                            <CardDescription className="text-slate-400">
                                Real-time sequence of neural truth consensus
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="p-0">
                            <div className="divide-y divide-slate-800/50">
                                {decisions.length === 0 ? (
                                    <div className="text-center py-12 text-slate-500">
                                        <Activity className="h-12 w-12 mx-auto mb-4 opacity-20" />
                                        <p>No telemetry processed yet</p>
                                        <p className="text-xs opacity-50">Sensor eBPF state: Monitoring...</p>
                                    </div>
                                ) : (
                                    decisions.map((decision) => (
                                        <div
                                            key={decision.id}
                                            className="flex items-start gap-4 p-4 bg-transparent hover:bg-white/5 transition-colors"
                                        >
                                            <div className="mt-1">{getDecisionIcon(decision.decision_type)}</div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <Badge className={`${getDecisionColor(decision.decision_type)} border-none shadow-sm`}>
                                                        {decision.decision_type.toUpperCase()}
                                                    </Badge>
                                                    <span className="text-xs font-bold text-slate-300">
                                                        {(decision.confidence * 100).toFixed(1)}% Neural Confidence
                                                    </span>
                                                </div>
                                                {decision.patterns.length > 0 && (
                                                    <div className="flex flex-wrap gap-1.5 mb-3">
                                                        {decision.patterns.map((pattern) => (
                                                            <Badge key={pattern} variant="outline" className="text-[10px] border-slate-700 text-slate-400 py-0 bg-slate-800/50">
                                                                {pattern}
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                )}
                                                <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
                                                    <Clock className="h-3 w-3" />
                                                    {new Date(decision.created_at).toISOString()}
                                                </div>
                                            </div>
                                            <div className="text-[10px] font-mono text-slate-700">
                                                #{decision.id}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Performance Stats */}
                {stats && Object.keys(stats.decisions_by_type).length > 0 && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Performance Metrics</CardTitle>
                            <CardDescription>Average processing times and confidence scores</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {Object.entries(stats.decisions_by_type).map(([type, data]) => (
                                    <div key={type} className="p-4 rounded-lg border bg-white dark:bg-slate-800">
                                        <div className="flex items-center gap-2 mb-2">
                                            {getDecisionIcon(type)}
                                            <h3 className="font-semibold capitalize">{type}</h3>
                                        </div>
                                        <div className="space-y-1 text-sm">
                                            <p className="text-slate-600 dark:text-slate-400">
                                                Count: <span className="font-medium text-slate-900 dark:text-white">{data.count}</span>
                                            </p>
                                            <p className="text-slate-600 dark:text-slate-400">
                                                Avg Confidence:{' '}
                                                <span className="font-medium text-slate-900 dark:text-white">
                                                    {(data.avg_confidence * 100).toFixed(1)}%
                                                </span>
                                            </p>
                                            <p className="text-slate-600 dark:text-slate-400">
                                                Avg Time:{' '}
                                                <span className="font-medium text-slate-900 dark:text-white">
                                                    {data.avg_processing_time_ms.toFixed(0)}ms
                                                </span>
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
