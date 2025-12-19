"""
Sentinel Fluido V2 - Buffers Dinámicos Adaptativos
Optimizado para GTX 1050 con buffers que se ajustan al flujo de datos

MEJORA CLAVE: Buffers dinámicos según:
- Tamaño del mensaje (corto vs largo)
- Velocidad de respuesta (rápido vs lento)
- Tipo de contenido (código vs texto)
"""

import asyncio
import time
import json
from typing import AsyncGenerator, Optional
from dataclasses import dataclass, field
from enum import Enum
import httpx
import logging

logger = logging.getLogger(__name__)


class FlowType(Enum):
    """Tipo de flujo de datos"""
    SHORT_QUERY = "short"      # <50 chars, respuesta rápida
    MEDIUM_QUERY = "medium"    # 50-200 chars
    LONG_QUERY = "long"        # >200 chars
    CODE_GENERATION = "code"   # Generación de código


@dataclass
class AdaptiveBuffer:
    """
    Buffer adaptativo que ajusta tamaño según flujo de datos
    
    INNOVACIÓN: Tamaño dinámico basado en:
    - Longitud del mensaje
    - Velocidad de respuesta
    - Tipo de contenido
    """
    episodico: list = field(default_factory=list)
    patrones: dict = field(default_factory=dict)
    
    # Configuración dinámica
    max_episodic_size: int = 50  # Dinámico
    max_pattern_size: int = 100  # Dinámico
    chunk_size: int = 100        # Dinámico
    
    def adjust_for_flow(self, flow_type: FlowType, message_len: int):
        """
        Ajusta tamaños de buffer según flujo de datos
        
        OPTIMIZACIÓN CLAVE: Buffers pequeños para queries cortos,
        buffers grandes para queries largos
        """
        if flow_type == FlowType.SHORT_QUERY:
            # Query corto: Buffers mínimos (menos overhead)
            self.max_episodic_size = 10
            self.max_pattern_size = 20
            self.chunk_size = 50
        
        elif flow_type == FlowType.MEDIUM_QUERY:
            # Query medio: Buffers moderados
            self.max_episodic_size = 30
            self.max_pattern_size = 50
            self.chunk_size = 100
        
        elif flow_type == FlowType.LONG_QUERY:
            # Query largo: Buffers grandes
            self.max_episodic_size = 100
            self.max_pattern_size = 200
            self.chunk_size = 200
        
        elif flow_type == FlowType.CODE_GENERATION:
            # Código: Buffers muy grandes (contexto importante)
            self.max_episodic_size = 200
            self.max_pattern_size = 500
            self.chunk_size = 500
        
        logger.debug(
            f"Buffer ajustado: flow={flow_type.value}, "
            f"episodic={self.max_episodic_size}, "
            f"chunk={self.chunk_size}"
        )
    
    def agregar_episodio(self, texto: str):
        """Agrega a buffer episódico con límite dinámico"""
        # Truncar texto según chunk_size
        texto_truncado = texto[-self.chunk_size:] if len(texto) > self.chunk_size else texto
        self.episodico.append(texto_truncado)
        
        # Limitar tamaño total
        if len(self.episodico) > self.max_episodic_size:
            self.episodico.pop(0)
    
    def actualizar_patron(self, texto: str):
        """Actualiza frecuencia de patrones con límite dinámico"""
        # Key size adaptativo
        key_size = min(10, len(texto))
        key = texto[:key_size] if len(texto) >= key_size else texto
        self.patrones[key] = self.patrones.get(key, 0) + 1
        
        # Limitar tamaño de diccionario
        if len(self.patrones) > self.max_pattern_size:
            # Eliminar patrón menos frecuente
            min_key = min(self.patrones, key=self.patrones.get)
            del self.patrones[min_key]
    
    def contexto(self, limite: int = 3) -> str:
        """Obtiene contexto reciente (límite adaptativo)"""
        # Ajustar límite según tamaño de buffer
        limite_ajustado = min(limite, len(self.episodico))
        recientes = self.episodico[-limite_ajustado:] if self.episodico else []
        return " ".join(recientes) if recientes else ""


class SentinelFluidoV2:
    """
    Sentinel con buffers adaptativos dinámicos
    
    MEJORA CLAVE vs V1:
    - Buffers se ajustan según flujo de datos
    - Menos overhead para queries cortos
    - Más contexto para queries largos
    - Parámetros Ollama optimizados
    """
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "llama3.2:1b"
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.buffers: dict[str, AdaptiveBuffer] = {}
        self.client = httpx.AsyncClient(timeout=60.0)
        
        logger.info(f"SentinelFluidoV2: {model} @ {ollama_url} (buffers adaptativos)")
    
    def _get_buffer(self, user_id: str) -> AdaptiveBuffer:
        """Obtiene o crea buffer adaptativo para usuario"""
        if user_id not in self.buffers:
            self.buffers[user_id] = AdaptiveBuffer()
        return self.buffers[user_id]
    
    def _detect_flow_type(self, mensaje: str) -> FlowType:
        """
        Detecta tipo de flujo según mensaje
        
        HEURÍSTICA:
        - <50 chars: SHORT_QUERY
        - 50-200 chars: MEDIUM_QUERY
        - >200 chars: LONG_QUERY
        - Contiene código: CODE_GENERATION
        """
        msg_len = len(mensaje)
        
        # Detectar código (heurística simple)
        code_indicators = ["def ", "class ", "import ", "function ", "{", "}", "```"]
        is_code = any(indicator in mensaje for indicator in code_indicators)
        
        if is_code:
            return FlowType.CODE_GENERATION
        elif msg_len < 50:
            return FlowType.SHORT_QUERY
        elif msg_len < 200:
            return FlowType.MEDIUM_QUERY
        else:
            return FlowType.LONG_QUERY
    
    def _get_optimized_params(self, flow_type: FlowType) -> dict:
        """
        Parámetros Ollama optimizados según flujo
        
        OPTIMIZACIÓN CLAVE: Parámetros pequeños para queries cortos,
        parámetros grandes para queries largos
        """
        if flow_type == FlowType.SHORT_QUERY:
            return {
                "temperature": 0.7,
                "num_predict": 128,      # Respuesta corta
                "num_ctx": 512,          # Contexto mínimo
                "num_batch": 32,         # Batch pequeño
                "num_gpu": 1,
                "num_thread": 4
            }
        
        elif flow_type == FlowType.MEDIUM_QUERY:
            return {
                "temperature": 0.7,
                "num_predict": 256,      # Respuesta media
                "num_ctx": 1024,         # Contexto medio
                "num_batch": 64,         # Batch medio
                "num_gpu": 1,
                "num_thread": 4
            }
        
        elif flow_type == FlowType.LONG_QUERY:
            return {
                "temperature": 0.7,
                "num_predict": 512,      # Respuesta larga
                "num_ctx": 2048,         # Contexto grande
                "num_batch": 128,        # Batch grande
                "num_gpu": 1,
                "num_thread": 4
            }
        
        else:  # CODE_GENERATION
            return {
                "temperature": 0.3,      # Más determinista
                "num_predict": 1024,     # Código largo
                "num_ctx": 4096,         # Contexto muy grande
                "num_batch": 256,        # Batch muy grande
                "num_gpu": 1,
                "num_thread": 4
            }
    
    def _construir_contexto(self, buffer: AdaptiveBuffer, mensaje: str) -> str:
        """Construye prompt con contexto adaptativo"""
        ctx = buffer.contexto(limite=3)
        if ctx:
            return f"Context: {ctx}\n\nUser: {mensaje}\nAssistant:"
        return f"User: {mensaje}\nAssistant:"
    
    async def responder_simple(self, user_id: str, mensaje: str) -> tuple[str, float]:
        """
        Versión simple con buffers adaptativos (para benchmarks)
        
        Returns:
            (respuesta, ttfb_ms)
        """
        # 1. Detectar tipo de flujo
        flow_type = self._detect_flow_type(mensaje)
        
        # 2. Obtener buffer y ajustar
        buffer = self._get_buffer(user_id)
        buffer.adjust_for_flow(flow_type, len(mensaje))
        
        # 3. Construir prompt
        prompt = self._construir_contexto(buffer, mensaje)
        
        # 4. Obtener parámetros optimizados
        params = self._get_optimized_params(flow_type)
        
        start = time.time()
        
        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": params
                }
            )
            response.raise_for_status()
            
            ttfb = (time.time() - start) * 1000
            data = response.json()
            respuesta = data.get("response", "")
            
            # Update buffers (ya ajustados)
            buffer.agregar_episodio(respuesta)
            buffer.actualizar_patron(respuesta)
            
            logger.info(
                f"Flow: {flow_type.value}, TTFB: {ttfb:.0f}ms, "
                f"Buffer: {buffer.max_episodic_size}/{buffer.chunk_size}"
            )
            
            return respuesta, ttfb
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama error: {e}")
            return f"Error: {str(e)}", 0
    
    async def responder(
        self,
        user_id: str,
        mensaje: str
    ) -> AsyncGenerator[tuple[str, Optional[float]], None]:
        """
        Responde con streaming y buffers adaptativos
        
        Yields:
            (chunk, ttfb) - ttfb solo en primer chunk
        """
        # 1. Detectar tipo de flujo
        flow_type = self._detect_flow_type(mensaje)
        
        # 2. Obtener buffer y ajustar
        buffer = self._get_buffer(user_id)
        buffer.adjust_for_flow(flow_type, len(mensaje))
        
        # 3. Construir prompt
        prompt = self._construir_contexto(buffer, mensaje)
        
        # 4. Obtener parámetros optimizados
        params = self._get_optimized_params(flow_type)
        
        start = time.time()
        ttfb = None
        respuesta_completa = ""
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": params
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        
                        if not chunk:
                            continue
                        
                        # TTFB: Mide PRIMER token real
                        if ttfb is None:
                            ttfb = (time.time() - start) * 1000
                            logger.info(
                                f"TTFB: {ttfb:.0f}ms, Flow: {flow_type.value}"
                            )
                        
                        respuesta_completa += chunk
                        
                        # Update buffers (ya ajustados dinámicamente)
                        buffer.agregar_episodio(chunk)
                        buffer.actualizar_patron(chunk)
                        
                        # Yield chunk con TTFB solo en primero
                        yield chunk, ttfb if ttfb else None
                        ttfb = None  # Solo reportar una vez
                        
                    except json.JSONDecodeError:
                        continue
            
            # Log final
            total_time = (time.time() - start) * 1000
            logger.info(
                f"Completado: {len(respuesta_completa)} chars, "
                f"{total_time:.0f}ms total, "
                f"Buffer: {buffer.max_episodic_size}/{buffer.chunk_size}"
            )
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama error: {e}")
            yield f"Error: {str(e)}", None
    
    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# Global instance
sentinel_fluido_v2 = SentinelFluidoV2()
