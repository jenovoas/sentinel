'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, ShieldAlert, CheckCircle2, History, AlertCircle, Loader2 } from 'lucide-react';
import DecisionReviewCard from './DecisionReviewCard';
import { toast } from 'react-hot-toast';

interface PendingDecision {
    id: number;
    guardian: string;
    type: string;
    context: any;
    evidence: any;
    confidence: float;
    created_at: string;
    timeout_at: string;
}

export default function GammaDashboard() {
    const [decisions, setDecisions] = useState<PendingDecision[]>([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        pending: 0,
        approvedToday: 0,
        deniedToday: 0
    });

    const fetchDecisions = useCallback(async () => {
        setLoading(true);
        try {
            const baseUrl = typeof window !== 'undefined' ? '' : 'http://sentinel-vault-backend:8000';
            const response = await fetch(`${baseUrl}/api/v1/gamma/pending?limit=20`);

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            setDecisions(data);
            setStats(prev => ({ ...prev, pending: data.length }));
        } catch (error) {
            console.error('Error fetching decisions:', error);
            toast.error('No se pudieron cargar las decisiones pendientes');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDecisions();

        // Polling cada 30 segundos
        const interval = setInterval(fetchDecisions, 30000);
        return () => clearInterval(interval);
    }, [fetchDecisions]);

    const handleActionComplete = () => {
        // Recargar datos tras una acción del usuario
        fetchDecisions();
        // Simular incremento de estadísticas (en un entorno real esto vendría del API de stats)
        // setStats(prev => ...);
    };

    return (
        <div className="space-y-6">
            {/* Header con estadísticas rápidas */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border-yellow-200">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-yellow-800 dark:text-yellow-600 font-medium">Pendientes HITL</CardDescription>
                        <CardTitle className="text-3xl font-bold flex items-center justify-between">
                            {stats.pending}
                            <ShieldAlert className="h-6 w-6 text-yellow-600" />
                        </CardTitle>
                    </CardHeader>
                </Card>
                <Card className="bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-200">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-green-800 dark:text-green-600 font-medium">Aprobadas Hoy</CardDescription>
                        <CardTitle className="text-3xl font-bold flex items-center justify-between">
                            {stats.approvedToday}
                            <CheckCircle2 className="h-6 w-6 text-green-600" />
                        </CardTitle>
                    </CardHeader>
                </Card>
                <Card className="bg-gradient-to-br from-slate-500/10 to-slate-600/5 border-slate-200">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-slate-800 dark:text-slate-600 font-medium">Tasa de Resolución</CardDescription>
                        <CardTitle className="text-3xl font-bold flex items-center justify-between">
                            94%
                            <History className="h-6 w-6 text-slate-600" />
                        </CardTitle>
                    </CardHeader>
                </Card>
            </div>

            {/* Lista Principal */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <AlertCircle className="h-5 w-5 text-orange-500" />
                        Revisiones Críticas Requeridas
                    </h2>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={fetchDecisions}
                        disabled={loading}
                        className="bg-white dark:bg-slate-800"
                    >
                        {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                        Actualizar
                    </Button>
                </div>

                {loading && decisions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 space-y-4">
                        <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
                        <p className="text-slate-500">Cargando cola de decisiones...</p>
                    </div>
                ) : decisions.length === 0 ? (
                    <Card className="border-dashed border-2 py-20">
                        <CardContent className="flex flex-col items-center justify-center text-center space-y-3">
                            <div className="h-12 w-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                                <CheckCircle2 className="h-6 w-6 text-green-600" />
                            </div>
                            <div className="space-y-1">
                                <h3 className="font-semibold text-lg">¡Todo despejado!</h3>
                                <p className="text-slate-500 text-sm max-w-xs">
                                    No hay decisiones pendientes de validación humana en este momento.
                                </p>
                            </div>
                            <Button variant="link" onClick={fetchDecisions}>Verificar de nuevo</Button>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        {decisions.map((decision) => (
                            <DecisionReviewCard
                                key={decision.id}
                                decision={decision}
                                onAction={handleActionComplete}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
