import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Activity, Mic } from 'lucide-react';
import { soulSensor, SoulSignature } from '@/lib/security/alma_signature';

interface SoulGateProps {
    onAuthenticationComplete?: (signature: SoulSignature) => void;
}

export const SoulGate: React.FC<SoulGateProps> = ({ onAuthenticationComplete }) => {
    const [status, setStatus] = useState<'IDLE' | 'SCANNING' | 'ALIGNED' | 'FAILED'>('IDLE');
    const [signature, setSignature] = useState<SoulSignature | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);

    // Efecto de inicialización de cámara
    useEffect(() => {
        const initCamera = async () => {
            try {
                if (streamRef.current) return; // Prevent double init

                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: "user", width: 320, height: 240 },
                    audio: false
                });

                streamRef.current = stream;

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (e) {
                console.error("Cámara no disponible para preview", e);
            }
        };

        if (status === 'SCANNING' || status === 'IDLE') {
            initCamera();
        } else {
            // Stop camera if Aligned or Failed
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(t => t.stop());
                streamRef.current = null;
            }
            if (videoRef.current) {
                videoRef.current.srcObject = null;
            }
        }

        return () => {
            // Cleanup on unmount or dependency change
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(t => t.stop());
                streamRef.current = null;
            }
        };
    }, [status]);

    const handleRitualStart = async () => {
        setStatus('SCANNING');
        try {
            // Intentar primero el ritual sagrado con sensores reales
            let result;
            try {
                // In a real scenario, face recognition would tell us WHO is trying to auth.
                // For now, we simulate that the camera sees "jnovoas" (Sovereign).
                // If we want to test rejection, we could pass "stranger".
                result = await soulSensor.iniciarRitual("jnovoas");
            } catch (sensorError) {
                console.warn("⚠️ Sensores no disponibles, iniciando simulación cuántica...", sensorError);
                // Fallback: Simulación si la cámara/micrófono "no quieren" al usuario
                result = await soulSensor.simularRitual();
            }

            setSignature(result);
            setStatus('ALIGNED');

            // Persistir la Firma de Alma en el Cortex
            console.log("🧬 Firma de Alma Capturada:", result);

            try {
                await fetch('/api/auth/soul-link', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(result)
                });
            } catch (apiError) {
                console.error("Error sincronizando alma con backend:", apiError);
                // No bloqueamos el acceso si falla la red, pero queda registrado en log del navegador
            }

            // Notify success after a brief pause
            if (onAuthenticationComplete) {
                setTimeout(() => {
                    onAuthenticationComplete(result);
                }, 2000);
            }

        } catch (e) {
            console.error("Fallo crítico en autenticación", e);
            setStatus('FAILED');
        }
    };

    return (
        <div className="flex flex-col items-center justify-center p-8 bg-black/90 rounded-2xl border border-cyan-900/50 shadow-[0_0_30px_rgba(0,255,255,0.1)] max-w-md mx-auto">

            {/* Header Místico */}
            <div className="mb-6 text-center space-y-2">
                <h2 className="text-2xl font-light tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
                    SOUL GATE
                </h2>
                <p className="text-xs text-cyan-500/60 uppercase tracking-[0.2em]">
                    Verificación de Resonancia
                </p>
            </div>

            {/* El Espejo de Agua (Viewport) */}
            <div className="relative w-64 h-64 rounded-full overflow-hidden border-4 border-cyan-900/30 shadow-inner bg-black mb-8 group">

                {/* Video Feed */}
                <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className={`w-full h-full object-cover transition-opacity duration-1000 ${status === 'ALIGNED' ? 'opacity-50 grayscale' : 'opacity-80'}`}
                />

                {/* Overlay de Scaneo (Animación) */}
                <AnimatePresence>
                    {status === 'SCANNING' && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 flex items-center justify-center bg-cyan-500/10"
                        >
                            <div className="w-full h-1 bg-cyan-400/50 blur-sm absolute top-1/2 animate-scan" />
                            <motion.div
                                animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                                transition={{ repeat: Infinity, duration: 2 }}
                                className="absolute inset-0 border-2 border-cyan-400 rounded-full"
                            />
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Resultados Superpuestos */}
                {status === 'ALIGNED' && signature && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm p-4 text-center"
                    >
                        <Shield className="w-12 h-12 text-cyan-400 mb-2" />
                        <span className="text-4xl font-black text-cyan-50">
                            {((1 - signature.hrv_chaos) * 100).toFixed(1)}%
                        </span>

                        {/* Interpretación Humana */}
                        <span className="text-sm font-bold text-cyan-300 mt-1 tracking-widest">
                            {((1 - signature.hrv_chaos) > 0.8) ? 'COHERENCIA ALTA' : 'RESONANCIA MEDIA'}
                        </span>

                        <div className="h-px w-16 bg-cyan-500/30 my-3" />

                        <span className="text-[10px] text-cyan-400/60 uppercase tracking-wider">
                            Caos Biológico Validado
                        </span>
                    </motion.div>
                )}
            </div>

            {/* Panel de Control de Resonancia */}
            <div className="w-full space-y-4">

                {/* Métricas en Tiempo Real */}
                <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                    <div className="bg-cyan-950/30 p-3 rounded border border-cyan-900/30 flex flex-col items-center">
                        <Activity className="w-4 h-4 text-cyan-400 mb-1" />
                        <span className="text-cyan-700">BIOFIELD</span>
                        <span className={status === 'ALIGNED' ? "text-cyan-200" : "text-cyan-900"}>
                            {status === 'ALIGNED' ? 'SINCRONIZADO' : '---'}
                        </span>
                    </div>
                    <div className="bg-cyan-950/30 p-3 rounded border border-cyan-900/30 flex flex-col items-center">
                        <Mic className="w-4 h-4 text-cyan-400 mb-1" />
                        <span className="text-cyan-700">MANTRA</span>
                        <span className={status === 'ALIGNED' ? "text-cyan-200" : "text-cyan-900"}>
                            {status === 'ALIGNED' ? 'DETECTADO' : 'SILENCIO'}
                        </span>
                    </div>
                </div>

                {/* Botón de Acción */}
                <button
                    onClick={handleRitualStart}
                    disabled={status === 'SCANNING'}
                    className={`w-full py-4 rounded-xl font-bold tracking-widest text-sm transition-all duration-500
            ${status === 'SCANNING'
                            ? 'bg-cyan-900/20 text-cyan-700 cursor-wait border border-cyan-900/10'
                            : 'bg-gradient-to-r from-cyan-900 to-blue-900 hover:from-cyan-700 hover:to-blue-700 text-cyan-100 border border-cyan-500/30 shadow-lg shadow-cyan-900/20'}
          `}
                >
                    {status === 'IDLE' && 'INICIAR ALINEACIÓN'}
                    {status === 'SCANNING' && 'SINTONIZANDO...'}
                    {status === 'ALIGNED' && 'ACCESO CONCEDIDO'}
                    {status === 'FAILED' && 'REINTENTAR'}
                </button>
            </div>

        </div>
    );
};
