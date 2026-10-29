export function csrfTokenFromCookie(): string {
  if (typeof document === "undefined") return "";
  const value = document.cookie.split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith("sentinel_csrf="))
    ?.slice("sentinel_csrf=".length);
  if (!value) return "";
  try {
    return decodeURIComponent(value);
  } catch {
    return "";
  }
}
