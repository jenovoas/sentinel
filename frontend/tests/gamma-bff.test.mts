import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { createServer } from "node:http";
import { once } from "node:events";
import "./server-test-hooks.mts";
const { proxyBackend } = await import("../src/lib/server/backend-proxy.ts");

const requests: { path: string; authorization?: string; cookie?: string; body: string }[] = [];
let oldUrl: string | undefined;
const server = createServer(async (request, response) => {
  let body = "";
  for await (const chunk of request) body += chunk;
  requests.push({ path: request.url!, authorization: request.headers.authorization, cookie: request.headers.cookie, body });
  response.setHeader("Content-Type", "application/json");
  const identity = request.headers.authorization?.replace("Bearer ", "");
  if (request.url === "/api/v1/auth/me") {
    if (identity === "expired") { response.writeHead(401); response.end('{"detail":"expired"}'); return; }
    if (identity === "auth-down") { response.writeHead(503); response.end('{}'); return; }
    response.end(JSON.stringify({ role: identity, is_superuser: identity === "platform-reviewer" }));
    return;
  }
  response.writeHead(200);
  response.end('[]');
});

before(async () => {
  oldUrl = process.env.SENTINEL_BACKEND_URL;
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const address = server.address();
  assert.ok(address && typeof address === "object");
  process.env.SENTINEL_BACKEND_URL = `http://127.0.0.1:${address.port}`;
});
after(async () => {
  if (oldUrl === undefined) delete process.env.SENTINEL_BACKEND_URL;
  else process.env.SENTINEL_BACKEND_URL = oldUrl;
  await new Promise<void>((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
});

function request(route: string, identity = "platform-reviewer", options: { method?: string; csrf?: string; origin?: string; contentType?: string } = {}) {
  const method = options.method ?? "GET";
  return new Request(`https://sentinel.example/api/v1/${route}`, {
    method,
    headers: {
      cookie: `sentinel_session=${identity}; sentinel_csrf=csrf-test`,
      origin: options.origin ?? "https://sentinel.example",
      "x-csrf-token": options.csrf ?? "csrf-test",
      "content-type": options.contentType ?? "application/json",
    },
    ...(method === "POST" ? { body: JSON.stringify({ feedback: "Evidence reviewed" }) } : {}),
  });
}

test("Gamma reads require a live platform superuser, not a tenant role", async () => {
  for (const identity of ["admin", "member", "viewer"]) {
    requests.length = 0;
    const response = await proxyBackend(request("gamma/pending", identity), "gamma/pending");
    assert.equal(response.status, 403);
    assert.deepEqual(requests.map((item) => item.path), ["/api/v1/auth/me"]);
    assert.match(response.headers.get("cache-control")!, /no-store/);
  }
  requests.length = 0;
  const response = await proxyBackend(request("gamma/pending"), "gamma/pending");
  assert.equal(response.status, 200);
  assert.deepEqual(requests.map((item) => item.path), ["/api/v1/auth/me", "/api/v1/gamma/pending"]);
  assert.equal(requests[1].authorization, "Bearer platform-reviewer");
  assert.equal(requests[1].cookie, undefined);
});

test("missing/expired sessions and unavailable identity fail closed", async () => {
  requests.length = 0;
  assert.equal((await proxyBackend(new Request("https://sentinel.example/api/v1/gamma/pending"), "gamma/pending")).status, 401);
  assert.equal(requests.length, 0);
  const expired = await proxyBackend(request("gamma/pending", "expired"), "gamma/pending");
  assert.equal(expired.status, 401);
  assert.match(expired.headers.get("set-cookie")!, /Max-Age=0/);
  assert.equal((await proxyBackend(request("gamma/pending", "auth-down"), "gamma/pending")).status, 503);
  assert.ok(requests.every((item) => item.path === "/api/v1/auth/me"));
});

test("Gamma mutations reject cross-origin, missing/mismatched CSRF and wrong media before any upstream call", async () => {
  for (const options of [
    { origin: "https://attacker.example" }, { csrf: "" }, { csrf: "wrong" }, { contentType: "text/plain" },
  ]) {
    requests.length = 0;
    const response = await proxyBackend(request("gamma/approve/7", "platform-reviewer", { method: "POST", ...options }), "gamma/approve/7");
    assert.equal(response.status, options.contentType ? 415 : 403);
    assert.equal(requests.length, 0);
  }
});

test("tenant admin cannot mutate even with valid CSRF; canonical review IDs only", async () => {
  requests.length = 0;
  assert.equal((await proxyBackend(request("gamma/deny/7", "admin", { method: "POST" }), "gamma/deny/7")).status, 403);
  assert.deepEqual(requests.map((item) => item.path), ["/api/v1/auth/me"]);
  for (const route of ["gamma/decision", "gamma/cleanup", "gamma/approve/../7", "gamma/approve/07", "gamma/deny/0", "gamma/approve/7/extra"]) {
    requests.length = 0;
    assert.equal((await proxyBackend(request(route, "platform-reviewer", { method: "POST" }), route)).status, 404);
    assert.equal(requests.length, 0);
  }
  assert.equal((await proxyBackend(request("gamma/approve/7"), "gamma/approve/7")).status, 405);
});

