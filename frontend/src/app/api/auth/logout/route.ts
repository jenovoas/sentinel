import { NextResponse } from "next/server";
import {
  clearSessionCookies,
  hasValidCsrf,
  isSameOrigin,
} from "@/lib/server/session";

export async function POST(request: Request) {
  if (!isSameOrigin(request) || !hasValidCsrf(request)) {
    return NextResponse.json(
      { error: "Solicitud no válida" },
      { status: 403, headers: { "Cache-Control": "private, no-store, max-age=0" } },
    );
  }

  return clearSessionCookies(NextResponse.json({ ok: true }));
}
