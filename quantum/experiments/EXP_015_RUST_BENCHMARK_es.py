#!/usr/bin/env python3
# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# EXPERIMENTO 015: BENCHMARK RUST HIPER-ESCALA
# -----------------------------------------------------------------------------
# Objetivo:
#   Comparar consumo de RAM entre:
#   1. Python Sparse Lattice (EXP-014)
#   2. Rust Sentinel Core (Fase 4)
# -----------------------------------------------------------------------------
# REVIEW: Se corrigió shadowing de variables temporales t0/t1 que invalidaba
#         la comparación de velocidad (ver sección COMPARISON).
# -----------------------------------------------------------------------------

import os
import secrets
import sys
import time
import tracemalloc

sys.path.append(os.getcwd())

# Import Python Implementation
from quantum.liquid_lattice_storage import LiquidLatticeStorage

# Import Rust Implementation
try:
    from quantum.sentinel_core import RustLattice
    RUST_AVAILABLE = True
except ImportError as e:
    print(f"❌ Rust Core No Encontrado: {e}")
    RUST_AVAILABLE = False
    sys.exit(1)

def run_benchmark():
    print("🔬 EXP-015: BENCHMARK RUST vs PYTHON")
    print("-" * 60)

    # ---------------------------------------------------------
    # TEST 1: ASIGNACIÓN RUST (1 Millón de Nodos)
    # ---------------------------------------------------------
    print("\n🦀 Probando Rust Core (1,000,000 Nodos)...")

    tracemalloc.start()
    start_snap = tracemalloc.take_snapshot()

    # Crear Lattice
    rust_lattice = RustLattice(rings=1) # Parámetro rings sin uso en Rust V1

    # Payload: 1 Millón * 8 Bytes (Capacidad) = 8 MB Datos
    # Pero la implementación Rust consume datos en chunks de 16 bytes (align struct) o 8 bytes?
    # Nuestra implementación Rust toma chunks de 16 bytes para creación.
    # Si queremos 1M nodos, necesitamos 16 MB de datos de entrada.

    data_size = 1_000_000 * 16
    payload = secrets.token_bytes(data_size)

    # REVIEW: usar variables específicas para evitar shadowing con Test 2
    t0_rust = time.time()
    count = rust_lattice.inject(payload)
    t1_rust = time.time()

    end_snap = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = end_snap.compare_to(start_snap, 'lineno')
    # Filtrar asignaciones significativas?
    # Nota: Las asignaciones de Rust ocurren FUERA de la visibilidad de tracemalloc de Python,
    # a menos que se use pymalloc.
    # Pero `active_memory_usage()` de Rust nos puede informar.

    rust_mem_reported = rust_lattice.active_memory_usage()
    rust_time = t1_rust - t0_rust
    rust_throughput = count / rust_time

    print(f"   Nodos Creados: {count}")
    print(f"   Tiempo: {rust_time:.4f}s")
    print(f"   Throughput: {rust_throughput / 1_000_000:.2f} M Nodos/s")
    print(f"   Memoria Reportada por Rust: {rust_mem_reported / 1024**2:.2f} MB")
    print(f"   Bytes por Nodo: {rust_mem_reported / count:.2f} B")

    # ---------------------------------------------------------
    # TEST 2: BASELINE PYTHON (10,000 Nodos)
    # ---------------------------------------------------------
    # No podemos hacer 1M en Python fácilmente (350MB + lento), pero probemos 10k para extrapolar.
    print("\n🐍 Probando Python Sparse (10,000 Nodos)...")

    tracemalloc.start()
    py_lattice = LiquidLatticeStorage(rings=1)

    # 10k nodos * 16 bytes = 160 KB
    py_payload = secrets.token_bytes(10_000 * 16)

    t0_py = time.time()
    py_lattice.inject_holograph(py_payload)
    t1_py = time.time()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    py_mem = current
    py_count = len(py_lattice.nodes)
    py_time = t1_py - t0_py
    py_throughput = py_count / py_time

    print(f"   Nodos Creados: {py_count}")
    print(f"   Tiempo: {py_time:.4f}s")
    print(f"   Throughput: {py_throughput / 1_000_000:.2f} M Nodos/s")
    print(f"   Memoria Python: {py_mem / 1024**2:.2f} MB")
    print(f"   Bytes por Nodo: {py_mem / py_count:.2f} B")

    # ---------------------------------------------------------
    # COMPARACIÓN
    # ---------------------------------------------------------
    ratio_mem = (py_mem / py_count) / (rust_mem_reported / count)
    # REVIEW: Antes usaba t0/t1 del último bloque (Python) para ambos cálculos.
    #         Ahora usa rust_time y py_time separados.
    ratio_speed_val = rust_throughput / py_throughput

    print("-" * 60)
    print(f"🚀 RESULTADOS:")
    print(f"   Eficiencia Memoria: Rust es {ratio_mem:.1f}x más eficiente")
    print(f"   Aceleración: Rust es {ratio_speed_val:.1f}x más rápido")

    if ratio_mem > 10 and (rust_mem_reported / count) <= 16.0:
        print("\n✅ PASS: Objetivos Hiper-Escala Cumplidos.")
    else:
        print("\n⚠️ ADVERTENCIA: Objetivos no cumplidos totalmente.")

if __name__ == "__main__":
    run_benchmark()
