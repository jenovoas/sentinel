"""
Loki Client con Firmas HMAC
Cliente para Loki con verificación criptográfica de headers

SEGURIDAD:
- HMAC-SHA256 en cada request
- Timestamp freshness (5 min window)
- Previene SSRF con headers forjados
- Nginx verifica firma antes de proxy
"""

import hmac
import hashlib
import json
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LogStream:
    """Stream de logs para Loki"""
    labels: Dict[str, str]
    entries: List[tuple]  # [(timestamp, log_line), ...]


class LokiClientSigned:
    """
    Cliente Loki con firmas HMAC
    
    FLUJO:
    1. Serializar payload
    2. Generar timestamp ISO8601
    3. Calcular HMAC-SHA256(tenant + timestamp + payload)
    4. Enviar con headers firmados
    5. Nginx verifica firma
    """
    
    def __init__(
        self,
        loki_url: str,
        secret_key: str,
        tenant_id: str = "sentinel-security"
    ):
        """
        Inicializa cliente
        
        Args:
            loki_url: URL de Loki (ej: http://nginx:3100)
            secret_key: Clave secreta compartida con Nginx
            tenant_id: Tenant ID para multi-tenancy
        """
        self.loki_url = loki_url.rstrip('/')
        self.secret_key = secret_key.encode('utf-8')
        self.tenant_id = tenant_id
        
        print(f"✅ Loki Client inicializado:")
        print(f"   URL: {self.loki_url}")
        print(f"   Tenant: {self.tenant_id}")
    
    def _generate_signature(
        self,
        tenant_id: str,
        timestamp: str,
        payload: str
    ) -> str:
        """
        Genera firma HMAC-SHA256
        
        Args:
            tenant_id: ID del tenant
            timestamp: Timestamp ISO8601
            payload: Payload JSON serializado
        
        Returns:
            Firma HMAC en hexadecimal
        """
        # Mensaje: tenant_id + timestamp + payload
        message = f"{tenant_id}{timestamp}{payload}"
        
        # HMAC-SHA256
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def push_logs(
        self,
        streams: List[LogStream],
        tenant_id: Optional[str] = None
    ) -> requests.Response:
        """
        Push logs a Loki con firma HMAC
        
        Args:
            streams: Lista de streams a enviar
            tenant_id: Override tenant ID (opcional)
        
        Returns:
            Response de Loki
        """
        tenant = tenant_id or self.tenant_id
        
        # 1. Serializar payload
        payload_dict = {
            "streams": [
                {
                    "stream": stream.labels,
                    "values": [
                        [str(int(ts * 1e9)), line]  # Timestamp en nanoseconds
                        for ts, line in stream.entries
                    ]
                }
                for stream in streams
            ]
        }
        
        payload = json.dumps(payload_dict)
        
        # 2. Timestamp ISO8601 UTC
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # 3. Generar firma HMAC
        signature = self._generate_signature(tenant, timestamp, payload)
        
        # 4. Headers con firma
        headers = {
            "Content-Type": "application/json",
            "X-Scope-OrgID": tenant,
            "X-Scope-Signature": signature,
            "X-Scope-Timestamp": timestamp
        }
        
        # 5. POST a Loki
        url = f"{self.loki_url}/loki/api/v1/push"
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=payload,
                timeout=5
            )
            
            if response.status_code == 204:
                print(f"✅ Logs enviados: {len(streams)} streams")
            elif response.status_code == 403:
                print(f"❌ Firma rechazada por Nginx")
                print(f"   Response: {response.text}")
            else:
                print(f"⚠️ Status {response.status_code}: {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            raise
    
    def verify_signature_locally(
        self,
        tenant_id: str,
        timestamp: str,
        payload: str,
        signature: str
    ) -> bool:
        """
        Verifica firma HMAC localmente (para testing)
        
        Args:
            tenant_id: ID del tenant
            timestamp: Timestamp ISO8601
            payload: Payload JSON
            signature: Firma a verificar
        
        Returns:
            True si firma válida
        """
        expected_sig = self._generate_signature(tenant_id, timestamp, payload)
        return hmac.compare_digest(signature, expected_sig)


# Ejemplo de uso
if __name__ == "__main__":
    import time
    
    print("🔒 Loki Client con HMAC Signatures\n")
    
    # 1. Crear cliente
    client = LokiClientSigned(
        loki_url="http://localhost:3100",
        secret_key="sentinel_secret_key_change_in_production",
        tenant_id="sentinel-security"
    )
    
    print()
    
    # 2. Crear streams de ejemplo
    streams = [
        LogStream(
            labels={
                "lane": "security",
                "source": "auditd",
                "host": "sentinel-01"
            },
            entries=[
                (time.time(), "User login successful: admin"),
                (time.time() + 1, "Sudo command executed: systemctl restart postgresql"),
            ]
        ),
        LogStream(
            labels={
                "lane": "ops",
                "source": "app",
                "host": "sentinel-01"
            },
            entries=[
                (time.time(), "INFO: Application started"),
                (time.time() + 1, "DEBUG: Cache hit rate: 99.5%"),
            ]
        )
    ]
    
    # 3. Enviar logs (esto fallará si Nginx no está configurado)
    print("📤 Enviando logs a Loki...")
    try:
        response = client.push_logs(streams)
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Esperado (Nginx no configurado aún): {e}")
    
    print()
    
    # 4. Test de verificación local
    print("🔍 Test de verificación local:")
    
    tenant = "sentinel-security"
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    payload = '{"test": "data"}'
    
    # Firma válida
    valid_sig = client._generate_signature(tenant, timestamp, payload)
    is_valid = client.verify_signature_locally(tenant, timestamp, payload, valid_sig)
    print(f"   Firma válida: {is_valid} ✅")
    
    # Firma inválida
    invalid_sig = "0" * 64
    is_valid = client.verify_signature_locally(tenant, timestamp, payload, invalid_sig)
    print(f"   Firma inválida: {is_valid} ❌")
    
    print("\n✅ Loki Client listo para integración con Nginx")
