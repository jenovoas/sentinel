import sys
from ..config import TRACE_PIPE_PATH
from .map_manager import MapManager
from ..brain.inference import SentinelBrain

class GuardianMonitor:
    """
    Monitor de Eventos del Kernel.
    Escucha el 'trace_pipe' del sistema para detectar eventos de bloqueo
    emitidos por el programa eBPF (Guardian Alpha).
    """

    def __init__(self):
        self.trace_pipe = TRACE_PIPE_PATH
        self.brain = SentinelBrain()
        self.map_manager = MapManager()
        self.is_running = False

    def start(self):
        """Inicia el ciclo de monitoreo infinito."""
        self.is_running = True
        print(f"📡 [Monitor] Escuchando eventos en: {self.trace_pipe}")
        
        try:
            # Abrir el pipe en modo lectura (bloqueante)
            with open(self.trace_pipe, "r", encoding="utf-8", errors="ignore") as f:
                while self.is_running:
                    line = f.readline()
                    if not line:
                        continue
                    
                    self._process_line(line)
                        
        except PermissionError:
            print("❌ [Monitor] Error: Se requieren permisos de root para leer trace_pipe.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n🛑 [Monitor] Deteniendo...")

    def _process_line(self, line: str):
        """Procesa una línea individual del log."""
        # Buscamos la firma de nuestro eBPF
        if "Guardian [BLOCK]" in line:
            # Formato esperado: ... bpf_trace_printk: Guardian [BLOCK]: Unknown binary ./safe_script.sh
            try:
                parts = line.split("Unknown binary ")
                if len(parts) > 1:
                    filename = parts[1].strip()
                    self._handle_block_event(filename)
            except Exception as e:
                print(f"⚠️ [Monitor] Error parseando línea: {e}")

    def _handle_block_event(self, filename: str):
        """Coordina la respuesta ante un evento de bloqueo."""
        # Limpiar el filename (a veces bpftool/printk añade basura al final)
        filename = filename.split('\0')[0].strip()
        print(f"🔍 [Monitor] Detectado bloqueo: {filename}")
        
        # 1. Consultar al Cerebro (IA)
        should_allow = self.brain.analyze_threat(filename)
        
        if should_allow:
            # 2. Actualizar el Kernel si la IA aprueba
            success = self.map_manager.whitelist_binary(filename)
            if success:
                print(f"✅ [Kernel] Whitelist actualizada para: {filename}")
            else:
                print(f"❌ [Kernel] Fallo al actualizar whitelist para: {filename}")
        else:
            print(f"🚫 [Monitor] Bloqueo CONFIRMADO por IA para: {filename}")
