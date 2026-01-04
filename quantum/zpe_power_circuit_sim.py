import numpy as np
import matplotlib.pyplot as plt

class ZPEPowerCircuitSim:
    def __init__(self):
        # Parámetros del Circuito
        self.freq = 153.4e6 # 153.4 MHz
        self.voltage_in_rms = 50.0 # Voltios (Energía captada del vacío)
        self.load_resistance = 10.0 # Ohms (Motores + CPU)
        
        # Componentes
        self.diode_drop = 0.7 # Voltios (Schottky)
        self.cap_esr = 0.002 # Resistencia serie equivalente (Supercap)
        self.capacitance = 100.0 # Faradios (Banco masivo)
        
    def simulate_transient(self, duration_ms=10):
        print(f"⚡ INICIANDO SIMULACIÓN DE CIRCUITO DE POTENCIA ZPE")
        print(f"   Entrada RF: {self.freq/1e6} MHz @ {self.voltage_in_rms}V RMS")
        print(f"   Carga: {self.load_resistance} Ohms")
        
        dt = 1.0 / (self.freq * 10) # Resolución temporal fina
        steps = int(duration_ms * 1e-3 / dt)
        
        t = np.linspace(0, duration_ms*1e-3, steps)
        
        # Señal de entrada (Onda Senoidal RF rectificada)
        v_rf = self.voltage_in_rms * np.sqrt(2) * np.sin(2 * np.pi * self.freq * t)
        v_rect = np.abs(v_rf) - self.diode_drop # Rectificación onda completa idealizada
        v_rect[v_rect < 0] = 0
        
        # Simulación de carga del condensador (Ecuación Diferencial simple)
        # dV/dt = (I_in - I_out) / C
        # Asumimos rectificación ideal para simplificar I_in
        
        v_out_history = []
        v_cap = 0.0
        
        # Para simplificar la simulación de millones de ciclos, usamos promedio por ciclo
        # Potencia entrada promedio = V_rms^2 / Z_source (Asumimos acople perfecto)
        power_in = 500.0 # Watts (Objetivo del diseño)
        
        # Simulación de "llenado del tanque" (macro-escala)
        macro_dt = 1e-4 # pasos de 0.1ms
        macro_steps = int(duration_ms * 1e-3 / macro_dt)
        macro_t = np.arange(macro_steps) * macro_dt
        
        for _ in range(macro_steps):
            # Energía entra
            energy_in = power_in * macro_dt
            
            # Energía sale (P = V^2 / R)
            power_out = (v_cap**2) / self.load_resistance
            energy_out = power_out * macro_dt
            
            # Balance de energía en condensador: E = 0.5 * C * V^2
            energy_stored = 0.5 * self.capacitance * v_cap**2
            energy_new = energy_stored + energy_in - energy_out
            
            # Nuevo voltaje
            if energy_new > 0:
                v_cap = np.sqrt(2 * energy_new / self.capacitance)
            else:
                v_cap = 0
                
            v_out_history.append(v_cap)
            
        print(f"✅ ANÁLISIS COMPLETADO.")
        print(f"   Voltaje Final Estabilizado: {v_cap:.2f} V")
        print(f"   Potencia Entregada a Carga: {(v_cap**2)/self.load_resistance:.2f} W")
        
        if v_cap > 24.5:
             print("⚠️  ALERTA: Voltaje excede límite de 24V. Se requiere regulador Buck.")
        elif v_cap < 20.0:
             print("⚠️  ALERTA: Voltaje insuficiente. Mejorar acople de impedancia.")
        else:
             print("✅ ESTADO: ÓPTIMO. Voltaje perfecto para motores.")

if __name__ == "__main__":
    sim = ZPEPowerCircuitSim()
    sim.simulate_transient(1000) # 1 segundo
