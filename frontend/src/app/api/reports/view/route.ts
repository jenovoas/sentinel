import { NextResponse } from "next/server";
import { readReport, reportNameFromRequest } from "@/lib/server/reports";
import { noStore, sessionError, validateSession } from "@/lib/server/session";

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) return sessionError(session.status);
  const name = reportNameFromRequest(request);
  if (!name) return noStore(NextResponse.json({ ok: false, error: "id o name requerido" }, { status: 400 }));
  if (!name.toLowerCase().endsWith(".html")) {
    return noStore(NextResponse.json({ ok: false, error: "Tipo de informe no permitido" }, { status: 400 }));
  }
  const report = await readReport(name);
  if (!report) return noStore(NextResponse.json({ ok: false, error: "Informe no encontrado" }, { status: 404 }));
  return noStore(new NextResponse(report.toString("utf8"), {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Content-Security-Policy": "sandbox; default-src 'none'; img-src data:; style-src 'unsafe-inline'",
      "X-Content-Type-Options": "nosniff",
    },
  }));
}
