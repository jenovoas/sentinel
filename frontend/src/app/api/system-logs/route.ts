import { NextResponse } from "next/server";
import fs from "fs";
import { noStore, sessionError, validateSession } from "@/lib/server/session";
import { hostMetricsFile } from "@/lib/server/host-metrics";

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) return sessionError(session.status);
  try {
    const { searchParams } = new URL(request.url);
    const requestedLimit = Number(searchParams.get("limit") || 100);
    const limit = Number.isFinite(requestedLimit) ? Math.max(1, Math.min(requestedLimit, 500)) : 100;
    const level = searchParams.get("level")?.toUpperCase();

    const csvPath = hostMetricsFile("data", "system-logs.csv");
    const summaryPath = hostMetricsFile("data", "logs-summary.json");

    // Leer resumen
    let summary = null;
    if (fs.existsSync(summaryPath)) summary = JSON.parse(fs.readFileSync(summaryPath, "utf8"));

    if (!fs.existsSync(csvPath)) {
      return noStore(NextResponse.json({
        ok: true, 
        logs: [], 
        summary: summary || { critical_count: 0, error_count: 0, warning_count: 0, total_issues: 0 } 
      }));
    }

    const content = fs.readFileSync(csvPath, "utf8");
    const lines = content.trim().split(/\r?\n/);
    
    if (lines.length <= 1) {
      return noStore(NextResponse.json({ ok: true, logs: [], summary }));
    }

    let logs = lines.slice(1).map((line) => {
      const columns = line.split(",");
      return {
        timestamp: columns[0] || "",
        level: columns[1] || "INFO",
        unit: columns[2] || "system",
        message: columns.slice(3).join(",") || "",
      };
    });
    if (level) logs = logs.filter((log) => log.level === level);
    logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    logs = logs.slice(0, limit);

    return noStore(NextResponse.json({
      ok: true, 
      logs,
      summary: summary || { critical_count: 0, error_count: 0, warning_count: 0, total_issues: 0 },
      total: logs.length 
    }));
  } catch (e: any) {
    return noStore(NextResponse.json({ ok: false, error: e?.message || "error" }, { status: 500 }));
  }
}
