import { proxyBackend } from "@/lib/server/backend-proxy";

export async function POST(request: Request) {
  return proxyBackend(request, "ai/query");
}
