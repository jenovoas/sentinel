import { registerHooks, createRequire } from "node:module";

// Execute server modules in Node tests with the same source aliases as Next.
// The build marker is not an authorization mechanism; no application module is mocked.
const require = createRequire(import.meta.url);
registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier === "server-only") return { url: "data:text/javascript,export{}", shortCircuit: true };
    if (specifier === "next/server") return { url: new URL(`file://${require.resolve("next/server")}`).href, shortCircuit: true };
    if (specifier.startsWith("@/")) return { url: new URL(`../src/${specifier.slice(2)}.ts`, import.meta.url).href, shortCircuit: true };
    try { return nextResolve(specifier, context); }
    catch (error) {
      if (specifier.startsWith(".") && context.parentURL?.includes("/src/") && !specifier.endsWith(".ts")) {
        return nextResolve(`${specifier}.ts`, context);
      }
      throw error;
    }
  },
});
