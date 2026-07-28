# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import sys
import os
print(f"sys.path[0]: {sys.path[0]}")
try:
    import sovereign_math
    print("Imported sovereign_math")
except ImportError as e:
    print(f"Failed to import sovereign_math: {e}")
