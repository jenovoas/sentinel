import { NextResponse } from "next/server";

// Use Grafana Proxy because direct Prometheus port 9091 might be blocked/unstable from Host
const GRAFANA_URL = process.env.GRAFANA_URL || "http://localhost:3001";
const PROMETHEUS_DS_ID = "2"; // From /api/datasources

async function queryPrometheus(query: string) {
    try {
        const res = await fetch(`${GRAFANA_URL}/api/datasources/proxy/${PROMETHEUS_DS_ID}/api/v1/query?query=${encodeURIComponent(query)}`, {
            cache: 'no-store'
        });
        const json = await res.json();
        if (json.status === 'success' && json.data.result.length > 0) {
            return parseFloat(json.data.result[0].value[1]);
        }
        return null;
    } catch (error) {
        console.error("Prometheus query error (via Grafana):", error);
        return null;
    }
}

export async function GET() {
    const now = new Date();

    // Queries
    const cpuQuery = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)';
    const memQuery = '100 * (1 - ((node_memory_MemFree_bytes + node_memory_Buffers_bytes + node_memory_Cached_bytes) / node_memory_MemTotal_bytes))';
    const uptimeQuery = 'time() - node_boot_time_seconds';
    const netRxQuery = 'rate(node_network_receive_bytes_total[1m])';
    const netTxQuery = 'rate(node_network_transmit_bytes_total[1m])';

    // Parallel Fetch
    const [cpu, mem, uptime, netRx, netTx] = await Promise.all([
        queryPrometheus(cpuQuery),
        queryPrometheus(memQuery),
        queryPrometheus(uptimeQuery),
        queryPrometheus(netRxQuery),
        queryPrometheus(netTxQuery)
    ]);

    // Determines System Status based on CPU/Mem
    let systemStatus = "OPTIMAL";
    if ((cpu && cpu > 80) || (mem && mem > 90)) systemStatus = "CRITICAL";
    else if ((cpu && cpu > 60) || (mem && mem > 70)) systemStatus = "WARNING";

    const data = {
        timestamp: now.toISOString(),
        status: {
            system: systemStatus,
            cpu: cpu ? cpu.toFixed(1) : 0,
            memory: mem ? mem.toFixed(1) : 0,
            uptime: uptime ? Math.floor(uptime) : 0,
            active_threats: 0, // Placeholder for Backend Security Service
            defense_level: "LEVEL 6", // Static for now
            ai_latency: "45ms", // Placeholder
            auth_personnel: 1, // User session
            network_nodes: 128, // Static
            db_transactions: 1204, // Placeholder
        },
        network: {
            rx_bytes_sec: netRx ? netRx.toFixed(0) : 0,
            tx_bytes_sec: netTx ? netTx.toFixed(0) : 0,
        },
        alerts: []
    };

    return NextResponse.json(data);
}
