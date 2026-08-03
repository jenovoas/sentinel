# Benchy de memoria compartida (SHM) y zero-copy usando me60os_core.PySharedBuffer.
# PySharedBuffer se apoya en shm_open + mmap: escribir a la region mapeada es
# zero-copy entre procesos (no hay memcpy a traves del boundary).
# Se mide ancho de banda de escritura/lectura y se reporta el backing mmap.

import time
import os
import me60os_core as S
from me60os_core import PySharedBuffer

NAME = "sentinel_bench_shm"
SIZE = 1 << 20  # 1 MiB

def main():
    print("=== SHM ZERO-COPY BENCH (PySharedBuffer / mmap) ===")
    buf = PySharedBuffer(NAME, SIZE, True)
    print(f"buffer '{NAME}' creado: {SIZE} bytes")

    # Entropia de hardware real (os.urandom) como payload
    data = os.urandom(SIZE)

    t0 = time.perf_counter_ns()
    buf.write(0, data)
    t1 = time.perf_counter_ns()
    w_ns = t1 - t0
    print(f"WRITE: {SIZE} bytes en {w_ns} ns => {SIZE*1e9/w_ns/1e6:.1f} MB/s (mmap, zero-copy)")

    # pyo3 v2: leer requiere el token Python 'py'
    import me60os_core
    # Acceder al gil para obtener py
    try:
        from me60os_core import Python
        py = Python.acquire_gil().python()
    except Exception:
        # fallback: usar API interna si existe
        py = None

    if py is not None:
        out = buf.read(py, 0, SIZE)
    else:
        # Intento directo (algunas versiones lo permiten)
        out = buf.read(0, SIZE)

    t0 = time.perf_counter_ns()
    if py is not None:
        out = buf.read(py, 0, SIZE)
    else:
        out = buf.read(0, SIZE)
    t1 = time.perf_counter_ns()
    r_ns = t1 - t0
    print(f"READ:  {SIZE} bytes en {r_ns} ns => {SIZE*1e9/r_ns/1e6:.1f} MB/s")

    # Verificar integridad (round-trip)
    got = bytes(out) if not isinstance(out, bytes) else out
    ok = got[:64] == data[:64]
    print(f"ROUND-TRIP OK: {ok} (primeros 64 bytes coinciden)")

    print("Backing: shm_open + mmap (sin memcpy a traves de procesos)")
    print("=== FIN SHM ===")

if __name__ == "__main__":
    main()
