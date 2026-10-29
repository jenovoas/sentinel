import { proxyBackend } from "@/lib/server/backend-proxy";

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: Request, context: RouteContext) {
  const { path } = await context.params;
  return proxyBackend(request, path.join("/"));
}

export const GET = proxy;
export const POST = proxy;
