'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Send, Loader2, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface TestEvent {
    name: string;
    description: string;
    event: {
        event_type: string;
        source: string;
        data: any;
    };
    expectedPattern?: string;
}

const TEST_EVENTS: TestEvent[] = [
    {
        name: 'Malicious Binary',
        description: 'Execution from /tmp/ directory',
        event: {
            event_type: 'syscall',
            source: 'guardian_alpha',
            data: {
                syscall: 'execve',
                process_path: '/tmp/suspicious_binary',
                user: 'attacker',
                uid: 1000,
                pid: 12345,
            },
        },
        expectedPattern: 'malicious_binary',
    },
    {
        name: 'Privilege Escalation',
        description: 'Attempting to become root',
        event: {
            event_type: 'syscall',
            source: 'guardian_alpha',
            data: {
                syscall: 'setuid',
                target_uid: 0,
                uid: 1000,
                user: 'attacker',
                pid: 54321,
            },
        },
        expectedPattern: 'privilege_escalation',
    },
    {
        name: 'Suspicious Network',
        description: 'Connection to backdoor port',
        event: {
            event_type: 'network',
            source: 'guardian_beta',
            data: {
                dest_port: 4444,
                dest_ip: '192.168.1.100',
                protocol: 'tcp',
                user: 'attacker',
            },
        },
        expectedPattern: 'suspicious_network',
    },
    {
        name: 'Data Exfiltration',
        description: 'Large data transfer to external IP',
        event: {
            event_type: 'network',
            source: 'guardian_beta',
            data: {
                bytes_sent: 50000000, // 50MB
                dest_ip: '8.8.8.8',
                is_external: true,
                user: 'attacker',
            },
        },
        expectedPattern: 'data_exfiltration',
    },
];

interface DecisionResponse {
    decision_id: number;
    decision_type: string;
    confidence: number;
    patterns_detected: string[];
    reasoning: string;
    processing_time_ms: number;
}

export default function EventTester() {
    const [loading, setLoading] = useState<string | null>(null);
    const [results, setResults] = useState<Map<string, DecisionResponse>>(new Map());

    const submitEvent = async (testEvent: TestEvent) => {
        setLoading(testEvent.name);
        try {
            const response = await fetch('http://localhost:8000/api/v1/cortex/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(testEvent.event),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data: DecisionResponse = await response.json();

            setResults(new Map(results.set(testEvent.name, data)));

            toast.success(
                `Decision: ${data.decision_type.toUpperCase()} (${(data.confidence * 100).toFixed(1)}%)`,
                { duration: 4000 }
            );
        } catch (error) {
            console.error('Error submitting event:', error);
            toast.error(`Failed to submit event: ${error}`);
        } finally {
            setLoading(null);
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
                return null;
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

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Send className="h-5 w-5 text-blue-600" />
                        Event Tester
                    </CardTitle>
                    <CardDescription>
                        Submit test events to the Cortex Decision Engine
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {TEST_EVENTS.map((testEvent) => {
                            const result = results.get(testEvent.name);
                            const isLoading = loading === testEvent.name;

                            return (
                                <div
                                    key={testEvent.name}
                                    className="p-4 rounded-lg border bg-white dark:bg-slate-800 space-y-3"
                                >
                                    <div>
                                        <h3 className="font-semibold text-slate-900 dark:text-white">
                                            {testEvent.name}
                                        </h3>
                                        <p className="text-sm text-slate-600 dark:text-slate-400">
                                            {testEvent.description}
                                        </p>
                                        {testEvent.expectedPattern && (
                                            <Badge variant="outline" className="mt-2 text-xs">
                                                Expected: {testEvent.expectedPattern}
                                            </Badge>
                                        )}
                                    </div>

                                    <Button
                                        onClick={() => submitEvent(testEvent)}
                                        disabled={isLoading}
                                        className="w-full"
                                        size="sm"
                                    >
                                        {isLoading ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Processing...
                                            </>
                                        ) : (
                                            <>
                                                <Send className="mr-2 h-4 w-4" />
                                                Submit Event
                                            </>
                                        )}
                                    </Button>

                                    {result && (
                                        <div className="pt-3 border-t space-y-2">
                                            <div className="flex items-center gap-2">
                                                {getDecisionIcon(result.decision_type)}
                                                <Badge className={getDecisionColor(result.decision_type)}>
                                                    {result.decision_type.toUpperCase()}
                                                </Badge>
                                                <span className="text-sm font-medium">
                                                    {(result.confidence * 100).toFixed(1)}%
                                                </span>
                                            </div>

                                            {result.patterns_detected.length > 0 && (
                                                <div className="flex flex-wrap gap-1">
                                                    {result.patterns_detected.map((pattern) => (
                                                        <Badge key={pattern} variant="secondary" className="text-xs">
                                                            {pattern}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            )}

                                            <p className="text-xs text-slate-600 dark:text-slate-400">
                                                Processing time: {result.processing_time_ms.toFixed(0)}ms
                                            </p>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
