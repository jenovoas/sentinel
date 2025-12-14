#!/usr/bin/env python3
import argparse
import csv
from datetime import datetime
from statistics import mean


def parse_args():
    p = argparse.ArgumentParser(description="Analyze host metrics CSV")
    p.add_argument("--input", required=True, help="Path to metrics.csv")
    p.add_argument("--output", required=True, help="Path to analysis.md")
    return p.parse_args()


def load_rows(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def main():
    args = parse_args()
    rows = load_rows(args.input)
    if not rows:
        with open(args.output, "w") as f:
            f.write("No hay datos para analizar.\n")
        return

    cpu = [to_float(r["cpu_percent"]) for r in rows]
    mem = [to_float(r["mem_percent"]) for r in rows]
    gpu = [to_float(r["gpu_percent"]) for r in rows]
    wifi = [to_float(r["wifi_signal"]) for r in rows]

    summary = {
        "samples": len(rows),
        "cpu_avg": round(mean(cpu), 2),
        "mem_avg": round(mean(mem), 2),
        "gpu_avg": round(mean(gpu), 2),
        "wifi_avg": round(mean(wifi), 2),
    }

    ts_first = rows[0]["timestamp"]
    ts_last = rows[-1]["timestamp"]

    md = f"""
# Análisis de Métricas (Host)

- Muestras: {summary['samples']}
- Rango: {ts_first} → {ts_last}

## Promedios
- CPU: {summary['cpu_avg']}%
- Memoria: {summary['mem_avg']}%
- GPU: {summary['gpu_avg']}%
- WiFi (señal): {summary['wifi_avg']}%

## Observaciones
- Si WiFi promedio < 30%, revisar interferencias o distancia.
- Si GPU promedio = 0%, puede que el contenedor no tenga acceso a GPU.
- Para WiFi real desde Docker, usar sidecar con `network_mode: host` y leer `/proc/net/wireless`.
"""

    with open(args.output, "w") as f:
        f.write(md)

    print(f"✓ Reporte escrito en {args.output}")


if __name__ == "__main__":
    main()
