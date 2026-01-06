from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import subprocess
from ..config import BPF_MAP_PATH

class MapManager:
    """
    Gestor de Mapas eBPF.
    Se encarga de la interacción de bajo nivel con el Kernel (bpftool)
    para actualizar las listas blancas y negras dinámicas.
    """

    def __init__(self):
        self.map_path = BPF_MAP_PATH

    def _string_to_hex(self, s: str) -> str:
        """Convierte un string a formato hex separado por espacios para bpftool."""
        return " ".join("{:02x}".format(ord(c)) for c in s) + " 00"

    def whitelist_binary(self, filename: str) -> bool:
        """
        Añade un binario a la whitelist del Kernel.

        Args:
            filename (str): Ruta completa del binario.

        Returns:
            bool: True si la operación fue exitosa.
        """
        # Preparar la clave en hexadecimal (padding a 256 bytes)
        hex_key = self._string_to_hex(filename)
        current_len = len(filename) + 1
        padding = " 00" * (256 - current_len)
        full_hex_key = hex_key + padding
        
        # Comando para actualizar el mapa Pinned
        cmd = [
            "sudo", "bpftool", "map", "update", "pinned", self.map_path,
            "key", "hex", *full_hex_key.split(),
            "value", "hex", "01" # 1 = Allowed
        ]
        
        try:
            # print(f"DEBUG: Running cmd: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            print(f"❌ [MapManager] Error actualizando mapa para {filename}: {error_msg}")
            return False
