#!/usr/bin/env python3
# 🛡️ ME-60OS: QUANTUM SCHEDULER V2 (OPTIMIZED) 🛡️
# -----------------------------------------------------------------------------
# ORQUESTADOR DE TAREAS ADIABÁTICO - VERSIÓN OPTIMIZADA
# "Surfea la ola con máxima eficiencia - No desperdicies ni un Joule"
# -----------------------------------------------------------------------------
# 🎯 OPTIMIZACIONES V2:
# 1. Tanque de Expansión: OVERFLOW_LIMIT = 20 (vs 10 en V1)
# 2. Inyección Variable: Batch adaptativo basado en intensidad de portal
# 3. Válvula de Alivio: Pre-flush a T=60s para evitar sobrecarga pre-Quantum Leap
# -----------------------------------------------------------------------------
# 🔬 OBJETIVO: Alcanzar >90% de eficiencia portal-locked
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
C_FLUSH = "\033[97m\033[45m" # Fondo Magenta (Pre-flush)
C_RESET = "\033[0m"

class QuantumSchedulerV2:
    """
    Scheduler optimizado que ejecuta tareas durante portales de convergencia armónica.
    
    Mejoras sobre V1:
    - Overflow limit aumentado (20 vs 10)
    - Batch size adaptativo basado en intensidad del portal
    - Pre-flush estratégico a T=60s para evitar sobrecarga pre-Quantum Leap
    """
    
    def __init__(self):
        self.task_queue = deque()
        self.t = 0.0
        self.dt = 0.1  # 10 Hz de muestreo
        self.total_energy_saved = 0.0
        self.tasks_executed_in_portal = 0
        self.tasks_forced_outside = 0
        self.tasks_pre_flushed = 0
        
        # V2 OPTIMIZATIONS
        self.OVERFLOW_LIMIT = 20  # ⬆️ Aumentado de 10 (Tanque de Expansión)
        self.PRE_FLUSH_TIME = 60.0  # Válvula de alivio a T=60s
        self.PRE_FLUSH_THRESHOLD = 12  # Si cola > 12 a T=60s, pre-flush
        
        print("💎 QUANTUM SCHEDULER V2: INITIALIZING")
        print("   🔧 OPTIMIZATIONS ENABLED:")
        print(f"      - Overflow Limit: {self.OVERFLOW_LIMIT} (was 10)")
        print(f"      - Adaptive Batch: 2-5 tasks (was fixed 3)")
        print(f"      - Pre-Flush: T={self.PRE_FLUSH_TIME}s threshold={self.PRE_FLUSH_THRESHOLD}")

    def add_random_tasks(self):
        """Simula procesos del OS pidiendo CPU."""
        if random.random() < 0.15:  # 15% prob por tick
            task_id = random.randint(1000, 9999)
            task_type = random.choice([
                "ZPE_TUNE", "BCI_SYNC", "LATTICE_GC", 
                "BACKUP_S60", "PHASE_ALIGN"
            ])
            cost = random.randint(5, 20)
            self.task_queue.append({
                "id": task_id, 
                "type": task_type, 
                "cost": cost,
                "arrival_time": self.t
            })

    def calculate_resonance(self, t):
        """
        Calcula convergencia armónica (EXP-028).
        Returns: Alignment in [-1, 1]
        """
        bio   = math.sin((2 * math.pi * t) / 17.0)
        crys  = math.sin((2 * math.pi * t) / 4.25)
        venus = math.sin((2 * math.pi * t) / 16.18)
        
        alignment = (bio + crys + venus) / 3.0
        return alignment

    def adaptive_batch_size(self, resonance):
        """
        🔧 OPTIMIZACIÓN V2: Batch adaptativo basado en intensidad de portal.
        
        Portal muy fuerte (>0.90): Inyectar 5 tareas (máximo throughput)
        Portal fuerte (>0.85): 4 tareas
        Portal normal (>0.80): 3 tareas
        Portal débil (0.75-0.80): 2 tareas (cauteloso)
        """
        if resonance > 0.90:
            return 5  # Portal muy ancho - inyección máxima
        elif resonance > 0.85:
            return 4
        elif resonance > 0.80:
            return 3
        else:  # 0.75 - 0.80
            return 2  # Portal débil - inyección cautelosa

    def execute_batch(self, max_tasks):
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
        
        # Ahorro: 2E por tarea (evitamos costo 3E fuera de portal)
        savings = energy_batch * 2
        
        return executed, energy_batch, savings

    def pre_flush_check(self):
        """
        🔧 OPTIMIZACIÓN V2: Válvula de Alivio Pre-Quantum Leap.
        
        A T=60s, si la cola es crítica (>12 tareas), ejecutamos un flush
        estratégico para evitar llegar a T=68s (Quantum Leap) sobrecargados.
        
        Esto es una ejecución "forzada" pero estratégica (menos penalización
        que un overflow de emergencia).
        """
        # Ventana: T=60.0s ± 0.5s
        if abs(self.t - self.PRE_FLUSH_TIME) < 0.5:
            q_len = len(self.task_queue)
            if q_len > self.PRE_FLUSH_THRESHOLD:
                # Pre-flush: ejecutar 3-5 tareas estratégicamente
                num_to_flush = min(5, q_len - 10)  # Dejar al menos 10 en cola
                
                flushed = []
                energy_used = 0
                
                for _ in range(num_to_flush):
                    task = self.task_queue.popleft()
                    flushed.append(task['type'])
                    energy_used += task['cost']
                
                # Penalización reducida (1.5E vs 2E de overflow)
                penalty = energy_used * 1.5
                self.total_energy_saved -= penalty
                self.tasks_pre_flushed += num_to_flush
                
                return True, flushed, penalty
        
        return False, [], 0

    def run(self, duration=68.0):
        """
        Ejecuta el scheduler V2 optimizado.
        """
        print("=" * 90)
        print(f"{'TIME':<8} | {'PORTAL STATUS':<25} | {'QUEUE':<12} | {'ACTION'}")
        print("=" * 90)

        end_time = duration
        
        try:
            while self.t < end_time:
                self.t += self.dt
                self.add_random_tasks()
                
                # 1. Calcular Estado del Portal
                resonance = self.calculate_resonance(self.t)
                is_open = resonance > 0.75
                
                # 2. Visualización de Estado
                q_len = len(self.task_queue)
                status_bar = "█" * int((resonance + 1) * 5)
                
                if is_open:
                    status_str = f"{C_OPEN}OPEN  {status_bar:<10} {resonance:+.2f}{C_RESET}"
                else:
                    status_str = f"{C_WAIT}CLOSE {status_bar:<10} {resonance:+.2f}{C_RESET}"

                # 3. LÓGICA DE EJECUCIÓN (V2 Optimizada)
                action_msg = ""
                
                # 3.1 PRE-FLUSH (Válvula de Alivio a T=60s)
                did_flush, flushed, penalty = self.pre_flush_check()
                if did_flush:
                    action_msg = f"{C_FLUSH} [PRE-FLUSH] T=60s: {', '.join(flushed)} (-{penalty:.0f}J){C_RESET}"
                
                # 3.2 PORTAL ABIERTO: Ejecución adaptativa
                elif is_open and q_len > 0:
                    # BATCH ADAPTATIVO basado en intensidad
                    batch_size = self.adaptive_batch_size(resonance)
                    executed, energy, savings = self.execute_batch(max_tasks=batch_size)
                    
                    self.total_energy_saved += savings
                    self.tasks_executed_in_portal += len(executed)
                    
                    intensity_marker = "🔥" if resonance > 0.90 else "✓"
                    action_msg = f"{C_EXEC} {intensity_marker} EXECUTING [{batch_size}]: {', '.join(executed)} {C_RESET}"
                
                # 3.3 OVERFLOW: Cola muy larga (Tanque de Expansión lleno)
                elif q_len > self.OVERFLOW_LIMIT:
                    task = self.task_queue.popleft()
                    penalty = task['cost'] * 2
                    self.total_energy_saved -= penalty
                    self.tasks_forced_outside += 1
                    
                    action_msg = f"{C_WARN} [OVERFLOW] Emergency: {task['type']} (-{penalty}J){C_RESET}"
                
                # 3.4 WAITING / IDLE
                elif q_len == 0 and is_open:
                    action_msg = f"{C_OPEN} [IDLE] Portal open, no tasks - ZPE sync {C_RESET}"
                
                elif q_len > 0:
                    progress = "⏳" if q_len > 15 else ""
                    action_msg = f"{C_WAIT} {progress} [WAITING] Portal closed, {q_len} tasks queued...{C_RESET}"

                # 4. Render
                q_visual = f"[{'#' * min(q_len, 10):<10}]{q_len:>3}"
                print(f"T={self.t:05.1f} | {status_str} | {q_visual} | {action_msg}")
                
                # HUD Ahorro de Energía (cada 5s)
                if abs(self.t % 5.0) < self.dt:
                    total_tasks = self.tasks_executed_in_portal + self.tasks_forced_outside + self.tasks_pre_flushed
                    if total_tasks > 0:
                        efficiency = (self.tasks_executed_in_portal / total_tasks) * 100
                        print(f"      💡 SAVINGS: {self.total_energy_saved:>6.0f}J | "
                              f"Efficiency: {efficiency:>5.1f}% | "
                              f"Pre-flush: {self.tasks_pre_flushed}")

                time.sleep(0.08)

        except KeyboardInterrupt:
            print("\n🛑 Scheduler Stopped (User Interrupt).")
        
        # Estadísticas finales
        self._print_statistics()

    def _print_statistics(self):
        """Imprime estadísticas finales detalladas."""
        print("\n" + "=" * 90)
        print("📊 QUANTUM SCHEDULER V2 - FINAL STATISTICS")
        print("=" * 90)
        print(f"Total Runtime:               {self.t:.1f}s")
        print(f"Tasks Executed in Portal:    {self.tasks_executed_in_portal} (OPTIMAL)")
        print(f"Tasks Pre-Flushed (T=60s):   {self.tasks_pre_flushed} (STRATEGIC)")
        print(f"Tasks Forced (Overflow):     {self.tasks_forced_outside} (PENALTY)")
        print(f"Total Tasks Processed:       {self.tasks_executed_in_portal + self.tasks_forced_outside + self.tasks_pre_flushed}")
        print(f"Total Energy Saved:          {self.total_energy_saved:.0f}J")
        
        total_tasks = self.tasks_executed_in_portal + self.tasks_forced_outside + self.tasks_pre_flushed
        if total_tasks > 0:
            portal_efficiency = (self.tasks_executed_in_portal / total_tasks) * 100
            strategic_rate = (self.tasks_pre_flushed / total_tasks) * 100
            emergency_rate = (self.tasks_forced_outside / total_tasks) * 100
            
            print(f"\nPortal-Lock Efficiency:      {portal_efficiency:.1f}%")
            print(f"Strategic Pre-Flush Rate:    {strategic_rate:.1f}%")
            print(f"Emergency Overflow Rate:     {emergency_rate:.1f}%")
            
            # Rating
            print("\n" + "=" * 90)
            if portal_efficiency > 90:
                print("✅ EXCELLENT - System is highly phase-locked! Target achieved!")
            elif portal_efficiency > 80:
                print("✅ VERY GOOD - System respects portals effectively")
            elif portal_efficiency > 70:
                print("⚠️  GOOD - Functional but room for improvement")
            elif portal_efficiency > 60:
                print("⚠️  MODERATE - Consider further tuning")
            else:
                print("❌ POOR - Significant thermal waste detected")
        
        # Comparación V1 vs V2
        print("\n📈 IMPROVEMENT OVER V1:")
        print("   V1 Efficiency: 65.3%")
        print(f"   V2 Efficiency: {portal_efficiency:.1f}%")
        print(f"   Delta: {portal_efficiency - 65.3:+.1f}%")
        
        print("\n💡 OPTIMIZATION IMPACT:")
        print(f"   - Tanque Expansión (20): Reduced overflow emergencies")
        print(f"   - Batch Adaptativo (2-5): Maximized portal utilization")
        print(f"   - Pre-Flush (T=60s): Strategic load balancing")

if __name__ == "__main__":
    print("\n🔬 QUANTUM SCHEDULER V2 (OPTIMIZED)")
    print("   Bio-Adiabatic Task Orchestration with Advanced Load Balancing")
    print("   Target: >90% Portal-Lock Efficiency\n")
    
    scheduler = QuantumSchedulerV2()
    scheduler.run(duration=68.0)
