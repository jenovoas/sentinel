import { proxyBackend } from "@/lib/server/backend-proxy";

export async function GET(request: Request) {
    return proxyBackend(request, "ai/health");
}
