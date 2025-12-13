export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div className="max-w-2xl text-center">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          Sentinel
        </h1>
        <p className="text-xl text-gray-300 mb-8">
          Multi-tenant SaaS Platform with Enterprise-Grade Security
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          <div className="p-4 rounded-lg bg-slate-700 border border-slate-600">
            <h3 className="text-lg font-semibold mb-2">🚀 FastAPI Backend</h3>
            <p className="text-sm text-gray-400">High-performance async API</p>
          </div>
          <div className="p-4 rounded-lg bg-slate-700 border border-slate-600">
            <h3 className="text-lg font-semibold mb-2">⚛️ Next.js Frontend</h3>
            <p className="text-sm text-gray-400">Modern React application</p>
          </div>
          <div className="p-4 rounded-lg bg-slate-700 border border-slate-600">
            <h3 className="text-lg font-semibold mb-2">🐘 PostgreSQL</h3>
            <p className="text-sm text-gray-400">Enterprise database with RLS</p>
          </div>
        </div>

        <div className="flex gap-4 justify-center">
          <a
            href="/api/v1/health"
            className="px-6 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold transition"
          >
            API Health
          </a>
          <a
            href="/api/docs"
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-semibold transition border border-slate-600"
          >
            API Docs
          </a>
          <a
            href="/dash-op"
            className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 rounded-lg font-semibold transition shadow-lg shadow-emerald-500/20"
          >
            Dash-Op (Dev)
          </a>
        </div>

        <div className="mt-12 text-sm text-gray-400">
          <p>Version: 1.0.0</p>
          <p>Status: ✓ All systems operational</p>
        </div>
      </div>
    </main>
  );
}
