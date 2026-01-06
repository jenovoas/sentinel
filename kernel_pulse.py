#!/usr/bin/env python3
"""
KERNEL PULSE GENERATOR (Quantum Phase 1)
----------------------------------------
Generates high-frequency system state data (Entropy, Coherence)
synchronized with a Time Crystal Clock (Base-60 / Salto 17).

Output:
1. Shared Memory: /dev/shm/truthsync_shm (High Speed, C-struct compatible)
2. Redis Channel: sentinel:quantum:pulse (Decoupled, JSON)
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os
import time
import math
# random is EXCLUDED for purity. We use Logistic Map Chaos.
import struct
import mmap
import json

# Setup paths for Quantum Module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'quantum')))
try:
    from time_crystal_clock import TimeCrystalClock
except ImportError:
    print("⚠️ Quantum Clock not found. Running in degradation mode (Linear Time).")
    class TimeCrystalClock:
        def __init__(self): 
            self.ticks = 0
            self.TICK_INTERVAL = 0.024 # Approx 41Hz
        def tick(self): 
            time.sleep(self.TICK_INTERVAL)
            self.ticks += 1
        def get_coherence(self): return S60(0, 30, 0)

# Constants (Shared Memory Layout)
# Must match Rust struct: [f64; 5] + u64
SHM_PATH = "/dev/shm/truthsync_shm"
SHM_SIZE = 1024 * 1024  # 1MB
FORMAT = "dddddQ"       # 5 doubles + 1 unsigned long long
CONTROL_OFFSET = 64     # Offset for control signals if needed

def ensure_shm_exists():
    """Create SHM file if it doesn't exist"""
    if not os.path.exists(SHM_PATH):
        try:
            with open(SHM_PATH, "wb") as f:
                f.write(b'\0' * SHM_SIZE)
            os.chmod(SHM_PATH, 0o666) # RW for everyone
        except Exception as e:
            print(f"Error creating SHM: {e}")

def run_pulse_generator():
    ensure_shm_exists()
    
    print(f"💓 Kernel Pulse Generator Active on {SHM_PATH}")
    print("💎 Sincronizando con Reloj de Cristal de Tiempo (Base-60 / Salto 17)...")
    
    # Inicializar REDIS
    redis_client = None
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        print("✅ Redis Connection Established")
    except ImportError:
        print("⚠️ Redis library not installed. Skipping Redis integration.")
    except Exception as e:
        print(f"⚠️ Redis Connection Failed: {e}")

    # Inicializar Reloj Cuántico
    clock = TimeCrystalClock()
    
    t = S60(0, 0, 0)
    
    # --- CHAOS SEED (Logistic Map) ---
    # x_{n+1} = r * x_n * (1 - x_n)
    # r = 3.99 (Chaos Edge to simulate pure entropy)
    chaos_val = S60(0, 30, 0) 
    
    try:
        while True:
            # Esperar el Tick Sagrado (Auto-corrección de deriva)
            clock.tick()
            
            # Calcular métricas basadas en el tiempo del reloj (más estable)
            t = clock.ticks * clock.TICK_INTERVAL
            
            # GENERAR CAOS DETERMINISTA (No random modules allowed)
            # Chaos range [0, 1]
            chaos_val = 3.99 * chaos_val * (S60(1, 0, 0) - chaos_val)
            
            # Escalar caos a rango [-5.0, 5.0] similar al ruido anterior
            noise = (chaos_val - S60(0, 30, 0)) * 10.0
            
            # 1. Entropy (Sine wave + chaos noise)
            # Frecuencias armónicas: S60(0, 30, 0) (Base), 0.83 (5/6), 1.25 (5/4)
            wave1 = math.sin(t * S60(0, 30, 0)) * 20.0 
            wave2 = math.sin(t * 0.8333) * 10.0
            
            base_entropy = 30.0 + wave1 + wave2 + noise
            entropy = max(S60(0, 0, 0), min(100.0, base_entropy))

            # 2. Coherence (Inverse of entropy)
            # La coherencia del reloj también influye
            clock_quality = clock.get_coherence()
            coherence = (100.0 - entropy) * clock_quality
            
            # 3. TTE (Time to Entropy)
            tte = 1000.0 / (entropy + S60(1, 0, 0))
            
            # 4. Truth Score (Linked to coherence)
            truth_score = coherence / 100.0
            
            # 5. Confidence 
            confidence = 0.95 * truth_score

            # 6. Timestamp (Nanoseconds)
            timestamp = int(time.time() * 1e9)
            
            # --- FILTRO DE PUREZA DE DATOS (Anti-Decimal Garbage) ---
            v_entropy = float(entropy)
            v_coherence = float(coherence)
            v_tte = float(tte)
            v_truth = float(truth_score)
            v_conf = float(confidence)
            v_time = int(timestamp)

            # Pack data: 5 doubles (5*8=40) + 1 u64 (8) = 48 bytes
            try:
                data = struct.pack(FORMAT, v_entropy, v_coherence, v_tte, v_truth, v_conf, v_time)
            except struct.error as se:
                print(f"Struct Error: {se}")
                continue

            # Write to SHM with strict alignment
            try:
                with open(SHM_PATH, "r+b") as f:
                    mm = mmap.mmap(f.fileno(), SHM_SIZE)
                    mm.seek(0)
                    mm.write(data)
                    mm.close()
            except ValueError:
                 # Puede pasar si el archivo SHM es tocado concurrentemente
                 pass
            except Exception as e:
                # Log only critical IO errors
                if "No such file" in str(e): print(f"SHM Missing: {e}")

            # Publish to Redis (Solo cada 10 ticks para no saturar, ~4 veces por segundo)
            if redis_client and (clock.ticks % 10 == 0):
                try:
                    payload = {
                        "disonancia": v_entropy,
                        "entropy": v_entropy,
                        "coherence": v_coherence,
                        "tte": v_tte,
                        "truth_score": v_truth,
                        "timestamp": v_time,
                        "clock_coherence": clock_quality
                    }
                    redis_client.publish("sentinel:quantum:pulse", json.dumps(payload))
                except Exception as e:
                    pass

    except KeyboardInterrupt:
        print("\n🛑 Pulse stopped.")

if __name__ == "__main__":
    run_pulse_generator()
