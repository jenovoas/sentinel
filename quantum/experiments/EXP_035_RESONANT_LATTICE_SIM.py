#!/usr/bin/env python3
#
# EXPERIMENT 035: Resonant Memory (Liquid Lattice) Simulation
#
# Objetivo:
# Simular una versión simplificada de la Resonant Memory, demostrando la
# propagación de fase y la coherencia de la red sin usar aritmética de
# punto flotante, en cumplimiento con el Axioma YATRA.
#
# Principios de RESEARCH.md aplicados:
# - Aritmética de punto fijo para cálculos de fase.
# - Simulación de un sistema de cristales resonantes.
#

import matplotlib.pyplot as plt
import numpy as np # Usado solo para std dev y visualización, no para la lógica de simulación.

# --- Simulación de Aritmética de Punto Fijo (Fixed-Point) ---
# En lugar de floats (0 a 2*PI), usamos enteros (0 a MAX_PHASE)
# Esto evita errores de redondeo y cumple con YATRA.
MAX_PHASE = 36000  # Representa 360 grados (360 * 100)

def s60_add(phase1, phase2):
    """Suma de fases con wrap-around."""
    return (phase1 + phase2) % MAX_PHASE

def s60_diff(phase1, phase2):
    """Diferencia angular más corta entre dos fases."""
    diff = (phase2 - phase1 + MAX_PHASE) % MAX_PHASE
    if diff > MAX_PHASE // 2:
        return diff - MAX_PHASE
    return diff

class ResonantCrystal:
    """
    Representa un único cristal en la red.
    Tiene una fase y una amplitud, y su estado evoluciona
    basándose en sus vecinos para buscar la coherencia.
    """
    def __init__(self, initial_phase=0, initial_amplitude=100):
        # Fase representada como entero (punto fijo)
        self.phase = initial_phase
        # Amplitud como entero (0-100)
        self.amplitude = initial_amplitude
        self.coupling_factor = 50  # Cuán fuertemente se acopla a los vecinos (de 1000)

    def calculate_next_phase(self, current_phase, neighbor_phases):
        """
        Calcula la nueva fase del cristal para el siguiente paso de tiempo.
        La lógica es determinista y se basa únicamente en los estados de entrada.
        """
        if not neighbor_phases:
            return current_phase

        # Calcular la diferencia de fase promedio con los vecinos
        total_phase_diff = 0
        for neighbor_phase in neighbor_phases:
            total_phase_diff += s60_diff(current_phase, neighbor_phase)
        
        avg_phase_diff = total_phase_diff // len(neighbor_phases)

        # Ajustar la fase propia para acercarse a la de los vecinos
        # El ajuste es proporcional al factor de acoplamiento.
        adjustment = (avg_phase_diff * self.coupling_factor) // 1000
        return s60_add(current_phase, adjustment)

    def __repr__(self):
        return f"Crystal(P:{self.phase}, A:{self.amplitude})"

class LiquidLattice:
    """
    Representa la red (lattice) de cristales resonantes.
    Orquesta la simulación y mide la coherencia.
    """
    def __init__(self, num_crystals=10):
        self.crystals = [ResonantCrystal() for _ in range(num_crystals)]

    def step(self):
        """Simula un paso de tiempo en la red."""
        # 1. Tomar una instantánea del estado actual (fundamental para la simulación correcta)
        old_phases = [c.phase for c in self.crystals]
        new_phases = [0] * len(self.crystals)

        # 2. Calcular todas las nuevas fases basándose únicamente en el estado anterior
        for i, crystal in enumerate(self.crystals):
            # Los vecinos son el cristal anterior y el siguiente en la red (circular)
            prev_neighbor_phase = old_phases[(i - 1 + len(old_phases)) % len(old_phases)]
            next_neighbor_phase = old_phases[(i + 1) % len(old_phases)]
            new_phases[i] = crystal.calculate_next_phase(old_phases[i], [prev_neighbor_phase, next_neighbor_phase])

        # 3. Aplicar el nuevo estado a toda la red de forma atómica
        for i, crystal in enumerate(self.crystals):
            crystal.phase = new_phases[i]

    def get_coherence(self):
        """
        Calcula la coherencia de la red.
        Una coherencia alta significa que todas las fases son similares.
        Se define como la inversa de la desviación estándar de las fases.
        """
        phases = [c.phase for c in self.crystals]
        # Usamos numpy aquí solo para el cálculo estadístico, no para la simulación.
        std_dev = np.std(phases)
        # Evitar división por cero. Si la desviación es cero, la coherencia es máxima.
        if std_dev == 0:
            return 1.0
        # Normalizamos para que el valor esté entre 0 y 1.
        return 1.0 - (std_dev / (MAX_PHASE / 2))

    def perturb(self, crystal_index, phase_change):
        """Introduce una perturbación en un cristal."""
        print(f"⚡ Perturbando cristal {crystal_index} con un cambio de fase de {phase_change}...")
        self.crystals[crystal_index].phase = s60_add(self.crystals[crystal_index].phase, phase_change)

def run_simulation():
    """
    Ejecuta la simulación completa y genera la visualización.
    """
    print("🚀 Iniciando simulación de Resonant Memory (Liquid Lattice)...")
    
    lattice = LiquidLattice(num_crystals=10)
    num_steps = 100
    coherence_history = []
    phase_history = []

    # 1. Simular estado inicial estable
    print("Estabilizando la red...")
    for _ in range(20):
        lattice.step()

    # 2. Introducir una perturbación
    lattice.perturb(crystal_index=5, phase_change=MAX_PHASE // 4) # Perturbación de 90 grados

    # 3. Simular la propagación y recuperación
    print("Simulando propagación de la perturbación...")
    for i in range(num_steps):
        coherence_history.append(lattice.get_coherence())
        lattice.step()
        phase_history.append([c.phase for c in lattice.crystals])
        if i % 10 == 0:
            print(f"  Paso {i}: Coherencia = {coherence_history[-1]:.3f}")

    print("✅ Simulación completada.")

    # 4. Visualizar los resultados
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(coherence_history, color='cyan', marker='o', markersize=4, linestyle='-')
    
    ax.set_title("Evolución de la Coherencia de la Red (Liquid Lattice)", fontsize=16, color='white')
    ax.set_xlabel("Pasos de Simulación", fontsize=12, color='gray')
    ax.set_ylabel("Nivel de Coherencia (0=Caos, 1=Perfecta)", fontsize=12, color='gray')
    
    ax.set_ylim(0, 1.1)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    
    # Marcar el punto de perturbación
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Perturbación Introducida')
    
    ax.legend()
    fig.tight_layout()
    
    # Guardar la visualización
    output_path = "resonant_lattice_coherence.png"
    plt.savefig(output_path)
    print(f"📈 Gráfico guardado en: {output_path}")

    # 5. Visualizar la fase de cada cristal a lo largo del tiempo (NUEVO)
    fig2, ax2 = plt.subplots(figsize=(12, 7))

    # Transponemos los datos para que el tiempo esté en el eje X
    phase_history_np = np.array(phase_history).T

    im = ax2.imshow(phase_history_np, aspect='auto', cmap='twilight_shifted', interpolation='nearest')

    ax2.set_title("Evolución de la Fase de Cada Cristal en el Tiempo", fontsize=16, color='white')
    ax2.set_xlabel("Pasos de Simulación", fontsize=12, color='gray')
    ax2.set_ylabel("Índice del Cristal", fontsize=12, color='gray')

    # Añadir una barra de color para la fase
    cbar = fig2.colorbar(im, ax=ax2)
    cbar.set_label('Fase (0 a 36000)', color='gray')
    cbar.ax.yaxis.set_tick_params(color='gray')
    plt.setp(plt.getp(cbar.ax.yaxis, 'ticklabels'), color='gray')

    fig2.tight_layout()

    output_path_phases = "resonant_lattice_phases.png"
    plt.savefig(output_path_phases)
    print(f"📈 Gráfico de fases guardado en: {output_path_phases}")

if __name__ == "__main__":
    run_simulation()
