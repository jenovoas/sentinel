import { NextResponse } from "next/server";
import {
  clearSessionCookies,
  noStore,
  sessionError,
  validateSession,
} from "@/lib/server/session";

export async function GET(request: Request) {
  const session = await validateSession(request);
  if (!session.ok) {
    const response = sessionError(session.status);
    return session.status === 401 ? clearSessionCookies(response) : response;
  }

  return noStore(NextResponse.json({ user: session.identity }));
}
