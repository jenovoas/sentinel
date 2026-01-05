
import numpy as np
import math
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sovereign_math import S60, S60_from_float, SovereignLUT

omega_m = 2 * np.pi * 1e6
dt = 0.01 / 600000
theta = omega_m * dt
theta_deg = theta * 180.0 / np.pi
s60 = S60_from_float(theta_deg)

print(f"Theta (rad): {theta}")
print(f"Theta (deg): {theta_deg}")
print(f"S60: {s60}")

sin_lut, cos_lut = SovereignLUT.get_sin_cos(s60)
sin_np = np.sin(theta)
cos_np = np.cos(theta)

print(f"Sin LUT: {sin_lut}")
print(f"Sin NP:  {sin_np}")
print(f"Diff:    {sin_lut - sin_np}")

print(f"Unitary LUT: {sin_lut**2 + cos_lut**2}")
print(f"Unitary NP:  {sin_np**2 + cos_np**2}")
