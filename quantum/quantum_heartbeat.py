#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

# quantum_heartbeat.py — Orquestador Resonante del Stack Cuántico Completo
"""
QUANTUM HEARTBEAT — El Director de Orquesta
============================================
Conecta todos los pilares del stack cuántico de Sentinel al ritmo
del ResonantLoop (17s = breath_cycle, 68s = master_cycle):

  Pulso 17s (Breath):
    → bring_ebpf_to_matrix: procesa eventos eBPF pendientes
    → SovereignCrystal: aplica entropía y propaga energía
    → TruthSync: verifica coherencia del estado actual

  Pulso 68s (Master Reset — 4 x 17s):
    → Purga de entropía acumulada en la lattice
    → Firma axiónica del estado → XDP Firewall actualiza reglas dinámicas
    → Registro en swarm:infra:log (bitácora S60)

Arquitectura del pipeline completo:
    Guardian-Alpha (Ring 0)
        │ eventos LSM
        ▼
    BringEbpfToMatrix          ← consume eventos eBPF
        │ CortexEventS60
        ▼
    SovereignCrystal           ← osciladores piezoeléctricos S60
        │ firma geométrica (amplitud, fase, coherencia)
        ▼
    TruthSync (n8n webhook)    ← verifica que la geometría cierre
        │ bool: verified / rejected
        ▼
    XDP Firewall               ← reglas dinámicas basadas en firma axiónica
        │ update blacklist/whitelist map
        ▼
    Redis (swarm:infra:log)    ← bitácora S60 inmutable

Autor: Jaime Novoa (Ea-nasir) / Quantum Heartbeat Integrator
YATRA: Cero floats. Cero random. Solo S60.
"""

import asyncio
import os
import sys
import time
import json
import subprocess
import redis

from quantum.yatra_core import S60
from quantum.sovereign_crystal import SovereignCrystal
from quantum.truthsync_verification import TruthSyncClient
from quantum.resonant_lattice_memory import ResonantLatticeMemory
import threading
try:
    from quantum.infra_cascade_adapter import InfraCascadeAdapter
    HAS_INFRA_ADAPTER = True
except ImportError:
    HAS_INFRA_ADAPTER = False

# ─────────────────────────────────────────── CONSTANTES YATRA ─────

# Ciclos resonantes (sin Duration::from_secs — usamos sleep directo)
BREATH_CYCLE_S  = 17    # segundos — pulso de respiración
MASTER_CYCLE_S  = 68    # segundos — master reset (4 x 17s)

# Threshold de coherencia geométrica en S60
# Por debajo de este valor → la geometría no cierra → TruthSync rechaza
COHERENCE_THRESHOLD = S60(42, 0, 0)   # 42 grados soberanos

# Firma axiónica mínima para whitelist del XDP firewall
AXION_THRESHOLD     = S60(51, 0, 0)   # 51/60 de firma pura

# Redis stream
STREAM_KEY = "swarm:infra:log"
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

# XDP firewall map (bpftool map update)
XDP_MAP_PATH = "/sys/fs/bpf/ai_guardian_maps/xdp_config"


# ─────────────────────────────────────────── HEARTBEAT ────────────

class QuantumHeartbeat:
    """
    Director de Orquesta del Stack Cuántico.
    Pulsa a 17s/68s y coordina todos los pilares.
    """

    def __init__(self):
        # Bus cuántico
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.redis.ping()

        # Pilares del stack
        self.crystal = SovereignCrystal()
        self.truthsync = TruthSyncClient()
        self.memory_lattice = ResonantLatticeMemory(size_slots=30)

        # Estado del heartbeat
        self._breath_count = 0          # contador de ciclos 17s
        self._last_master_ts = int(time.time())
        self._running = False
        
        # Thread de bitácora
        if HAS_INFRA_ADAPTER:
            self.adapter = InfraCascadeAdapter()
            self.adapter_thread = threading.Thread(target=self._run_adapter_bg, daemon=True)
            self.adapter_thread.start()
            print("🔗 InfraCascadeAdapter backflow thread iniciado")
        else:
            self.adapter = None
        self.memory_lattice.start()

        print("🫀 Quantum Heartbeat iniciado")
        print(f"   breath_cycle = {BREATH_CYCLE_S}s")
        print(f"   master_cycle = {MASTER_CYCLE_S}s")

    # ── Pulso de Respiración (17s) ────────────────────────────────
    def _breath_pulse(self):
        """
        Ejecuta un ciclo de respiración:
        1. Aplica entropía al cristal soberano
        2. Propaga energía entre osciladores
        3. Obtiene firma geométrica actual
        4. Verifica coherencia con TruthSync
        """
        self._breath_count += 1
        ts = S60(int(time.time()) % 3600, 0, 0)

        print(f"\n🫁 Breath #{self._breath_count} | t={ts}")

        # 1. Paso de física: entropía + propagación
        time_step = S60(BREATH_CYCLE_S, 0, 0)
        self.crystal.apply_entropy(time_step)
        self.crystal.propagate()

        # 2. Firma geométrica actual
        coherence, axion_sig = self.crystal.get_signature()

        # 2.5. Escribir cadena de control en la memoria resonante
        control_string = f"HEARTBEAT_PULSE_{self._breath_count}"
        self.memory_lattice.write(control_string)
        print(f"   Memory Lattice: Escribiendo '{control_string}' para auditoría.")

        print(f"   Coherencia: {coherence} | Firma axiónica: {axion_sig}")

        # 3. Verificar si la geometría cierra (TruthSync)
        if coherence < COHERENCE_THRESHOLD:
            print(f"   ⚠️ Coherencia sub-soberana: geometría no cierra")
            verified = False
        else:
            verified = self.truthsync.verify_data(
                context="HEARTBEAT_PULSE",
                payload={
                    "breath": self._breath_count,
                    "coherence": str(coherence),
                    "axion_sig": str(axion_sig),
                    "timestamp": str(ts),
                }
            )

        # 4. Registrar en bitácora S60
        self.redis.xadd(STREAM_KEY, {
            "node":       "sentinel",
            "agent":      "quantum_heartbeat",
            "event_type": "BREATH_PULSE",
            "breath":     str(self._breath_count),
            "coherence":  str(coherence),
            "axion_sig":  str(axion_sig),
            "verified":   "1" if verified else "0",
            "timestamp":  str(ts),
        })

        return coherence, axion_sig, verified

    # ── Pulso Maestro (68s = 4 x breath) ─────────────────────────
    def _master_pulse(self, axion_sig: S60, verified: bool):
        """
        Ejecuta el Master Reset cada 68s:
        1. Purga entropía acumulada (inyecta energía)
        2. Si la firma axiónica es suficiente → actualiza XDP firewall
        3. Registra el evento de reset en la bitácora
        """
        print(f"\n🌀 MASTER CYCLE RESET (68s) | Purgando Entropía...")

        # 1. Purga: inyecta energía de compensación al cristal
        self.crystal.pump_energy()

        # 1.5. Auditar Memoria Resonante
        expected_string = f"HEARTBEAT_PULSE_{self._breath_count}"
        read_string = self.memory_lattice.read()
        memory_ok = (read_string == expected_string)
        
        if memory_ok:
            print("   Memory Lattice: ✅ Auditoría de fidelidad PASADA.")
        else:
            print(f"   Memory Lattice: ❌ Auditoría de fidelidad FALLIDA. Esperado: '{expected_string}', Obtenido: '{read_string}'")
            # Una firma axiónica no puede ser válida si la memoria está corrupta
            verified = False

        # 2. XDP Firewall: actualizar modo según firma axiónica
        if axion_sig >= AXION_THRESHOLD and verified:
            self._xdp_set_mode(mode=0)   # 0 = Normal
            print("   XDP: modo NORMAL (firma axiónica válida)")
        else:
            self._xdp_set_mode(mode=1)   # 1 = Quarantine
            print("   XDP: modo QUARANTINE (firma axiónica inválida)")

        # 3. Bitácora master reset
        self.redis.xadd(STREAM_KEY, {
            "node":       "sentinel",
            "agent":      "quantum_heartbeat",
            "event_type": "MASTER_RESET",
            "axion_sig":  str(axion_sig),
            "memory_audit": "PASSED" if memory_ok else "FAILED",
            "xdp_mode":   "0" if (axion_sig >= AXION_THRESHOLD and verified) else "1",
            "breath_count": str(self._breath_count),
        })

        self._last_master_ts = int(time.time())

    # ── Integración XDP Firewall ───────────────────────────────────
    def _xdp_set_mode(self, mode: int):
        """
        Actualiza el modo global del XDP firewall via bpftool.
        mode=0: Normal, mode=1: Quarantine/Panic
        """
        try:
            # bpftool map update — key=0 (config_map index), value=mode
            result = subprocess.run(
                ["bpftool", "map", "update", "pinned", XDP_MAP_PATH,
                 "key", "0", "0", "0", "0",
                 "value", str(mode), "0", "0", "0"],
                capture_output=True, timeout=5
            )
            if result.returncode != 0:
                print(f"   ⚠️ bpftool error: {result.stderr.decode()[:80]}")
        except FileNotFoundError:
            print("   ⚠️ bpftool no disponible — XDP mode no actualizado")
        except Exception as e:
            print(f"   ⚠️ XDP update error: {e}")

    # ── Thread Infra Cascade ───────────────────────────────────────
    def _run_adapter_bg(self):
        """Procesa pasivamente el stream swarm:infra:log."""
        try:
            self.adapter.process_backflow()
        except Exception as e:
            print(f"⚠️ InfraCascadeAdapter error: {e}")

    # ── Loop Principal ─────────────────────────────────────────────
    def run(self):
        """
        Loop resonante: pulsa cada 17s.
        Cada 4 pulsos → master reset.
        No usa async para simplicidad — sleep síncrono S60.
        """
        self._running = True
        print("\n🫀 Heartbeat activo. Ctrl+C para detener.\n")

        try:
            while self._running:
                t_start = int(time.time())

                # Ejecutar ciclo de respiración
                coherence, axion_sig, verified = self._breath_pulse()

                # Cada 4 pulsos → master reset
                if self._breath_count % 4 == 0:
                    self._master_pulse(axion_sig, verified)

                # Dormir hasta el próximo pulso (17s - tiempo de ejecución)
                elapsed = int(time.time()) - t_start
                remaining = BREATH_CYCLE_S - elapsed
                if remaining > 0:
                    time.sleep(remaining)

        except KeyboardInterrupt:
            print("\n🔴 Heartbeat detenido. Coherencia preservada.")
            self._running = False
            self.memory_lattice.stop()


# ─────────────────────────────────────────── ENTRY POINT ──────────

if __name__ == "__main__":
    print("=== QUANTUM HEARTBEAT — Stack Cuántico Sentinel ===")
    print(f"    Breath: {BREATH_CYCLE_S}s | Master: {MASTER_CYCLE_S}s")
    print(f"    Coherence threshold: {COHERENCE_THRESHOLD}")
    print(f"    Axion threshold:     {AXION_THRESHOLD}")
    print()

    hb = QuantumHeartbeat()
    hb.run()
