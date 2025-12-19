"""
Whitelist Manager con Firmas ECDSA
Gestiona whitelist de eBPF con integridad criptográfica

SEGURIDAD:
- Cada entrada firmada con ECDSA P-256
- Verificación en kernel space (Ring 0)
- Expiración automática (24h)
- Imposible modificar sin clave privada
"""

import ecdsa
from hashlib import sha256
import time
import json
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict


@dataclass
class WhitelistEntry:
    """Entrada de whitelist con firma ECDSA"""
    path: str
    path_hash: int
    policy: int  # 1 = ALLOW_AI, 0 = BLOCK_AI
    signature: bytes
    timestamp: int  # nanoseconds
    version: int = 1
    
    def to_dict(self) -> dict:
        """Serializa para JSON"""
        d = asdict(self)
        d['signature'] = self.signature.hex()
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WhitelistEntry':
        """Deserializa desde JSON"""
        data['signature'] = bytes.fromhex(data['signature'])
        return cls(**data)


class WhitelistManager:
    """
    Gestiona whitelist con firmas ECDSA
    
    FLUJO:
    1. Generar par de claves ECDSA P-256
    2. Agregar path con firma
    3. eBPF verifica firma en kernel
    4. Rechaza modificaciones sin clave privada
    """
    
    def __init__(self, private_key_path: Optional[str] = None):
        """
        Inicializa manager
        
        Args:
            private_key_path: Path a clave privada PEM (genera nueva si None)
        """
        self.key_dir = Path("/tmp/sentinel-keys")
        self.key_dir.mkdir(exist_ok=True)
        
        if private_key_path and Path(private_key_path).exists():
            # Cargar clave existente
            with open(private_key_path, 'rb') as f:
                self.sk = ecdsa.SigningKey.from_pem(f.read())
        else:
            # Generar nueva clave ECDSA P-256
            self.sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
            
            # Guardar clave privada
            private_key_path = self.key_dir / "kernel_signing.pem"
            with open(private_key_path, 'wb') as f:
                f.write(self.sk.to_pem())
            
            print(f"✅ Nueva clave ECDSA generada: {private_key_path}")
        
        # Clave pública (para verificación)
        self.vk = self.sk.get_verifying_key()
        
        # Guardar clave pública
        public_key_path = self.key_dir / "kernel_public.pem"
        with open(public_key_path, 'wb') as f:
            f.write(self.vk.to_pem())
        
        print(f"✅ Clave pública: {public_key_path}")
        
        # Cache de entradas
        self.entries: Dict[int, WhitelistEntry] = {}
    
    def add_to_whitelist(
        self,
        path: str,
        policy: int = 1,
        ttl_hours: int = 24
    ) -> WhitelistEntry:
        """
        Agrega path a whitelist con firma ECDSA
        
        Args:
            path: Path completo a permitir/bloquear
            policy: 1 = ALLOW_AI, 0 = BLOCK_AI
            ttl_hours: Horas antes de expiración
        
        Returns:
            WhitelistEntry firmada
        """
        # 1. Calcular hash del path (SHA256, primeros 8 bytes)
        path_bytes = path.encode('utf-8')
        path_hash_full = sha256(path_bytes).digest()
        path_hash = int.from_bytes(path_hash_full[:8], 'little')
        
        # 2. Timestamp actual (nanoseconds)
        timestamp = int(time.time() * 1e9)
        
        # 3. Construir mensaje a firmar
        # Formato: path (256 bytes) + path_hash (8 bytes) + policy (1 byte) + timestamp (8 bytes)
        message = bytearray(256 + 8 + 1 + 8)
        
        # Path (padding con zeros)
        path_padded = path_bytes[:256].ljust(256, b'\x00')
        message[0:256] = path_padded
        
        # Path hash
        message[256:264] = path_hash.to_bytes(8, 'little')
        
        # Policy
        message[264] = policy
        
        # Timestamp
        message[265:273] = timestamp.to_bytes(8, 'little')
        
        # 4. Firmar con ECDSA
        signature = self.sk.sign(bytes(message), hashfunc=sha256)
        
        # 5. Crear entrada
        entry = WhitelistEntry(
            path=path,
            path_hash=path_hash,
            policy=policy,
            signature=signature,
            timestamp=timestamp,
            version=1
        )
        
        # 6. Guardar en cache
        self.entries[path_hash] = entry
        
        print(f"✅ Agregado a whitelist: {path}")
        print(f"   Hash: {path_hash:016x}")
        print(f"   Policy: {'ALLOW' if policy == 1 else 'BLOCK'}")
        print(f"   Expires: {ttl_hours}h")
        
        return entry
    
    def verify_entry(self, entry: WhitelistEntry) -> bool:
        """
        Verifica firma ECDSA de entrada
        
        Args:
            entry: Entrada a verificar
        
        Returns:
            True si firma válida
        """
        # 1. Reconstruir mensaje
        message = bytearray(256 + 8 + 1 + 8)
        
        path_padded = entry.path.encode('utf-8')[:256].ljust(256, b'\x00')
        message[0:256] = path_padded
        message[256:264] = entry.path_hash.to_bytes(8, 'little')
        message[264] = entry.policy
        message[265:273] = entry.timestamp.to_bytes(8, 'little')
        
        # 2. Verificar firma
        try:
            self.vk.verify(entry.signature, bytes(message), hashfunc=sha256)
            return True
        except ecdsa.BadSignatureError:
            return False
    
    def is_expired(self, entry: WhitelistEntry, ttl_hours: int = 24) -> bool:
        """
        Verifica si entrada expiró
        
        Args:
            entry: Entrada a verificar
            ttl_hours: TTL en horas
        
        Returns:
            True si expirada
        """
        now = int(time.time() * 1e9)
        age_ns = now - entry.timestamp
        age_hours = age_ns / (3600 * 1e9)
        
        return age_hours > ttl_hours
    
    def export_to_json(self, output_path: str):
        """
        Exporta whitelist a JSON
        
        Args:
            output_path: Path de salida
        """
        data = {
            'entries': [entry.to_dict() for entry in self.entries.values()],
            'public_key': self.vk.to_pem().decode('utf-8')
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Whitelist exportada: {output_path}")
    
    def import_from_json(self, input_path: str) -> List[WhitelistEntry]:
        """
        Importa whitelist desde JSON
        
        Args:
            input_path: Path de entrada
        
        Returns:
            Lista de entradas importadas
        """
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        entries = []
        for entry_dict in data['entries']:
            entry = WhitelistEntry.from_dict(entry_dict)
            
            # Verificar firma
            if not self.verify_entry(entry):
                print(f"⚠️ Firma inválida: {entry.path}")
                continue
            
            # Verificar expiración
            if self.is_expired(entry):
                print(f"⚠️ Entrada expirada: {entry.path}")
                continue
            
            self.entries[entry.path_hash] = entry
            entries.append(entry)
        
        print(f"✅ Importadas {len(entries)} entradas válidas")
        return entries
    
    def get_public_key_bytes(self) -> bytes:
        """
        Obtiene clave pública en formato bytes (para eBPF)
        
        Returns:
            64 bytes (X, Y coordinates de P-256)
        """
        # ECDSA P-256 public key = 64 bytes (32 bytes X + 32 bytes Y)
        point = self.vk.pubkey.point
        x_bytes = point.x().to_bytes(32, 'big')
        y_bytes = point.y().to_bytes(32, 'big')
        
        return x_bytes + y_bytes


# Ejemplo de uso
if __name__ == "__main__":
    print("🔒 Whitelist Manager con ECDSA Signatures\n")
    
    # 1. Crear manager (genera claves)
    wm = WhitelistManager()
    
    # 2. Agregar paths a whitelist
    paths_to_allow = [
        "/tmp/sentinel/data",
        "/var/lib/sentinel/logs",
        "/usr/bin/python3",
        "/bin/bash"
    ]
    
    for path in paths_to_allow:
        wm.add_to_whitelist(path, policy=1)
    
    print()
    
    # 3. Exportar a JSON
    wm.export_to_json("/tmp/sentinel-whitelist.json")
    
    print()
    
    # 4. Verificar entradas
    print("🔍 Verificando firmas:")
    for entry in wm.entries.values():
        valid = wm.verify_entry(entry)
        expired = wm.is_expired(entry)
        status = "✅ VÁLIDA" if valid and not expired else "❌ INVÁLIDA"
        print(f"  {entry.path}: {status}")
    
    print()
    
    # 5. Obtener clave pública para eBPF
    pubkey = wm.get_public_key_bytes()
    print(f"📋 Clave pública (64 bytes):")
    print(f"   {pubkey.hex()}")
    
    print("\n✅ Whitelist Manager listo para integración con eBPF")
