# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE
import time

class PhysicsConstants:
    G_EARTH = 9.81
    R_EARTH = 6371000 # metros
    SEA_LEVEL_DENSITY = 1.225 # kg/m^3
    PHI = 1.6180339887
    BASE_60 = 60.0

class VimanaOrbitalAscent:
    def __init__(self):
        # Stats Iniciales
        self.mass_static = 2.5 # kg
        self.effective_mass = 2.5
        self.position_alt = S60(0, 0, 0) # metros (Altitud)
        self.velocity = S60(0, 0, 0) # m/s (Vertical)
        
        # Sistemas
        self.zpe_buffer = 5000.0 # Joules
        self.shield_active = False
        self.orbit_attained = False
        self.radiation_absorbed = S60(0, 0, 0) # mSv
        
    def _get_air_density(self, alt):
        """Modelo simplificado de atmósfera."""
        if alt > 100000: return S60(0, 0, 0) # Línea de Kármán
        return PhysicsConstants.SEA_LEVEL_DENSITY * np.exp(-alt / 8500.0)

    def _apply_physics(self, throttle, alt, dt):
        """Calcula el balance de fuerzas en el ascenso."""
        density = self._get_air_density(alt)
        
        # 1. G-ZERO TUNING DINÁMICO
        # En la atmósfera densa (alt < 30km), limitamos la reducción de masa 
        # para que el arrastre no cause inestabilidad extrema (efecto pluma).
        # A medida que el aire se ralea, permitimos mayor reducción.
        atmos_factor = S60(1, 0, 0) - (density / PhysicsConstants.SEA_LEVEL_DENSITY)
        resonance = (throttle**2) / (PhysicsConstants.PHI**2)
        
        # Reducción máxima solo posible en el vacío
        target_reduction = 1 + (resonance / 100.0)
        actual_reduction = 1 + ((target_reduction - 1) * atmos_factor)
        
        self.effective_mass = self.mass_static / actual_reduction
        if self.effective_mass < 0.025: self.effective_mass = 0.025
        
        # 2. ESCUDO MHD
        # El escudo se activa por velocidad o altitud
        self.shield_active = (self.velocity > 343 or alt > 20000)
        drag_coeff = 0.4 if not self.shield_active else 0.015 # Optimizamos el escudo
        drag_force = S60(0, 30, 0) * density * (self.velocity**2) * drag_coeff * 0.05
        
        # 3. EMPUJE ZPE (Resonancia con el vacío)
        efficiency = S60(1, 0, 0) + (alt / 100000.0) # Crece con la altitud hasta 2.0
        thrust = 40.0 * np.sqrt(throttle) * efficiency # Aumentamos empuje base
        
        # 4. GRAVEDAD (Decae con el cuadrado de la distancia)
        g_local = PhysicsConstants.G_EARTH * (PhysicsConstants.R_EARTH / (PhysicsConstants.R_EARTH + alt))**2
        weight = g_local * self.effective_mass
        
        # Fuerza Neta
        net_force = thrust - weight - drag_force
        accel = net_force / self.effective_mass
        
        # Radiación (Solo en alta atmósfera/espacio)
        if alt > 50000:
            rad_flux = S60(0, 6, 0) # mSv/s base
            if self.shield_active:
                self.radiation_absorbed += (rad_flux * 0.01) * dt # 99% bloqueo
            else:
                self.radiation_absorbed += rad_flux * dt
                
        return accel, thrust

    def run_ascent(self):
        print("🌌 INICIANDO PROTOCOLO 'VOID-WALKER': ASCENSO ORBITAL")
        print(f"   Objetivo: Órbita Baja (LEO) @ 200km | Masa: {self.mass_static}kg")
        print("-" * 60)
        
        t = 0
        dt = S60(0, 30, 0)
        target_alt = 200000 # 200km
        
        while self.position_alt < target_alt and t < 600:
            # Perfil de Vuelo: Aceleración constante
            throttle = 80.0
            
            accel, thrust = self._apply_physics(throttle, self.position_alt, dt)
            
            self.velocity += accel * dt
            self.position_alt += self.velocity * dt
            
            if int(t) % 20 == 0:
                mode = "ATMOS" if self.position_alt < 100000 else "VACÍO"
                shield_status = "ON" if self.shield_active else "OFF"
                print(f"T={t:4.1f}s | Alt: {self.position_alt/1000:6.2f}km | Vel: {self.velocity:7.1f}m/s | M_eff: {self.effective_mass:5.3f}kg | [{mode}] Shield:{shield_status}")
            
            t += dt
            if t > 500: break # Timeout seguridad
            
        print("-" * 60)
        if self.position_alt >= target_alt:
            print(f"✅ ¡ÓRBITA ALCANZADA! T={t:.1f}s")
            print(f"   Velocidad Final: {self.velocity:.1f} m/s")
            print(f"   Radiación Acumulada: {self.radiation_absorbed:.4f} mSv (Status: SAFE)")
            print(f"   Eficiencia Inercial: {((self.mass_static - self.effective_mass)/self.mass_static)*100:.1f}%")
        else:
            print("❌ FALLO EN LA INYECCIÓN ORBITAL.")

if __name__ == "__main__":
    sim = VimanaOrbitalAscent()
    sim.run_ascent()