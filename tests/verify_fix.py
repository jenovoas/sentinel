# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import sys
from unittest.mock import MagicMock

# Mock numpy
sys.modules["numpy"] = MagicMock()

try:
    # We need to make sure the script can find 'quantum' if we import it as a module
    # or we can just execute it.
    import quantum.validate_prime_math as vpm
    print("Successfully imported quantum.validate_prime_math")
    print("Testing if S60 and SovereignLUT are present in the module...")
    assert hasattr(vpm, 'S60'), "S60 missing"
    assert hasattr(vpm, 'SovereignLUT'), "SovereignLUT missing"
    print("Verification successful!")
except Exception as e:
    print(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
