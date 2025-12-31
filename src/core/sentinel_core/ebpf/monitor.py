import sys
import time
import json
from ..config import TRACE_PIPE_PATH
from .map_manager import MapManager
from ..brain.inference import SentinelBrain
from ..memory.ca3_generator import CA3Generator
from ..memory.ca1_selector import memory_selector
from ..brain.bci_controller import bci_controller
from ..brain.snn_core import GeneticImmunitySystem
from ..memory.chromadb_storage import memory_vault

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
        self.generator = CA3Generator()
        self.selector = memory_selector
        self.snn = GeneticImmunitySystem()
        self.memory_vault = memory_vault
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
        # 0. Alerta Sensorial Inmediata (Qualia)
        residue = hash(filename) % 60
        bci_controller.trigger_qualia("KERNEL_BLOCK")
        bci_controller.play_base60_pattern(residue)
        
        # 1. Consultar al Cerebro (IA) con contexto Base-60
        brain_result = self.brain.analyze_threat(filename, residue=residue)
        should_allow = brain_result["allow"]
        threat_score = brain_result["score"]
        
        if should_allow:
            # 2. Actualizar el Kernel si la IA aprueba
            success = self.map_manager.whitelist_binary(filename)
            if success:
                print(f"✅ [Kernel] Whitelist actualizada para: {filename}")
                bci_controller.trigger_qualia("SYSTEM_SECURE")
            else:
                print(f"❌ [Kernel] Fallo al actualizar whitelist para: {filename}")
        else:
            print(f"🚫 [Monitor] Bloqueo CONFIRMADO por IA para: {filename} (Score: {threat_score})")
            if threat_score > 0.8:
                bci_controller.trigger_qualia("THREAT_HIGH")
            
            # Phase 3: SNN Synaptic Reaction (Akashic Loop)
            # stimulus_result = SPIKE or LEAK
            stimulus_result = self.snn.process_stimulus(filename, threat_score * 100, residue)
            
            if stimulus_result == "SPIKE":
                id_hash = hash(filename)
                # Store Genetic Lineage
                self.memory_vault.store_lineage(
                    child_pid=0, # TODO: extract from log
                    parent_pid=0,
                    lineage_hash=id_hash,
                    metadata={"filename": filename, "score": threat_score, "type": "AKASHIC_SPIKE"}
                )
                bci_controller.trigger_qualia("SYNAPTIC_SPIKE")
                print(f"🧬 [SNN] IMMUNE RESPONSE TRIGGERED for {filename}")
            
        print(f"🧠 [Monitor] Generando escenario de memoria para: {filename}...")
        incident = {
            "id": int(time.time() * 1000),
            "event_type": "KERNEL_BLOCK",
            "filename": filename,
            "ai_decision": "ALLOW" if should_allow else "BLOCK",
            "threat_score": threat_score,
            "classification": brain_result["classification"]
        }
        
        try:
            scenarios = self.generator.generate_scenarios(incident)
            best = self.selector.select_best_scenario(scenarios, residue)
            self.selector.record_decision(incident, residue, best)
            print(f"✅ [Memory] Decisión registrada en Zona Armónica {residue}")
        except Exception as e:
            print(f"⚠️ [Memory] Error registrando memoria: {e}")
