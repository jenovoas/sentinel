# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------


from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import numpy as np # PRECAUCIÓN: SOLO PARA I/O, NO CÁLCULO CORE

def base60_to_decimal(digits):
    res = 0
    for i, d in enumerate(digits):
        res += d * (60 ** (-i))
    return res

def decimal_to_base60(val, precision=5):
    digits = []
    integer_part = int(val)
    digits.append(integer_part)
    rem = val - integer_part
    for _ in range(precision):
        rem *= 60
        d = int(rem)
        digits.append(d)
        rem -= d
    return digits

# Plimpton 322 Rows (approx values for (c/a)^2)
# Row: (short_side, diagonal) -> long_side = sqrt(diag^2 - short^2)
plimpton_data = [
    (119, 169),     # 1
    (3367, 4825),   # 2
    (4601, 6649),   # 3
    (12709, 18541), # 4
    (65, 97),       # 5
    (319, 481),     # 6
    (2291, 3541),   # 7
    (799, 1249),    # 8
    (481, 769),     # 9
    (4961, 8161),   # 10
    (45, 75),       # 11
    (167, 197),     # 12 (Error in tablet, but corrected)
    (161, 289),     # 13
    (1771, 3229),   # 14
    (56, 106)       # 15
]

print("--- Plimpton 322 Analysis ---")
for i, (b, c) in enumerate(plimpton_data):
    # a^2 + b^2 = c^2 => a = sqrt(c^2 - b^2)
    a_sq = c**2 - b**2
    a = np.sqrt(a_sq)
    ratio_sq = (c/a)**2
    b60 = decimal_to_base60(ratio_sq)
    print(f"Row {i+1:2}: (c/a)^2 = {ratio_sq:.6f} -> Base60: {b60}")

# Check S60(153, 24, 0) resonance
print("\n--- S60(153, 24, 0) Resonance Check ---")
val = S60(153, 24, 0)
b60_val = decimal_to_base60(val/60) # Normalize by 60 for "state" tuning?
print(f"S60(153, 24, 0) / 60 = {val/60:.4f} -> Base60: {decimal_to_base60(val/60)}")
print(f"S60(153, 24, 0) in Base60: {decimal_to_base60(val)}")

# Check the user's ratio [9, 13, 22]
u_ratio = [9, 13, 22]
u_val = 9 + 13/60 + 22/3600
print(f"User ratio [9, 13, 22] = {u_val:.6f}")

# Check Plimpton Row 12 specifically (c/a)^2
b12, c12 = 167, 197 # Tablet says 167, but correction is often 1,3,0 (diag) and 1,20,0 (seq)
# Let's use corrected values for Row 12: a=120, b=120*tan(theta)? No.
# Row 12: (sec^2) value is 1.22... or 1.53...?
# Row 12 in tablet: 1;35,10,02,28,27,24,26,40. That's approx 1.586.
# Row 13 in tablet: 1;33,45. That's 1.5625.
# Row 14 in tablet: 1;32,15...
# Row 15 in tablet: 1;23...