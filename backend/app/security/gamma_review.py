"""Bounded, secret-redacted snapshots for human review and the existing audit log."""
import re
from itertools import islice
from typing import Any

_SENSITIVE_KEY = re.compile(r"password|passwd|passphrase|secret|token|authorization|cookie|credential|private.?key|api.?key|^(?:env|environment|cmdline|command_line)$", re.I)
_SECRET_TEXT = re.compile(
    r"-----BEGIN [^-]*PRIVATE KEY-----[\s\S]*?(?:-----END [^-]*PRIVATE KEY-----|$)"
    r"|\bBearer\s+[^\s,;]+"
    r"|\b(?:password|passwd|passphrase|secret|token|api[_-]?key)\s*(?:[=:]\s*|\s+)"
    r"""(?:"[^"]*"|'[^']*'|[^\s,;]+)"""
    r"|\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@"
    r"|\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", re.I
)
_CONTROLS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f\u202a-\u202e\u2066-\u2069]")


def review_snapshot(value: Any) -> Any:
    """Keep inert JSON within shared 16K-character/128-node/depth-5 budgets.

    Raw operational evidence remains in GammaDecision; only this projection is
    exposed to the browser or copied into audit details. Truncation is explicit.
    """
    remaining = 16384
    nodes = 128

    def text(item: str) -> str:
        nonlocal remaining
        clean = _CONTROLS.sub("", _SECRET_TEXT.sub("[REDACTED]", item))
        size = min(2048, remaining)
        remaining -= min(len(clean), size)
        return clean[:size] + (" [TRUNCATED]" if len(clean) > size else "")

    def visit(item: Any, depth: int) -> Any:
        nonlocal nodes
        nodes -= 1
        if nodes < 0 or remaining <= 0 or depth > 5:
            return "[TRUNCATED]"
        if isinstance(item, dict):
            result = {}
            for key, child in islice(item.items(), 32):
                label = text(str(key))
                result[label] = "[REDACTED]" if _SENSITIVE_KEY.search(str(key)) else visit(child, depth + 1)
                if nodes <= 0 or remaining <= 0:
                    break
            if len(result) < len(item):
                result["[TRUNCATED]"] = True
            return result
        if isinstance(item, (list, tuple)):
            result = []
            for child in islice(item, 32):
                result.append(visit(child, depth + 1))
                if nodes <= 0 or remaining <= 0:
                    break
            if len(result) < len(item):
                result.append("[TRUNCATED]")
            return result
        if isinstance(item, str):
            return text(item)
        if item is None or isinstance(item, (int, float, bool)):
            return item
        return text(str(item))

    return visit(value, 0)
