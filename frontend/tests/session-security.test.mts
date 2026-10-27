import assert from "node:assert/strict";
import test from "node:test";
import { hasValidCsrf, isSameOrigin, readCookie } from "../src/lib/server/security.ts";
import { isValidReportName } from "../src/lib/server/reports.ts";

test("Origin must match the externally visible host and protocol", () => {
  const sameOrigin = new Request("http://internal:3000/api/auth/logout", {
    headers: {
      origin: "https://sentinel.example",
      host: "internal:3000",
      "x-forwarded-host": "sentinel.example",
      "x-forwarded-proto": "https",
    },
  });
  const crossOrigin = new Request("http://internal:3000/api/auth/logout", {
    headers: { origin: "https://attacker.example", host: "sentinel.example" },
  });

  assert.equal(isSameOrigin(sameOrigin), true);
  assert.equal(isSameOrigin(crossOrigin), false);
  assert.equal(isSameOrigin(new Request("http://sentinel.example/api/auth/logout")), false);
});

test("Mutations require a matching double-submit CSRF token", () => {
  const valid = new Request("http://sentinel.example/api/v1/ai/query", {
    headers: { cookie: "sentinel_csrf=token-1", "x-csrf-token": "token-1" },
  });
  const invalid = new Request("http://sentinel.example/api/v1/ai/query", {
    headers: { cookie: "sentinel_csrf=token-1", "x-csrf-token": "token-2" },
  });

  assert.equal(hasValidCsrf(valid), true);
  assert.equal(hasValidCsrf(invalid), false);
  assert.equal(readCookie(new Request("http://sentinel.example", { headers: { cookie: "sentinel_session=%E0%A4%A" } }), "sentinel_session"), undefined);
});

test("Report identifiers cannot be absolute or traverse directories", () => {
  assert.equal(isValidReportName("daily-report.html"), true);
  assert.equal(isValidReportName("../secrets"), false);
  assert.equal(isValidReportName("/etc/passwd"), false);
  assert.equal(isValidReportName("folder\\report.html"), false);
  assert.equal(isValidReportName(".."), false);
});
