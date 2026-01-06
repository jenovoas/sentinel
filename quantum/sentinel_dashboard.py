#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
SENTINEL VIMANA DASHBOARD (OBSERVATORY)
---------------------------------------
Interfaz CLI en tiempo real para visualizar el estado cuántico del sistema.
FUENTE DE VERDAD: Lee 'perpetual_engine_status.json' directamente.
NO SIMULA, NO INTERPOLA.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import curses
import time
import json
import os
import sys
# Importamos la lógica de red (Lattice) para visualizar su estado teórico
from quantum_lattice import VimanaLattice

STATUS_FILE = "/home/jnovoas/sentinel/quantum/perpetual_engine_status.json"

def load_real_status():
    """Lee el estado real del disco. Si falla, retorna estado NULO."""
    if not os.path.exists(STATUS_FILE):
        return None
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None # Lectura sucia (race condition), mejor mostrar nada que mentir

def draw_bar(stdscr, y, x, label, value, max_val, color_pair):
    """Dibuja una barra de progreso honesta."""
    bar_len = 30
    normalized = max(S60(0, 0, 0), min(S60(1, 0, 0), value / max_val))
    filled_len = int(normalized * bar_len)
    
    stdscr.addstr(y, x, f"{label}: [", curses.color_pair(1))
    stdscr.addstr("=" * filled_len, color_pair)
    stdscr.addstr(" " * (bar_len - filled_len), curses.color_pair(1))
    stdscr.addstr(f"] {value:.4f}")

def draw_hex_grid(stdscr, y, x, energy_level):
    """
    Visualización ASCII de la Red Hexagonal.
    El 'brillo' (nodos activos) depende de la energía real del motor.
    """
    # Si hay energía, el nucleo brilla. Si hay mucha, el anillo brilla.
    core_char = "●" if energy_level > 0 else "○"
    ring_char = "●" if energy_level > 10 else "○"
    
    # ASCII Hex Art
    #   ○   ○
    # ○   ●   ○
    #   ○   ○
    
    stdscr.addstr(y,   x+4, ring_char, curses.color_pair(3))
    stdscr.addstr(y,   x+8, ring_char, curses.color_pair(3))
    
    stdscr.addstr(y+1, x+2, ring_char, curses.color_pair(3))
    stdscr.addstr(y+1, x+6, core_char, curses.color_pair(2) | curses.A_BOLD) # Centro
    stdscr.addstr(y+1, x+10, ring_char, curses.color_pair(3))
    
    stdscr.addstr(y+2, x+4, ring_char, curses.color_pair(3))
    stdscr.addstr(y+2, x+8, ring_char, curses.color_pair(3))
    
    stdscr.addstr(y+4, x, f"Lattice Status: {'CHARGED' if energy_level > 10 else 'DRAINED'}")

def main(stdscr):
    # Configuración Curses
    curses.curs_set(0) # Ocultar cursor
    stdscr.nodelay(1)  # No bloquear
    curses.start_color()
    
    # Colores Resonantes
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # Texto Base
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Bueno / Coherente
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Medio / Energía
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)   # Malo / Fricción
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Frío / Hielo

    while True:
        stdscr.clear()
        
        # 1. Cabecera
        stdscr.addstr(1, 2, "🛡️  SENTINEL VIMANA DASHBOARD (REAL-TIME)", curses.A_BOLD)
        stdscr.addstr(2, 2, "="*45)

        # 2. Leer Datos Reales
        data = load_real_status()
        
        if data:
            timestamp = time.ctime(data.get("timestamp", 0))
            energy = data.get("energy", S60(0, 0, 0))
            
            # Physics (Si existen)
            physics = data.get("physics", {})
            coherence = physics.get("coherence", S60(0, 0, 0))
            friction = physics.get("friction", S60(0, 0, 0))
            load = physics.get("load", S60(0, 0, 0))
            
            # Audit info
            audit = data.get("truthsync", {})
            audit_status = "PASSED" if audit.get("verified") else "PENDING/OFFLINE"
            
            # --- PANTALLA ---
            stdscr.addstr(4, 2, f"🕒 Last Tick: {timestamp}")
            
            # Energía (Axiones)
            draw_bar(stdscr, 6, 2, "ENERGY (AX)", energy, 200.0, curses.color_pair(3))
            
            # Coherencia (Cristal)
            # Rango 0-1
            coh_color = curses.color_pair(2) if coherence > 0.9 else curses.color_pair(4)
            draw_bar(stdscr, 8, 2, "COHERENCE  ", coherence, S60(1, 0, 0), coh_color)
            
            # Fricción (CPU Load)
            # Rango 0-1 (Inverso, menos es mejor)
            fric_color = curses.color_pair(4) if friction > 0.2 else curses.color_pair(5)
            draw_bar(stdscr, 10, 2, "FRICTION   ", friction, S60(0, 30, 0), fric_color)
            
            stdscr.addstr(12, 2, f"🖥️  CPU Load: {load:.2f}")
            stdscr.addstr(12, 25, f"⚖️  TruthSync: {audit_status}")

            # 3. Visualización Lattice
            draw_hex_grid(stdscr, 15, 20, energy)
            
        else:
            stdscr.addstr(10, 10, "⚠️  NO SIGNAL (ENGINE OFFLINE)", curses.color_pair(4) | curses.A_BLINK)
            stdscr.addstr(12, 10, "Waiting for Superradiant Burst...", curses.color_pair(1))

        # 4. Pie de página
        stdscr.addstr(22, 2, "[Q] Quit", curses.color_pair(1))
        
        stdscr.refresh()
        
        # Input Loop
        c = stdscr.getch()
        if c == ord('q'):
            break
        
        time.sleep(S60(0, 6, 0)) # Refresco visual amigable (10Hz)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error fatal en dashboard: {e}")