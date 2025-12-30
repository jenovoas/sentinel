'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, Shield, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react';
import EventTester from '@/components/cortex/EventTester';

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
            const [patternsRes, decisionsRes, statsRes] = await Promise.all([
                fetch('http://localhost:8000/api/v1/cortex/patterns'),
                fetch('http://localhost:8000/api/v1/cortex/decisions?limit=10'),
                fetch('http://localhost:8000/api/v1/cortex/stats?hours=24'),
            ]);

            const patternsData = await patternsRes.json();
            const decisionsData = await decisionsRes.json();
            const statsData = await statsRes.json();

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
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6">
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-4xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                            <Shield className="h-10 w-10 text-blue-600" />
                            Cortex Decision Engine
                        </h1>
                        <p className="text-slate-600 dark:text-slate-400 mt-2">
                            AI-powered security threat analysis and decision making
                        </p>
                    </div>
                    <Button onClick={fetchData} variant="outline" className="gap-2">
                        <Activity className="h-4 w-4" />
                        Refresh
                    </Button>
                </div>

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
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Security Patterns */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Shield className="h-5 w-5 text-blue-600" />
                                Security Patterns
                            </CardTitle>
                            <CardDescription>
                                {patterns.length} active threat detection patterns
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {patterns.map((pattern) => (
                                    <div
                                        key={pattern.name}
                                        className="flex items-center justify-between p-3 rounded-lg border bg-white dark:bg-slate-800 hover:shadow-md transition-shadow"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`w-2 h-2 rounded-full ${getSeverityColor(pattern.severity)}`} />
                                            <div>
                                                <p className="font-medium text-slate-900 dark:text-white">
                                                    {pattern.display_name}
                                                </p>
                                                <p className="text-sm text-slate-500">
                                                    Weight: {(pattern.weight * 100).toFixed(0)}% | Detections: {pattern.detection_count}
                                                </p>
                                            </div>
                                        </div>
                                        <Badge variant={pattern.enabled ? 'default' : 'secondary'}>
                                            {pattern.enabled ? 'Active' : 'Disabled'}
                                        </Badge>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recent Decisions */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Activity className="h-5 w-5 text-blue-600" />
                                Recent Decisions
                            </CardTitle>
                            <CardDescription>
                                Last {decisions.length} security decisions
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {decisions.length === 0 ? (
                                    <div className="text-center py-8 text-slate-500">
                                        <Activity className="h-12 w-12 mx-auto mb-3 opacity-50" />
                                        <p>No decisions yet</p>
                                        <p className="text-sm">Submit events to see decisions here</p>
                                    </div>
                                ) : (
                                    decisions.map((decision) => (
                                        <div
                                            key={decision.id}
                                            className="flex items-start gap-3 p-3 rounded-lg border bg-white dark:bg-slate-800 hover:shadow-md transition-shadow"
                                        >
                                            <div className="mt-1">{getDecisionIcon(decision.decision_type)}</div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <Badge className={getDecisionColor(decision.decision_type)}>
                                                        {decision.decision_type.toUpperCase()}
                                                    </Badge>
                                                    <span className="text-sm font-medium text-slate-900 dark:text-white">
                                                        {(decision.confidence * 100).toFixed(1)}% confidence
                                                    </span>
                                                </div>
                                                {decision.patterns.length > 0 && (
                                                    <div className="flex flex-wrap gap-1 mb-2">
                                                        {decision.patterns.map((pattern) => (
                                                            <Badge key={pattern} variant="outline" className="text-xs">
                                                                {pattern}
                                                            </Badge>
                                                        ))}
                                                    </div>
                                                )}
                                                <div className="flex items-center gap-2 text-xs text-slate-500">
                                                    <Clock className="h-3 w-3" />
                                                    {new Date(decision.created_at).toLocaleString()}
                                                </div>
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
