'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { CheckCircle, XCircle, Clock, Shield, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface DecisionReviewCardProps {
    decision: {
        id: number;
        guardian: string;
        type: string;
        context: any;
        evidence: any;
        confidence: number;
        created_at: string;
        timeout_at: string;
    };
    onAction: () => void;
}

export default function DecisionReviewCard({ decision, onAction }: DecisionReviewCardProps) {
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState('');
    const [showRaw, setShowRaw] = useState(false);

    const handleAction = async (action: 'approve' | 'deny') => {
        setLoading(true);
        try {
            const baseUrl = typeof window !== 'undefined' ? '' : 'http://sentinel-vault-backend:8000';
            const response = await fetch(`${baseUrl}/api/v1/gamma/${action}/${decision.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ feedback }),
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            toast.success(`Decisión ${action === 'approve' ? 'aprobada' : 'denegada'} con éxito`);
            onAction();
        } catch (error) {
            console.error(`Error al ${action} decisión:`, error);
            toast.error(`Error al procesar la acción: ${error}`);
        } finally {
            setLoading(false);
        }
    };

    const getTimeLeft = (timeoutAt: string) => {
        const timeout = new Date(timeoutAt);
        const now = new Date();
        const diff = timeout.getTime() - now.getTime();

        if (diff <= 0) return 'Expirado';

        const minutes = Math.floor(diff / 1000 / 60);
        return `${minutes} min`;
    };

    return (
        <Card className="border-l-4 border-yellow-500 bg-white dark:bg-slate-900 overflow-hidden">
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            <Shield className="h-5 w-5 text-blue-600" />
                            <CardTitle className="text-lg">#{decision.id} - {decision.type.replace('_', ' ').toUpperCase()}</CardTitle>
                        </div>
                        <CardDescription className="flex items-center gap-2">
                            <Badge variant="outline">{decision.guardian.toUpperCase()}</Badge>
                            <span className="text-xs text-slate-500">Recibido: {new Date(decision.created_at).toLocaleTimeString()}</span>
                        </CardDescription>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                        <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 border-yellow-200 flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {getTimeLeft(decision.timeout_at)}
                        </Badge>
                        <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                            Confianza: {(decision.confidence * 100).toFixed(1)}%
                        </span>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-md border text-sm overflow-auto max-h-40">
                    <div className="flex justify-between items-center mb-2">
                        <span className="font-semibold text-xs text-slate-500 uppercase">Contexto del Evento</span>
                        <Button variant="ghost" size="sm" onClick={() => setShowRaw(!showRaw)} className="h-6 px-2 text-xs">
                            {showRaw ? <ChevronUp className="h-3 w-3 mr-1" /> : <ChevronDown className="h-3 w-3 mr-1" />}
                            {showRaw ? 'Simplificar' : 'Ver JSON'}
                        </Button>
                    </div>
                    {showRaw ? (
                        <pre className="text-xs font-mono">{JSON.stringify(decision.context, null, 2)}</pre>
                    ) : (
                        <div className="grid grid-cols-2 gap-2 text-xs">
                            {Object.entries(decision.context).slice(0, 6).map(([key, val]) => (
                                <div key={key} className="flex gap-2">
                                    <span className="text-slate-500 font-medium">{key}:</span>
                                    <span className="text-slate-900 dark:text-slate-200 truncate">{String(val)}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {decision.evidence && (
                    <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md border border-blue-100 dark:border-blue-800">
                        <AlertTriangle className="h-4 w-4 text-blue-600 mt-0.5" />
                        <div className="text-xs text-blue-800 dark:text-blue-300">
                            <span className="font-semibold block mb-1">Evidencia Detectada:</span>
                            {typeof decision.evidence === 'string' ? decision.evidence : JSON.stringify(decision.evidence)}
                        </div>
                    </div>
                )}

                <Textarea
                    placeholder="Notas o feedback para el motor de IA (opcional)..."
                    className="text-sm h-20"
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                />
            </CardContent>

            <CardFooter className="bg-slate-50 dark:bg-slate-800/50 border-t p-4 flex gap-3">
                <Button
                    variant="outline"
                    className="flex-1 border-red-200 text-red-700 hover:bg-red-50"
                    onClick={() => handleAction('deny')}
                    disabled={loading}
                >
                    <XCircle className="mr-2 h-4 w-4" />
                    Denegar
                </Button>
                <Button
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    onClick={() => handleAction('approve')}
                    disabled={loading}
                >
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Aprobar
                </Button>
            </CardFooter>
        </Card>
    );
}
