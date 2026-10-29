import { NextResponse } from "next/server";
import { listReports } from "@/lib/server/reports";
import { noStore, sessionError, validateSession } from "@/lib/server/session";

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) return sessionError(session.status);
  try {
    return noStore(NextResponse.json({ ok: true, items: await listReports() }));
  } catch {
    return noStore(NextResponse.json({ ok: false, error: "No se pudieron leer los informes" }, { status: 500 }));
  }
}
