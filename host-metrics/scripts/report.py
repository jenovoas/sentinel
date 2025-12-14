#!/usr/bin/env python3
import argparse
import csv
from statistics import mean

HTML_TMPL = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>Reporte de Métricas (Host)</title>
<style>
body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
.card {{ background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px; margin-bottom: 16px; }}
.grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
.badge {{ display: inline-block; padding: 4px 8px; border-radius: 999px; background: rgba(34, 197, 94, 0.15); color: #22c55e; font-size: 12px; }}
</style>
</head>
<body>
<h1>Reporte de Métricas (Host)</h1>
<div class="grid">
    <div class="card"><h3>CPU</h3><p>Promedio: {cpu_avg}%</p></div>
    <div class="card"><h3>Memoria</h3><p>Promedio: {mem_avg}%</p></div>
    <div class="card"><h3>GPU</h3><p>Promedio: {gpu_avg}%</p></div>
    <div class="card"><h3>WiFi</h3><p>Señal Promedio: {wifi_avg}%</p></div>
</div>
<p class="badge">Muestras: {samples}</p>
</body>
</html>
"""


def parse_args():
    p = argparse.ArgumentParser(description="Generate HTML report from metrics CSV")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    return p.parse_args()


def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def main():
    args = parse_args()
    rows = load_rows(args.input)
    cpu = [to_float(r.get("cpu_percent", 0)) for r in rows]
    mem = [to_float(r.get("mem_percent", 0)) for r in rows]
    gpu = [to_float(r.get("gpu_percent", 0)) for r in rows]
    wifi = [to_float(r.get("wifi_signal", 0)) for r in rows]

    html = HTML_TMPL.format(
        cpu_avg=round(mean(cpu), 2) if cpu else 0,
        mem_avg=round(mean(mem), 2) if mem else 0,
        gpu_avg=round(mean(gpu), 2) if gpu else 0,
        wifi_avg=round(mean(wifi), 2) if wifi else 0,
        samples=len(rows),
    )

    with open(args.output, "w") as f:
        f.write(html)

    print(f"✓ HTML report written to {args.output}")


if __name__ == "__main__":
    main()
