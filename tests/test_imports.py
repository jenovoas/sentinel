import sys
import os
print(f"sys.path[0]: {sys.path[0]}")
try:
    from quantum import sovereign_math
    print("Imported quantum.sovereign_math successfully")
except ImportError:
    print("Failed to import quantum.sovereign_math")

try:
    sys.path.append(os.path.join(os.getcwd(), 'quantum'))
    import sovereign_math
    print("Imported sovereign_math from quantum/ successfully after appending to path")
except ImportError:
    print("Failed to import sovereign_math even after appending")
