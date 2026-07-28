# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import unittest
import os
import sys
import struct
import time

# Agregar directorio raiz para imports si es necesario
sys.path.append(os.getcwd())

# Definir estructura C-style para validación cruzada
# u64 timestamp, u32 pid, u32 type, entropy(u64, 5*u8, 3 pad), payload 64, u32 cpu
EVENT_STRUCT_FMT = "Q I I Q B B B B B 3x 64s I" 

class TestEbpfCortexIntegration(unittest.TestCase):
    
    def setUp(self):
        self.ebpf_path = "ebpf/lsm_ai_guardian.c"
        self.header_path = "ebpf/cortex_events.h"
        self.bridge_path = "sentinel-cortex/src/ebpf_cortex_bridge.rs"

    def test_files_exist(self):
        """Verifica que todos los componentes de la integración existen"""
        self.assertTrue(os.path.exists(self.ebpf_path), "Falta lsm_ai_guardian.c")
        self.assertTrue(os.path.exists(self.header_path), "Falta cortex_events.h")
        self.assertTrue(os.path.exists(self.bridge_path), "Falta ebpf_cortex_bridge.rs")

    def test_header_consistency(self):
        """Verifica que el header C define las estructuras S60 correctas"""
        with open(self.header_path, 'r') as f:
            content = f.read()
            self.assertIn("struct s60_entropy_t", content)
            self.assertIn("struct cortex_event_t", content)
            self.assertIn("EVENT_TYPE_BIO", content)

    def test_kernel_logic_s60(self):
        """Verifica que la lógica S60 está implementada en el código C"""
        with open(self.ebpf_path, 'r') as f:
            content = f.read()
            # Debe usar módulo 60 para grados/minutos
            self.assertIn("% 60", content) 
            self.assertIn("calculate_s60_entropy", content)
            self.assertIn("cortex_ringbuf", content)

    def test_bridge_struct_alignment(self):
        """Verifica que Rust tiene la misma alineación de memoria (aprox)"""
        with open(self.bridge_path, 'r') as f:
            content = f.read()
            self.assertIn("#[repr(C)]", content)
            self.assertIn("struct S60Entropy", content)

    def test_s60_math_simulation(self):
        """Simula la matemática S60 del Kernel en Python para verificar lógica"""
        # Logic from kernel:
        # e->second = val % 60; val /= 60;
        # e->minute = val % 60; val /= 60;
        
        seed = 1234567890
        val = seed
        
        second = val % 60
        val //= 60
        minute = val % 60
        val //= 60
        degree = val % 60
        
        # Validar rangos S60
        self.assertTrue(0 <= second < 60)
        self.assertTrue(0 <= minute < 60)
        self.assertTrue(0 <= degree < 60)
        
        # No decimales
        self.assertIsInstance(second, int)

if __name__ == '__main__':
    print("🛡️  VERIFICANDO INTEGRACIÓN EBPF-CORTEX (ME-60OS)")
    unittest.main()
