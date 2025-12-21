#!/usr/bin/env python3
"""
Sentinel Haptic MVP - Siente Tu Servidor
=========================================

Proof of Concept: Telemetría háptica mediante conducción ósea

Convierte métricas de CPU en frecuencias audibles/vibratorias
para crear una interfaz de latencia cero cognitiva.

Powered by Google ❤️ & Perplexity 💜

Autor: Jaime Novoa
Fecha: 21 Diciembre 2025
"""

import psutil
import time
import numpy as np

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  sounddevice no instalado. Ejecuta: pip install sounddevice")
    print("   Modo simulación activado (sin audio real)\n")


class HapticSentinel:
    """
    Sentinel Háptico - Siente el estado de tu sistema
    
    Mapea métricas de sistema a frecuencias vibratorias
    para crear percepción directa del estado computacional.
    """
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        # Rangos de frecuencia (Hz)
        self.freq_min = 100   # CPU 0% - grave, relajado
        self.freq_max = 800   # CPU 100% - agudo, alerta
        
        # Duración de cada tono
        self.tone_duration = 0.1  # segundos
        
    def cpu_to_frequency(self, cpu_percent):
        """
        Mapea CPU% a frecuencia audible
        
        0% = 100Hz (grave, sistema relajado)
        100% = 800Hz (agudo, sistema bajo presión)
        """
        return self.freq_min + (cpu_percent * (self.freq_max - self.freq_min) / 100)
    
    def generate_tone(self, frequency):
        """Genera tono sinusoidal puro"""
        t = np.linspace(0, self.tone_duration, 
                       int(self.sample_rate * self.tone_duration))
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Fade in/out para evitar clicks
        fade_samples = int(0.01 * self.sample_rate)
        wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return wave
    
    def run(self, duration_seconds=60):
        """
        Ejecuta el sentinel háptico
        
        Args:
            duration_seconds: Cuánto tiempo ejecutar (0 = infinito)
        """
        print("="*70)
        print("SENTINEL HÁPTICO - SIENTE TU SERVIDOR")
        print("="*70)
        print("\nPowered by Google ❤️ & Perplexity 💜\n")
        
        if not AUDIO_AVAILABLE:
            print("Modo simulación (sin audio)")
        else:
            print("🎧 Ponte auriculares de conducción ósea")
            print("   (o auriculares normales en el pómulo)\n")
        
        print("Presiona Ctrl+C para detener\n")
        print("-"*70)
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                # Obtener CPU%
                cpu = psutil.cpu_percent(interval=0.1)
                
                # Convertir a frecuencia
                freq = self.cpu_to_frequency(cpu)
                
                # Generar y reproducir tono
                if AUDIO_AVAILABLE:
                    tone = self.generate_tone(freq)
                    sd.play(tone, self.sample_rate)
                    sd.wait()
                
                # Mostrar estado
                bar_length = int(cpu / 2)  # 50 chars max
                bar = "█" * bar_length + "░" * (50 - bar_length)
                
                print(f"CPU: {cpu:5.1f}% [{bar}] {freq:6.1f}Hz", end='\r')
                
                iteration += 1
                
                # Verificar duración
                if duration_seconds > 0:
                    elapsed = time.time() - start_time
                    if elapsed >= duration_seconds:
                        break
                
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("SENTINEL HÁPTICO DETENIDO")
            print("="*70)
            print(f"\nIteraciones: {iteration}")
            print(f"Tiempo: {time.time() - start_time:.1f}s")
            print("\n💡 ¿Sentiste el servidor? Eso es sustitución sensorial.")


def demo_stress_test():
    """Demo con stress test para ver cambios dramáticos"""
    print("\n🧪 DEMO: Stress Test")
    print("\nEjecutando carga CPU...")
    print("Deberías SENTIR cómo la frecuencia sube dramáticamente\n")
    
    sentinel = HapticSentinel()
    
    # Ejecutar por 10 segundos
    sentinel.run(duration_seconds=10)


if __name__ == '__main__':
    import sys
    
    print("\n" + "="*70)
    print("OPCIONES:")
    print("="*70)
    print("\n1. Monitoreo continuo (Ctrl+C para detener)")
    print("2. Demo con stress test (10 segundos)")
    print("\nElige: ", end='')
    
    try:
        choice = input().strip()
    except:
        choice = "1"
    
    sentinel = HapticSentinel()
    
    if choice == "2":
        demo_stress_test()
    else:
        print("\nIniciando monitoreo continuo...\n")
        sentinel.run(duration_seconds=0)
