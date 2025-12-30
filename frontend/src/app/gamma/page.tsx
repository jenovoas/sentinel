import GammaDashboard from '@/components/gamma/GammaDashboard';

export const metadata = {
    title: 'Guardian Gamma | Sentinel',
    description: 'Validación humana para decisiones críticas de seguridad y HITL.',
};

export default function GammaPage() {
    return (
        <main className="p-6 lg:p-10 space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
                    Guardian Gamma <span className="text-blue-600">HITL</span>
                </h1>
                <p className="text-slate-500 dark:text-slate-400 max-w-2xl">
                    Centro de validación humana. Revisa las decisiones de seguridad marcadas por la IA con baja confianza
                    para prevenir falsos positivos y mejorar el motor de aprendizaje.
                </p>
            </div>

            <GammaDashboard />
        </main>
    );
}
