import { NextResponse } from "next/server";
import { readReport, reportNameFromRequest } from "@/lib/server/reports";
import { noStore, sessionError, validateSession } from "@/lib/server/session";

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) return sessionError(session.status);
  const name = reportNameFromRequest(request);
  if (!name) return noStore(NextResponse.json({ ok: false, error: "id o name requerido" }, { status: 400 }));
  const report = await readReport(name);
  if (!report) return noStore(NextResponse.json({ ok: false, error: "Informe no encontrado" }, { status: 404 }));
  const safeName = name.replace(/["\\\r\n]/g, "_");
  return noStore(new NextResponse(new Uint8Array(report), {
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Disposition": `attachment; filename="${safeName}"`,
      "X-Content-Type-Options": "nosniff",
    },
  }));
}
