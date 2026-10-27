import { proxyCortex } from "@/lib/server/cortex-proxy";

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: Request, context: RouteContext) {
  const { path } = await context.params;
  return proxyCortex(request, path.join("/"));
}

export const GET = proxy;
export const POST = proxy;
