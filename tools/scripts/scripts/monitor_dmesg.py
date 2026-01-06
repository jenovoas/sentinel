#!/usr/bin/env python3
"""
Sentinel Core Monitor - Ringbuffer Reader
Reads block events directly from the eBPF ringbuffer instead of trace_pipe.
"""
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os
import subprocess
import json
import struct

sys.path.insert(0, os.path.expanduser('~/sentinel'))

from sentinel_core.brain.inference import SentinelBrain
from sentinel_core.ebpf.map_manager import MapManager

RINGBUF_PATH = "/sys/fs/bpf/guardian_alpha/events"

def read_ringbuffer():
    """
    Lee eventos del ringbuffer usando bpftool.
    Formato del evento (struct event en guardian_cognitive.c):
    - pid: u32 (4 bytes)
    - uid: u32 (4 bytes)
    - filename: char[256] (256 bytes)
    - pattern: char[64] (64 bytes)
    - action: u8 (1 byte)
    - timestamp: u64 (8 bytes)
    Total: 333 bytes
    """
    print("🧠 [SentinelBrain] Conectando a Ollama Local: phi3:mini")
    brain = SentinelBrain()
    map_manager = MapManager()
    
    print(f"📡 [Monitor] Leyendo eventos desde ringbuffer: {RINGBUF_PATH}")
    
    # Usar bpftool para leer el ringbuffer
    # Nota: bpftool no tiene comando directo para ringbuf, usaremos un enfoque alternativo
    # Vamos a monitorear usando dmesg o kernel logs
    
    print("⚠️  [Monitor] Ringbuffer directo no soportado por bpftool.")
    print("📡 [Monitor] Cambiando a monitoreo de dmesg...")
    
    # Alternativa: usar dmesg para capturar printk del kernel
    proc = subprocess.Popen(
        ['sudo', 'dmesg', '-w'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        for line in proc.stdout:
            if "Guardian [BLOCK]" in line:
                # Extraer el nombre del archivo
                try:
                    parts = line.split("Unknown binary ")
                    if len(parts) > 1:
                        filename = parts[1].strip()
                        handle_block_event(filename, brain, map_manager)
                except Exception as e:
                    print(f"⚠️ [Monitor] Error parseando: {e}")
    except KeyboardInterrupt:
        print("\n🛑 [Monitor] Deteniendo...")
        proc.terminate()

def handle_block_event(filename: str, brain, map_manager):
    """Maneja un evento de bloqueo."""
    print(f"🔍 [Monitor] Detectado bloqueo: {filename}")
    
    should_allow = brain.analyze_threat(filename)
    
    if should_allow:
        print(f"🛡️  [Brain] Decisión: PERMITIR '{filename}'")
        if map_manager.whitelist_binary(filename):
            print(f"✅ [Kernel] Whitelist actualizada.")
    else:
        print(f"🚫 [Brain] Decisión: BLOQUEO CONFIRMADO para '{filename}'")

if __name__ == "__main__":
    read_ringbuffer()
