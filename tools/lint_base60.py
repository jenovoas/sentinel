#!/usr/bin/env python3
import re
import sys
import glob

# Patrones de "Grasa Decimal" prohibida
# Busca números decimales que NO sean parte de una división fracciónaria (ej: 1/60 es válido, 0.0166 no)
DECIMAL_PATTERN = re.compile(r'\b\d+\.\d+\b')

# Excepciones permitidas (versiones de librerías, IPs, constantes matemáticas puras comentadas)
WHITELIST = [
    "1.618", # PHI comentado
    "3.14159", # PI comentado
    "S60(0, 0, 0)", "S60(1, 0, 0)", # Identidades básicas
    "127.0.S60(0, 6, 0)" # IPs
]

def is_contaminated(line):
    # Ignorar comentarios
    if line.strip().startswith("#"): return False
    
    matches = DECIMAL_PATTERN.findall(line)
    for m in matches:
        if m in WHITELIST: continue
        # Si es un float simple (ej S60(0, 30, 0)), es sospechoso
        # Pero si está dentro de S60(...), podría ser válido (ej segundos).
        # Para ser estricto, reportamos todo float fuera de S60.
        if "S60" not in line and "time.sleep" not in line:
            return m
    return None

def scan_files():
    print("🛡️  INICIANDO ESCANEO DE PUREZA BASE-60...")
    files = glob.glob("quantum/**/*.py", recursive=True)
    contaminated_count = 0
    
    for f_path in files:
        if "sovereign_math.py" in f_path: continue # Ignorar el núcleo
        if "lint_base60.py" in f_path: continue
        
        with open(f_path, 'r') as f:
            lines = f.readlines()
            
        file_dirty = False
        for i, line in enumerate(lines):
            bad_token = is_contaminated(line)
            if bad_token:
                if not file_dirty:
                    print(f"\n📂 Archivo Contaminado: {f_path}")
                    file_dirty = True
                print(f"   ❌ Línea {i+1}: Uso de decimal impuro '{bad_token}' -> {line.strip()}")
                contaminated_count += 1

    if contaminated_count > 0:
        print(f"\n🚨 ALERTA: Se detectaron {contaminated_count} herejías decimales.")
        print("   Acción requerida: Reemplazar con S60(g, m, s) o fracciones 1/60.")
        sys.exit(1)
    else:
        print("\n✅ PUREZA VERIFICADA: El sistema está limpio de fricción decimal.")
        sys.exit(0)

if __name__ == "__main__":
    scan_files()
