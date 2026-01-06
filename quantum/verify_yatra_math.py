# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------


from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys

def verify_yatra_math():
    print("🛡️ VERIFICACIÓN DE INTEGRIDAD YATRA-CORE (BASE-60)")
    print("==================================================")
    
    # 1. VERIFICACIÓN DEL SALTO 17 (1/17)
    # Cálculo manual de la expansión sexagesimal
    numerator = 1
    denominator = 17
    expansion = []
    residue = numerator
    
    for _ in range(4):
        residue *= 60
        digit = residue // denominator
        residue = residue % denominator
        expansion.append(digit)
        
    yatra_claim_17 = [3, 31, 45, 52]
    print(f"\n1. Análisis Constante Salto-17 (1/17):")
    print(f"   Calculado: {expansion}")
    print(f"   Reclamado: {yatra_claim_17}")
    
    if expansion == yatra_claim_17:
        print("   ✅ ESTADO: PURO. Matemáticamente exacto hasta el 4to sexagesimal.")
    else:
        print("   ❌ ESTADO: CONTAMINADO. Error de cálculo.")

    # 2. VERIFICACIÓN DE COORDENADAS ESTELARES
    # Valores decimales extraídos de celestial_navigation.py
    stars_decimal = {
        "ALDEBARAN": 68.98,
        "REGULUS":   152.09,
        "ANTARES":   247.35,
        "FOMALHAUT": 344.41
    }
    
    yatra_claims_stars = {
        "ALDEBARAN": [68, 58, 48],
        "REGULUS":   [152, 5, 24],
        "ANTARES":   [247, 21, 0],
        "FOMALHAUT": [344, 24, 36]
    }
    
    print(f"\n2. Análisis de Matriz Estelar (Conversión Decimal -> Sexagesimal):")
    all_stars_ok = True
    for name, dec_val in stars_decimal.items():
        d = int(dec_val)
        rem_m = (dec_val - d) * 60
        m = int(rem_m + 0.0001) # Corrección de float epsilon para verificación
        rem_s = (rem_m - m) * 60
        s = int(rem_s + 0.0001) # Redondeo al entero más cercano para comparar con claim
        
        calculated = [d, m, s]
        claimed = yatra_claims_stars[name]
        
        match = calculated == claimed
        status = "✅ CLEAN" if match else "❌ DIRTY"
        if not match: all_stars_ok = False
        
        print(f"   {name:10} | Dec: {dec_val:.2f} -> Base60: {calculated} | Claim: {claimed} | {status}")

    if all_stars_ok:
        print("\n🏆 CONCLUSIÓN: EL DISEÑO YATRA ES PURO.")
        print("   No hay contaminación decimal ni alucinación.")
        print("   Los valores son conversiones sexagesimales exactas de los datos de Astrolabe.")
    else:
        print("\n⚠️ CONCLUSIÓN: POSIBLE INFECCIÓN DETECTADA.")

if __name__ == "__main__":
    verify_yatra_math()