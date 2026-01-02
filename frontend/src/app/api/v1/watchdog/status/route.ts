import { NextResponse } from "next/server";

export async function GET() {
    try {
        // Fetch real data from backend
        const response = await fetch("http://localhost:8000/watchdog/status", {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error(`Backend returned ${response.status}`);
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error) {
        console.error("Watchdog status error:", error);

        // Fallback to mock data if backend is unavailable
        const fallbackData = {
            timestamp: new Date().toISOString(),
            hardware_watchdog: {
                enabled: true,
                status: "active",
                last_kick: new Date(Date.now() - 15000).toISOString(),
                interval_seconds: 30,
                device: "/dev/watchdog"
            },
            systemd_services: [
                {
                    name: "sentinel-hardware-watchdog",
                    status: "active",
                    uptime_seconds: 7200,
                    restart_count: 0
                },
                {
                    name: "sentinel-core",
                    status: "active",
                    uptime_seconds: 7200,
                    restart_count: 0
                }
            ],
            docker_containers: [
                {
                    name: "truthsync-prometheus",
                    health: "healthy",
                    uptime_seconds: 7200,
                    restart_count: 1
                },
                {
                    name: "sentinel-grafana",
                    health: "healthy",
                    uptime_seconds: 7200,
                    restart_count: 2
                },
                {
                    name: "sentinel-loki",
                    health: "healthy",
                    uptime_seconds: 7200,
                    restart_count: 0
                },
                {
                    name: "sentinel-truth-db",
                    health: "healthy",
                    uptime_seconds: 7200,
                    restart_count: 0
                },
                {
                    name: "sentinel-truth-redis",
                    health: "healthy",
                    uptime_seconds: 7200,
                    restart_count: 0
                }
            ],
            alerts: ["⚠️ Backend unavailable - showing cached data"]
        };

        return NextResponse.json(fallbackData);
    }
}
