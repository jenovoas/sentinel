#!/usr/bin/env python3
# 🛡️ ME-60OS: QUANTUM SCHEDULER DAEMON 🛡️
# -----------------------------------------------------------------------------
# ORQUESTADOR DE TAREAS BASADO EN PENTA-RESONANCIA
# "No actúes cuando quieras. Actúa cuando el Universo te abra la puerta."
# -----------------------------------------------------------------------------
# 🎯 CONCEPTO: Adiabatic Computing
# En lugar de ejecutar tareas inmediatamente (forzando contra resistencia),
# esperamos los PORTALES de convergencia armónica donde el sistema está
# en superconductividad (resistencia = 0).
# -----------------------------------------------------------------------------
# ⚠️ EXPERIMENTAL: Usa math/random para demo. Versión producción usará S60.
# -----------------------------------------------------------------------------

import time
import math
import random
import sys
from collections import deque

# --- CONFIGURACIÓN VISUAL ---
C_WAIT = "\033[90m"   # Gris (Dormido)
C_OPEN = "\033[92m"   # Verde (Portal Abierto)
C_WARN = "\033[93m"   # Amarillo (Cola creciendo)
C_EXEC = "\033[97m\033[42m" # Fondo Verde (Ejecutando)
C_RESET = "\033[0m"

class QuantumScheduler:
    """
    Scheduler que ejecuta tareas SOLO durante ventanas de convergencia armónica.
    
    Principio Físico:
    - Ejecutar en portal: Costo energético = E
    - Ejecutar fuera de portal: Costo energético = 3E (resistencia térmica)
    
    Resultado: Ahorro de 2E por tarea al esperar portales.
    """
    
    def __init__(self):
        self.task_queue = deque()
        self.t = 0.0
        self.dt = 0.1  # 10 Hz de muestreo (visual)
        self.total_energy_saved = 0.0
        self.tasks_executed_in_portal = 0
        self.tasks_forced_outside = 0
        
        # Simulación de carga de trabajo entrante
        self.last_task_time = 0
        
        print("💎 QUANTUM SCHEDULER: INITIALIZING")
        print("   Bio-Adiabatic Task Orchestrator")
        print("   Waiting for Harmonic Windows...")

    def add_random_tasks(self):
        """Simula procesos del OS pidiendo CPU."""
        if random.random() < 0.15:  # 15% prob por tick
            task_id = random.randint(1000, 9999)
            task_type = random.choice([
                "ZPE_TUNE",      # Re-sintonización del reactor
                "BCI_SYNC",      # Sincronización bio-máquina
                "LATTICE_GC",    # Garbage collection de memoria líquida
                "BACKUP_S60",    # Snapshot de estado
                "PHASE_ALIGN"    # Re-calibración de fase
            ])
            cost = random.randint(5, 20)  # Costo energético teórico (Joules)
            self.task_queue.append({
                "id": task_id, 
                "type": task_type, 
                "cost": cost,
                "arrival_time": self.t
            })

    def calculate_resonance(self, t):
        """
        Calcula la apertura del Portal (0.0 a 1.0).
        
        Basado en las ecuaciones de EXP-028:
        - Bio: Ciclo de 17s
        - Crystal: Ciclo de 4.25s (17/4)
        - Venus: Ciclo de 16.18s (Phi)
        
        Retorna: Alineación promedio en rango [-1, 1]
        """
        # Las 5 Frecuencias Maestras
        bio   = math.sin((2 * math.pi * t) / 17.0)
        crys  = math.sin((2 * math.pi * t) / 4.25)
        venus = math.sin((2 * math.pi * t) / 16.18)
        
        # Alineación promedio (simplificado - EXP-028 usa threshold individual)
        alignment = (bio + crys + venus) / 3.0
        return alignment

    def execute_batch(self, max_tasks=3):
        """
        Ejecuta un batch de tareas durante un portal abierto.
        
        Returns: (executed_tasks, energy_used, energy_saved)
        """
        executed = []
        energy_batch = 0
        
        actual_executed = min(max_tasks, len(self.task_queue))
        
        for _ in range(actual_executed):
            task = self.task_queue.popleft()
            executed.append(task['type'])
            energy_batch += task['cost']
        
        # Ahorro energético: 
        # En portal (superconductor): E
        # Fuera de portal (resistivo): 3E
        # Ahorro = 2E
        savings = energy_batch * 2
        
        return executed, energy_batch, savings

    def run(self, duration=68.0):
        """
        Ejecuta el scheduler por `duration` segundos (default: 1 ciclo Quantum Leap).
        """
        print("=" * 80)
        print(f"{'TIME':<8} | {'PORTAL STATUS':<25} | {'QUEUE':<12} | {'ACTION'}")
        print("=" * 80)

        end_time = duration
        
        try:
            while self.t < end_time:
                self.t += self.dt
                self.add_random_tasks()
                
                # 1. Calcular Estado del Portal
                resonance = self.calculate_resonance(self.t)
                is_open = resonance > 0.75  # Umbral de apertura (75% de convergencia)
                
                # 2. Visualización de Estado
                q_len = len(self.task_queue)
                status_bar = "█" * int((resonance + 1) * 5)
                
                if is_open:
                    status_str = f"{C_OPEN}OPEN  {status_bar:<10} {resonance:+.2f}{C_RESET}"
                else:
                    status_str = f"{C_WAIT}CLOSE {status_bar:<10} {resonance:+.2f}{C_RESET}"

                # 3. Lógica de Ejecución (Adiabatic)
                action_msg = ""
                
                if is_open and q_len > 0:
                    # ¡PORTAL ABIERTO! EJECUTAR TAREAS (BATCH)
                    executed, energy, savings = self.execute_batch(max_tasks=3)
                    
                    self.total_energy_saved += savings
                    self.tasks_executed_in_portal += len(executed)
                    
                    action_msg = f"{C_EXEC} >>> EXECUTING: {', '.join(executed)} {C_RESET}"
                
                elif q_len > 10:
                    # CRÍTICO: La cola es muy larga, forzamos ejecución ineficiente
                    # para evitar desbordamiento de memoria.
                    task = self.task_queue.popleft()
                    penalty = task['cost'] * 2  # Penalización 3x - 1x = 2x extra
                    self.total_energy_saved -= penalty
                    self.tasks_forced_outside += 1
                    
                    action_msg = f"{C_WARN} [FORCED] Overflow Prevent: {task['type']} (-{penalty}J){C_RESET}"
                
                elif q_len == 0 and is_open:
                    action_msg = f"{C_OPEN} [IDLE] Portal open, no tasks - ZPE sync {C_RESET}"
                
                elif q_len > 0:
                    action_msg = f"{C_WAIT} [WAITING] Portal closed, {q_len} tasks queued...{C_RESET}"

                # 4. Render
                q_visual = f"[{'#' * min(q_len, 10):<10}]{q_len:>3}"
                print(f"T={self.t:05.1f} | {status_str} | {q_visual} | {action_msg}")
                
                # HUD Ahorro de Energía (cada 5s)
                if abs(self.t % 5.0) < self.dt:
                    efficiency = (self.tasks_executed_in_portal / 
                                 max(1, self.tasks_executed_in_portal + self.tasks_forced_outside) * 100)
                    print(f"      💡 ADIABATIC SAVINGS: {self.total_energy_saved:>6.0f}J | "
                          f"Efficiency: {efficiency:.1f}% portal-locked")

                time.sleep(0.08)  # Velocidad de visualización

        except KeyboardInterrupt:
            print("\n🛑 Scheduler Stopped (User Interrupt).")
        
        # Estadísticas finales
        print("\n" + "=" * 80)
        print("📊 QUANTUM SCHEDULER STATISTICS")
        print("=" * 80)
        print(f"Total Runtime:               {self.t:.1f}s")
        print(f"Tasks Executed in Portal:    {self.tasks_executed_in_portal}")
        print(f"Tasks Forced (Overflow):     {self.tasks_forced_outside}")
        print(f"Total Energy Saved:          {self.total_energy_saved:.0f}J")
        
        total_tasks = self.tasks_executed_in_portal + self.tasks_forced_outside
        if total_tasks > 0:
            efficiency = (self.tasks_executed_in_portal / total_tasks) * 100
            print(f"Portal-Lock Efficiency:      {efficiency:.1f}%")
            
            if efficiency > 80:
                print("\n✅ EXCELLENT - System is highly phase-locked!")
            elif efficiency > 60:
                print("\n⚠️  MODERATE - Consider increasing task queue capacity")
            else:
                print("\n❌ POOR - Tasks are executing out of phase (thermal waste)")
        
        print("\n💡 INTERPRETATION:")
        print("   Positive savings = System respects portals (Adiabatic)")
        print("   Negative savings = System forced execution (Resistive/Hot)")

if __name__ == "__main__":
    print("\n🔬 QUANTUM SCHEDULER DAEMON")
    print("   Proof-of-Concept: Bio-Adiabatic Task Orchestration")
    print("   Based on EXP-028 (Penta-Resonance Portal Detection)\n")
    
    scheduler = QuantumScheduler()
    scheduler.run(duration=68.0)  # 1 ciclo Quantum Leap completo
