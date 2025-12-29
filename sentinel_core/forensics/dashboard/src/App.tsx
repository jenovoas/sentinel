import React, { useEffect, useState, useRef } from 'react';
import { Activity, Shield, Terminal, AlertTriangle, Lock, Unlock, Cpu, Server } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface DashboardEvent {
  type: 'process_start' | 'detections' | 'decision';
  data: {
    pid: number;
    comm: string;
    findings?: string[];
    decision?: string;
    blocked?: boolean;
  };
}

interface LogEntry {
  id: string;
  timestamp: string;
  type: 'info' | 'alert' | 'success' | 'block';
  message: string;
}

function App() {
  const [events, setEvents] = useState<DashboardEvent[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [threatLevel, setThreatLevel] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws');

    ws.onopen = () => {
      setIsConnected(true);
      addLog('success', '🔌 Conectado al Sentinel Core WebSocket');
    };

    ws.onclose = () => {
      setIsConnected(false);
      addLog('alert', '🔌 Desconectado del servidor. Reintentando...');
    };

    ws.onmessage = (event) => {
      try {
        const data: DashboardEvent = JSON.parse(event.data);
        setEvents((prev) => [data, ...prev].slice(0, 50)); // Keep last 50 events

        switch (data.type) {
          case 'process_start':
            addLog('info', `📦 Proceso iniciado: ${data.data.comm} (PID: ${data.data.pid})`);
            break;
          case 'detections':
            setThreatLevel((prev) => Math.min(prev + 20, 100));
            addLog('alert', `⚠️ AMENAZA DETECTADA en PID ${data.data.pid} (${data.data.comm})`);
            break;
          case 'decision':
            if (data.data.blocked) {
              setThreatLevel(0); // Threat neutralized
              addLog('block', `🛑 BLOQUEADO: ${data.data.comm} (PID: ${data.data.pid}) por orden de IA`);
            } else {
              setThreatLevel((prev) => Math.max(prev - 10, 0));
              addLog('success', `✅ PERMITIDO: ${data.data.comm} (PID: ${data.data.pid})`);
            }
            break;
        }
      } catch (e) {
        console.error('Error parsing WS message:', e);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const addLog = (type: LogEntry['type'], message: string) => {
    setLogs((prev) => [
      ...prev,
      {
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date().toLocaleTimeString(),
        type,
        message,
      },
    ].slice(-100)); // Keep last 100 logs
  };

  // Chart Data Configuration
  const chartData = {
    labels: Array.from({ length: 20 }, (_, i) => i),
    datasets: [
      {
        label: 'Nivel de Amenaza',
        data: Array.from({ length: 20 }, () => Math.random() * 10 + (threatLevel > 0 ? threatLevel : 0)),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        grid: { color: '#333' },
      },
      x: { display: false },
    },
    animation: { duration: 0 },
  };

  return (
    <div className="min-h-screen bg-background text-white p-6 font-mono overflow-hidden relative">
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>

      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
        <div className="flex items-center gap-3">
          <Shield className="w-10 h-10 text-primary animate-pulse" />
          <div>
            <h1 className="text-2xl font-bold tracking-wider">SENTINEL <span className="text-primary">CORTEX</span></h1>
            <p className="text-xs text-gray-400">COGNITIVE KERNEL PROTECTION SYSTEM // v1.2.0</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${isConnected ? 'bg-green-900/30 text-green-400 border border-green-900' : 'bg-red-900/30 text-red-400 border border-red-900'}`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-ping' : 'bg-red-500'}`}></div>
          {isConnected ? 'SISTEMA ONLINE' : 'DESCONECTADO'}
        </div>
      </header>

      <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">

        {/* Left Column: Stats & Radar */}
        <div className="col-span-3 flex flex-col gap-6">
          {/* Threat Level */}
          <div className="bg-surface border border-gray-800 rounded-xl p-6 relative overflow-hidden group">
            <div className={`absolute inset-0 opacity-10 transition-colors duration-500 ${threatLevel > 50 ? 'bg-red-600' : 'bg-blue-600'}`}></div>
            <h2 className="text-gray-400 text-xs uppercase tracking-widest mb-2 flex items-center gap-2">
              <Activity className="w-4 h-4" /> Nivel de Amenaza Global
            </h2>
            <div className="text-5xl font-bold mb-2 transition-colors duration-300" style={{ color: threatLevel > 50 ? '#ef4444' : '#3b82f6' }}>
              {threatLevel}%
            </div>
            <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
              <div
                className="h-full transition-all duration-300 ease-out"
                style={{ width: `${threatLevel}%`, backgroundColor: threatLevel > 50 ? '#ef4444' : '#3b82f6' }}
              ></div>
            </div>
          </div>

          {/* Active Services */}
          <div className="bg-surface border border-gray-800 rounded-xl p-6 flex-1">
            <h2 className="text-gray-400 text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
              <Server className="w-4 h-4" /> Servicios Activos
            </h2>
            <div className="space-y-4">
              <ServiceStatus name="Guardian-Alpha LSM" status="active" />
              <ServiceStatus name="Memory Forensics" status="active" />
              <ServiceStatus name="Cognitive Loop (Ollama)" status="active" />
              <ServiceStatus name="Event Stream" status={isConnected ? 'active' : 'inactive'} />
            </div>
          </div>
        </div>

        {/* Center Column: Live Chart & Console */}
        <div className="col-span-6 flex flex-col gap-6">
          {/* Live Chart */}
          <div className="bg-surface border border-gray-800 rounded-xl p-4 h-64 relative">
            <div className="absolute top-2 right-2 text-xs text-gray-500">LIVE TELEMETRY</div>
            <Line data={chartData} options={chartOptions as any} />
          </div>

          {/* Console Output */}
          <div className="bg-black border border-gray-800 rounded-xl flex-1 p-4 font-mono text-xs overflow-hidden flex flex-col relative shadow-[0_0_30px_rgba(0,0,0,0.5)_inset]">
            <div className="absolute top-0 left-0 right-0 bg-gray-900/90 p-2 border-b border-gray-800 flex justify-between items-center z-10">
              <span className="flex items-center gap-2 text-gray-400"><Terminal className="w-3 h-3" /> /var/log/sentinel/cognitive.log</span>
              <span className="flex gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div><div className="w-2 h-2 rounded-full bg-yellow-500"></div><div className="w-2 h-2 rounded-full bg-green-500"></div></span>
            </div>
            <div className="flex-1 overflow-y-auto pt-8 space-y-1 scrollbar-hide">
              {logs.map((log) => (
                <div key={log.id} className="flex gap-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <span className="text-gray-600">[{log.timestamp}]</span>
                  <span className={clsx(
                    log.type === 'info' && 'text-blue-400',
                    log.type === 'alert' && 'text-yellow-400 font-bold',
                    log.type === 'block' && 'text-red-500 font-black bg-red-900/20 px-1',
                    log.type === 'success' && 'text-green-400',
                  )}>
                    {log.type === 'alert' && '⚠️ '}
                    {log.type === 'block' && '🛑 '}
                    {log.message}
                  </span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>

        {/* Right Column: Recent Events */}
        <div className="col-span-3 bg-surface border border-gray-800 rounded-xl p-6 flex flex-col overflow-hidden">
          <h2 className="text-gray-400 text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4" /> Eventos Recientes
          </h2>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
            {events.map((evt, i) => (
              <EventCard key={i} event={evt} />
            ))}
            {events.length === 0 && <div className="text-gray-600 text-center mt-10">Esperando actividad...</div>}
          </div>
        </div>

      </div>
    </div>
  );
}

const ServiceStatus = ({ name, status }: { name: string, status: 'active' | 'inactive' }) => (
  <div className="flex justify-between items-center p-3 bg-gray-900/50 rounded-lg border border-gray-800/50">
    <span className="text-sm font-medium text-gray-300">{name}</span>
    <span className={`text-xs px-2 py-0.5 rounded uppercase font-bold tracking-wider ${status === 'active' ? 'bg-green-900/30 text-green-400 border border-green-900' : 'bg-red-900/30 text-red-400 border border-red-900'}`}>
      {status}
    </span>
  </div>
);

const EventCard = ({ event }: { event: DashboardEvent }) => {
  const getIcon = () => {
    switch (event.type) {
      case 'process_start': return <Cpu className="w-4 h-4 text-blue-400" />;
      case 'detections': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'decision': return event.data.blocked ? <Lock className="w-4 h-4 text-red-400" /> : <Unlock className="w-4 h-4 text-green-400" />;
    }
  };

  const getBorderColor = () => {
    switch (event.type) {
      case 'process_start': return 'border-blue-900/30 hover:border-blue-500/50';
      case 'detections': return 'border-yellow-900/30 bg-yellow-900/10 hover:border-yellow-500/50';
      case 'decision': return event.data.blocked ? 'border-red-900/30 bg-red-900/10 hover:border-red-500/50' : 'border-green-900/30 hover:border-green-500/50';
    }
  };

  return (
    <div className={`p-3 rounded border transition-colors duration-200 ${getBorderColor()} bg-gray-900/30`}>
      <div className="flex items-center gap-2 mb-1">
        {getIcon()}
        <span className="text-xs font-bold text-gray-300 uppercase">{event.type.replace('_', ' ')}</span>
      </div>
      <div className="text-sm text-white font-mono break-all">{event.data.comm} (PID: {event.data.pid})</div>
      {event.data.decision && (
        <div className={`text-xs mt-1 font-bold ${event.data.blocked ? 'text-red-400' : 'text-green-400'}`}>
          IA VERDICT: {event.data.decision}
        </div>
      )}
    </div>
  );
}

// Utility for classnames 
function clsx(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}

export default App;
