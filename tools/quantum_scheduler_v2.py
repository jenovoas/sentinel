#!/usr/bin/env python3
# 🛡️ ME-60OS: QUANTUM SCHEDULER V2 (YATRA S60 PURO) 🛡️
# -----------------------------------------------------------------------------
# ORQUESTADOR DE TAREAS ADIABÁTICO - VERSIÓN S60 (ZERO DECIMAL)
# "Surfea la ola con máxima eficiencia - No desperdicies ni un Joule"
# -----------------------------------------------------------------------------

import time
import random
import sys
import os
from collections import deque

# Añadir me-60os al path para importar quantum.s60_fixedpoint
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'me-60os'))
from quantum.s60_fixedpoint import S60
from quantum.s60_math import S60Math

# --- CONFIGURACIÓN VISUAL ---
C_WAIT = "\033[90m"   # Gris (Dormido)
C_OPEN = "\033[92m"   # Verde (Portal Abierto)
C_WARN = "\033[93m"   # Amarillo (Cola creciendo)
C_EXEC = "\033[97m\033[42m" # Fondo Verde (Ejecutando)
C_FLUSH = "\033[97m\033[45m" # Fondo Magenta (Pre-flush)
C_RESET = "\033[0m"

class QuantumSchedulerV2:
    """
    Scheduler optimizado S60 Puro (YATRA LOCK).
    """
    
    def __init__(self):
        self.task_queue = deque()
        self.t = S60(0)
        self.dt = S60(0, 6, 0, 0, 0)  # 0.1 en base 60 (6/60)
        self.total_energy_saved = S60(0)
        self.tasks_executed_in_portal = 0
        self.tasks_forced_outside = 0
        self.tasks_pre_flushed = 0
        
        self.OVERFLOW_LIMIT = 20
        self.PRE_FLUSH_TIME = S60(60)
        self.PRE_FLUSH_THRESHOLD = 12
        
        print("💎 QUANTUM SCHEDULER V2 [S60 PURE]: INITIALIZING")
        print("   🔧 OPTIMIZATIONS ENABLED:")
        print(f"      - Overflow Limit: {self.OVERFLOW_LIMIT}")
        print(f"      - Pre-Flush: T={self.PRE_FLUSH_TIME}")

    def add_random_tasks(self):
        # 15% de probabilidad (usamos int puro para evitar random.random float)
        if random.randint(1, 100) <= 15:
            task_id = random.randint(1000, 9999)
            task_type = random.choice([
                "ZPE_TUNE", "BCI_SYNC", "LATTICE_GC", 
                "BACKUP_S60", "PHASE_ALIGN"
            ])
            cost = S60(random.randint(5, 20))
            self.task_queue.append({
                "id": task_id, 
                "type": task_type, 
                "cost": cost,
                "arrival_time": self.t
            })

    def calculate_resonance(self, t):
        """
        Calcula convergencia armónica (EXP-028) en S60 Puro.
        """
        dos_pi = S60(2) * S60Math.PI
        
        # 17.0 -> S60(17)
        bio_angle = (dos_pi * t) / S60(17)
        # 4.25 -> 4;15 (15/60 = 0.25)
        crys_angle = (dos_pi * t) / S60(4, 15, 0, 0, 0)
        # 16.18 -> 16;10,48
        venus_angle = (dos_pi * t) / S60(16, 10, 48, 0, 0)
        
        bio = S60Math.sin(bio_angle)
        crys = S60Math.sin(crys_angle)
        venus = S60Math.sin(venus_angle)
        
        alignment = (bio + crys + venus) / S60(3)
        return alignment

    def adaptive_batch_size(self, resonance):
        """
        Batch adaptativo basado en intensidad de portal (S60).
        """
        if resonance > S60(0, 54, 0, 0, 0):    # > 0.90
            return 5
        elif resonance > S60(0, 51, 0, 0, 0):  # > 0.85
            return 4
        elif resonance > S60(0, 48, 0, 0, 0):  # > 0.80
            return 3
        else:
            return 2

    def execute_batch(self, max_tasks):
        executed = []
        energy_batch = S60(0)
        actual_executed = min(max_tasks, len(self.task_queue))
        
        for _ in range(actual_executed):
            task = self.task_queue.popleft()
            executed.append(task['type'])
            energy_batch = energy_batch + task['cost']
        
        savings = energy_batch * S60(2)
        return executed, energy_batch, savings

    def pre_flush_check(self):
        # 0.5s = S60(0, 30, 0, 0, 0)
        diff = S60Math.abs(self.t - self.PRE_FLUSH_TIME)
        if diff < S60(0, 30, 0, 0, 0):
            q_len = len(self.task_queue)
            if q_len > self.PRE_FLUSH_THRESHOLD:
                num_to_flush = min(5, q_len - 10)
                flushed = []
                energy_used = S60(0)
                
                for _ in range(num_to_flush):
                    task = self.task_queue.popleft()
                    flushed.append(task['type'])
                    energy_used = energy_used + task['cost']
                
                # Penalización 1.5x -> energy * 3 / 2
                penalty = (energy_used * S60(3)) // 2
                self.total_energy_saved = self.total_energy_saved - penalty
                self.tasks_pre_flushed += num_to_flush
                return True, flushed, penalty
        
        return False, [], S60(0)

    def run(self, duration=68):
        print("=" * 90)
        print(f"{'TIME (S60)':<15} | {'PORTAL STATUS':<25} | {'QUEUE':<12} | {'ACTION'}")
        print("=" * 90)

        end_time = S60(duration)
        
        try:
            while self.t < end_time:
                self.t = self.t + self.dt
                self.add_random_tasks()
                
                resonance = self.calculate_resonance(self.t)
                is_open = resonance > S60(0, 45, 0, 0, 0) # 0.75
                
                q_len = len(self.task_queue)
                
                # Render: usar el valor raw de S60 para simular barra
                res_val = (resonance._value * 5) // S60.SCALE_0 + 5
                status_bar = "█" * max(0, int(res_val))
                
                res_str = f"S60[{resonance._value // S60.SCALE_0};{(abs(resonance._value) % S60.SCALE_0) // S60.SCALE_1:02d}]"
                
                if is_open:
                    status_str = f"{C_OPEN}OPEN  {status_bar:<10} {res_str}{C_RESET}"
                else:
                    status_str = f"{C_WAIT}CLOSE {status_bar:<10} {res_str}{C_RESET}"

                action_msg = ""
                
                did_flush, flushed, penalty = self.pre_flush_check()
                if did_flush:
                    action_msg = f"{C_FLUSH} [PRE-FLUSH]: {', '.join(flushed)} (-{penalty}){C_RESET}"
                elif is_open and q_len > 0:
                    batch_size = self.adaptive_batch_size(resonance)
                    executed, energy, savings = self.execute_batch(max_tasks=batch_size)
                    self.total_energy_saved = self.total_energy_saved + savings
                    self.tasks_executed_in_portal += len(executed)
                    intensity_marker = "🔥" if resonance > S60(0, 54, 0, 0, 0) else "✓"
                    action_msg = f"{C_EXEC} {intensity_marker} EXECUTING [{batch_size}]: {', '.join(executed)} {C_RESET}"
                elif q_len > self.OVERFLOW_LIMIT:
                    task = self.task_queue.popleft()
                    penalty = task['cost'] * S60(2)
                    self.total_energy_saved = self.total_energy_saved - penalty
                    self.tasks_forced_outside += 1
                    action_msg = f"{C_WARN} [OVERFLOW] Emergency: {task['type']} (-{penalty}){C_RESET}"
                elif q_len == 0 and is_open:
                    action_msg = f"{C_OPEN} [IDLE] Portal open, no tasks - ZPE sync {C_RESET}"
                elif q_len > 0:
                    progress = "⏳" if q_len > 15 else ""
                    action_msg = f"{C_WAIT} {progress} [WAITING] Portal closed, {q_len} tasks...{C_RESET}"

                q_visual = f"[{'#' * min(q_len, 10):<10}]{q_len:>3}"
                t_str = f"{self.t._value // S60.SCALE_0:02d};{(self.t._value % S60.SCALE_0) // S60.SCALE_1:02d}"
                print(f"T={t_str:<12} | {status_str} | {q_visual} | {action_msg}")
                
                if (self.t._value % (5 * S60.SCALE_0)) < self.dt._value:
                    total_tasks = self.tasks_executed_in_portal + self.tasks_forced_outside + self.tasks_pre_flushed
                    if total_tasks > 0:
                        efficiency = (self.tasks_executed_in_portal * 100) // total_tasks
                        print(f"      💡 SAVINGS: {self.total_energy_saved} | Efficiency: {efficiency}% | Pre-flush: {self.tasks_pre_flushed}")

                time.sleep(0.08)

        except KeyboardInterrupt:
            print("\n🛑 Scheduler Stopped.")
            
if __name__ == "__main__":
    scheduler = QuantumSchedulerV2()
    scheduler.run(duration=68)
