'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, Clock, Shield, AlertTriangle } from 'lucide-react';

// API URL - hardcoded for Docker network
// Frontend and backend are in same Docker network, use service name
const API_URL = 'http://backend:8000';

interface Decision {
    id: number;
    guardian: string;
    type: string;
    context: Record<string, any>;
    evidence: Record<string, any>;
    confidence: number;
    created_at: string;
    timeout_at: string;
}

export default function GuardianGammaPage() {
    const [decisions, setDecisions] = useState<Decision[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [feedback, setFeedback] = useState<Record<number, string>>({});
    const [processing, setProcessing] = useState<Record<number, boolean>>({});

    // Fetch pending decisions
    const fetchDecisions = async () => {
        try {
            const response = await fetch(`${API_URL}/api/v1/gamma/pending`);
            if (!response.ok) throw new Error('Failed to fetch decisions');
            const data = await response.json();
            setDecisions(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    // Approve decision
    const handleApprove = async (id: number) => {
        setProcessing({ ...processing, [id]: true });
        try {
            const response = await fetch(`${API_URL}/api/v1/gamma/approve/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback: feedback[id] || '' }),
            });

            if (!response.ok) throw new Error('Failed to approve decision');

            // Remove from list
            setDecisions(decisions.filter(d => d.id !== id));
            setFeedback({ ...feedback, [id]: '' });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to approve');
        } finally {
            setProcessing({ ...processing, [id]: false });
        }
    };

    // Deny decision
    const handleDeny = async (id: number) => {
        setProcessing({ ...processing, [id]: true });
        try {
            const response = await fetch(`${API_URL}/api/v1/gamma/deny/${id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback: feedback[id] || '' }),
            });

            if (!response.ok) throw new Error('Failed to deny decision');

            // Remove from list
            setDecisions(decisions.filter(d => d.id !== id));
            setFeedback({ ...feedback, [id]: '' });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to deny');
        } finally {
            setProcessing({ ...processing, [id]: false });
        }
    };

    // Auto-refresh every 5 seconds
    useEffect(() => {
        fetchDecisions();
        const interval = setInterval(fetchDecisions, 5000);
        return () => clearInterval(interval);
    }, []);

    // Format timestamp
    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

        if (diff < 60) return `${diff}s ago`;
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        return `${Math.floor(diff / 3600)}h ago`;
    };

    // Get confidence color
    const getConfidenceColor = (confidence: number) => {
        if (confidence < 0.5) return 'text-red-500';
        if (confidence < 0.7) return 'text-yellow-500';
        return 'text-green-500';
    };

    // Get guardian icon
    const getGuardianIcon = (guardian: string) => {
        if (guardian === 'alpha') return <Shield className="w-5 h-5 text-blue-500" />;
        if (guardian === 'beta') return <AlertTriangle className="w-5 h-5 text-orange-500" />;
        return <Shield className="w-5 h-5" />;
    };

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Guardian Gamma</h1>
                <p className="text-gray-600">Human-in-the-Loop Decision Queue</p>
            </div>

            {error && (
                <Alert variant="destructive" className="mb-6">
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Badge variant="outline" className="text-lg px-4 py-2">
                        {decisions.length} Pending
                    </Badge>
                    <Button onClick={fetchDecisions} variant="outline" size="sm">
                        Refresh
                    </Button>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <Clock className="w-12 h-12 animate-spin mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-600">Loading decisions...</p>
                </div>
            ) : decisions.length === 0 ? (
                <Card>
                    <CardContent className="py-12 text-center">
                        <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
                        <h3 className="text-xl font-semibold mb-2">All Clear</h3>
                        <p className="text-gray-600">No pending decisions require your attention.</p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-4">
                    {decisions.map((decision) => (
                        <Card key={decision.id} className="border-l-4 border-l-blue-500">
                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        {getGuardianIcon(decision.guardian)}
                                        <div>
                                            <CardTitle className="text-lg">
                                                Guardian {decision.guardian.charAt(0).toUpperCase() + decision.guardian.slice(1)}
                                            </CardTitle>
                                            <CardDescription>
                                                {decision.type.replace(/_/g, ' ')}
                                            </CardDescription>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-2xl font-bold ${getConfidenceColor(decision.confidence)}`}>
                                            {Math.round(decision.confidence * 100)}%
                                        </div>
                                        <div className="text-sm text-gray-500">confidence</div>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {/* Context */}
                                <div>
                                    <h4 className="font-semibold mb-2">Context</h4>
                                    <div className="bg-gray-50 p-3 rounded-md">
                                        <pre className="text-sm overflow-x-auto">
                                            {JSON.stringify(decision.context, null, 2)}
                                        </pre>
                                    </div>
                                </div>

                                {/* Evidence */}
                                {Object.keys(decision.evidence).length > 0 && (
                                    <div>
                                        <h4 className="font-semibold mb-2">Evidence</h4>
                                        <div className="bg-gray-50 p-3 rounded-md">
                                            <pre className="text-sm overflow-x-auto">
                                                {JSON.stringify(decision.evidence, null, 2)}
                                            </pre>
                                        </div>
                                    </div>
                                )}

                                {/* Metadata */}
                                <div className="flex items-center gap-4 text-sm text-gray-600">
                                    <span className="flex items-center gap-1">
                                        <Clock className="w-4 h-4" />
                                        Created {formatTime(decision.created_at)}
                                    </span>
                                    <span>•</span>
                                    <span>ID: {decision.id}</span>
                                </div>

                                {/* Feedback */}
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Feedback (optional)
                                    </label>
                                    <Textarea
                                        placeholder="Explain your decision to help the system learn..."
                                        value={feedback[decision.id] || ''}
                                        onChange={(e) => setFeedback({ ...feedback, [decision.id]: e.target.value })}
                                        className="min-h-[80px]"
                                    />
                                </div>

                                {/* Actions */}
                                <div className="flex gap-3 pt-2">
                                    <Button
                                        onClick={() => handleApprove(decision.id)}
                                        disabled={processing[decision.id]}
                                        className="flex-1 bg-green-600 hover:bg-green-700"
                                    >
                                        <CheckCircle className="w-4 h-4 mr-2" />
                                        Approve
                                    </Button>
                                    <Button
                                        onClick={() => handleDeny(decision.id)}
                                        disabled={processing[decision.id]}
                                        variant="destructive"
                                        className="flex-1"
                                    >
                                        <XCircle className="w-4 h-4 mr-2" />
                                        Deny
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
