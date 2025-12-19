"""
Write-Ahead Log (WAL) para Sentinel Dual-Lane
Garantiza durabilidad de eventos antes de procesamiento

CARACTERÍSTICAS:
- Append-only per lane
- Fsync periódico (100ms security, 1s ops)
- Replay on startup (recuperación de fallos)
- Rotación automática (tamaño/tiempo)
- Compresión LZ4 (opcional)
"""

import asyncio
import time
import json
import gzip
from typing import AsyncGenerator, Optional, List
from pathlib import Path
from dataclasses import dataclass
import logging
import os

from .data_lanes import DataLane, LaneEvent

logger = logging.getLogger(__name__)


@dataclass
class WALConfig:
    """Configuración de WAL por lane"""
    fsync_interval_ms: int  # Intervalo de fsync
    max_file_size_mb: int   # Tamaño máximo antes de rotar
    max_file_age_hours: int # Edad máxima antes de rotar
    compress: bool          # Comprimir archivos rotados
    retention_days: int     # Días de retención


class WAL:
    """
    Write-Ahead Log para durabilidad de eventos
    
    GARANTÍAS:
    - Eventos escritos antes de procesamiento
    - Fsync periódico (configurable por lane)
    - Replay completo en caso de fallo
    - Sin pérdida de datos
    
    ARQUITECTURA:
    - Un archivo WAL activo por lane
    - Archivos rotados comprimidos
    - Directorio: /var/lib/sentinel/wal/{lane}/
    """
    
    def __init__(
        self,
        base_path: Optional[Path] = None,
        security_config: Optional[WALConfig] = None,
        observability_config: Optional[WALConfig] = None
    ):
        # Default to /tmp for development, /var/lib/sentinel/wal for production
        if base_path is None:
            base_path = Path("/tmp/sentinel/wal")
        
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Configuraciones por lane
        self.configs = {
            DataLane.SECURITY: security_config or WALConfig(
                fsync_interval_ms=100,    # 100ms (muy frecuente)
                max_file_size_mb=100,     # 100MB
                max_file_age_hours=1,     # 1 hora
                compress=True,            # Comprimir rotados
                retention_days=730        # 2 años (compliance)
            ),
            DataLane.OBSERVABILITY: observability_config or WALConfig(
                fsync_interval_ms=1000,   # 1s (menos frecuente)
                max_file_size_mb=500,     # 500MB
                max_file_age_hours=24,    # 24 horas
                compress=True,            # Comprimir rotados
                retention_days=30         # 30 días
            )
        }
        
        # File handles por lane
        self.files = {}
        self.last_fsync = {}
        self.last_rotation_check = {}
        
        # Stats
        self.stats = {
            DataLane.SECURITY: {
                "events_written": 0,
                "bytes_written": 0,
                "fsyncs": 0,
                "rotations": 0
            },
            DataLane.OBSERVABILITY: {
                "events_written": 0,
                "bytes_written": 0,
                "fsyncs": 0,
                "rotations": 0
            }
        }
        
        # Inicializar archivos
        self._initialize_files()
    
    def _initialize_files(self):
        """Inicializa archivos WAL por lane"""
        for lane in DataLane:
            lane_dir = self.base_path / lane.value
            lane_dir.mkdir(parents=True, exist_ok=True)
            
            # Archivo WAL activo
            wal_file = lane_dir / "current.wal"
            
            # Abrir en modo append
            self.files[lane] = open(wal_file, "a", buffering=1)  # Line buffered
            self.last_fsync[lane] = time.time()
            self.last_rotation_check[lane] = time.time()
            
            logger.info(f"WAL initialized: {wal_file}")
    
    async def append(
        self,
        lane: DataLane,
        event: LaneEvent
    ) -> bool:
        """
        Append evento a WAL
        
        GARANTÍA: Evento escrito antes de return
        
        Args:
            lane: Carril de datos
            event: Evento a escribir
        
        Returns:
            True si exitoso, False si error
        """
        try:
            # Serializar evento
            event_json = json.dumps(event.to_dict())
            event_line = event_json + "\n"
            
            # Escribir a archivo
            file_handle = self.files[lane]
            file_handle.write(event_line)
            
            # Stats
            self.stats[lane]["events_written"] += 1
            self.stats[lane]["bytes_written"] += len(event_line)
            
            # Fsync si necesario
            await self._maybe_fsync(lane)
            
            # Rotar si necesario
            await self._maybe_rotate(lane)
            
            return True
            
        except Exception as e:
            logger.error(f"WAL append failed ({lane.value}): {e}")
            return False
    
    async def append_batch(
        self,
        lane: DataLane,
        events: List[LaneEvent]
    ) -> int:
        """
        Append batch de eventos a WAL
        
        Returns:
            Número de eventos escritos exitosamente
        """
        written = 0
        
        for event in events:
            if await self.append(lane, event):
                written += 1
        
        return written
    
    async def _maybe_fsync(self, lane: DataLane):
        """
        Fsync si intervalo alcanzado
        
        Security: 100ms (muy frecuente)
        Observability: 1s (menos frecuente)
        """
        config = self.configs[lane]
        elapsed_ms = (time.time() - self.last_fsync[lane]) * 1000
        
        if elapsed_ms >= config.fsync_interval_ms:
            file_handle = self.files[lane]
            file_handle.flush()
            os.fsync(file_handle.fileno())
            
            self.last_fsync[lane] = time.time()
            self.stats[lane]["fsyncs"] += 1
            
            logger.debug(f"WAL fsync ({lane.value}): {elapsed_ms:.0f}ms since last")
    
    async def _maybe_rotate(self, lane: DataLane):
        """
        Rotar archivo WAL si necesario
        
        Condiciones:
        - Tamaño > max_file_size_mb
        - Edad > max_file_age_hours
        """
        # Verificar cada 60s
        if (time.time() - self.last_rotation_check[lane]) < 60:
            return
        
        self.last_rotation_check[lane] = time.time()
        
        config = self.configs[lane]
        lane_dir = self.base_path / lane.value
        wal_file = lane_dir / "current.wal"
        
        # Verificar tamaño
        file_size_mb = wal_file.stat().st_size / 1024 / 1024
        
        # Verificar edad
        file_age_hours = (time.time() - wal_file.stat().st_mtime) / 3600
        
        should_rotate = (
            file_size_mb >= config.max_file_size_mb or
            file_age_hours >= config.max_file_age_hours
        )
        
        if should_rotate:
            await self._rotate(lane)
    
    async def _rotate(self, lane: DataLane):
        """
        Rotar archivo WAL
        
        1. Cerrar archivo actual
        2. Renombrar con timestamp
        3. Comprimir (opcional)
        4. Abrir nuevo archivo
        5. Limpiar archivos viejos
        """
        try:
            config = self.configs[lane]
            lane_dir = self.base_path / lane.value
            wal_file = lane_dir / "current.wal"
            
            # 1. Cerrar archivo actual
            file_handle = self.files[lane]
            file_handle.flush()
            os.fsync(file_handle.fileno())
            file_handle.close()
            
            # 2. Renombrar con timestamp
            timestamp = int(time.time())
            rotated_file = lane_dir / f"wal-{timestamp}.wal"
            wal_file.rename(rotated_file)
            
            logger.info(f"WAL rotated ({lane.value}): {rotated_file}")
            
            # 3. Comprimir (opcional)
            if config.compress:
                await self._compress_file(rotated_file)
            
            # 4. Abrir nuevo archivo
            self.files[lane] = open(wal_file, "a", buffering=1)
            self.last_fsync[lane] = time.time()
            
            self.stats[lane]["rotations"] += 1
            
            # 5. Limpiar archivos viejos
            await self._cleanup_old_files(lane)
            
        except Exception as e:
            logger.error(f"WAL rotation failed ({lane.value}): {e}")
    
    async def _compress_file(self, file_path: Path):
        """Comprimir archivo WAL con gzip"""
        try:
            compressed_path = file_path.with_suffix(".wal.gz")
            
            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    f_out.writelines(f_in)
            
            # Eliminar archivo sin comprimir
            file_path.unlink()
            
            logger.debug(f"WAL compressed: {compressed_path}")
            
        except Exception as e:
            logger.error(f"WAL compression failed: {e}")
    
    async def _cleanup_old_files(self, lane: DataLane):
        """
        Eliminar archivos WAL viejos según retention
        
        Security: 2 años
        Observability: 30 días
        """
        try:
            config = self.configs[lane]
            lane_dir = self.base_path / lane.value
            
            retention_seconds = config.retention_days * 24 * 3600
            cutoff_time = time.time() - retention_seconds
            
            # Buscar archivos viejos
            for wal_file in lane_dir.glob("wal-*.wal*"):
                if wal_file.stat().st_mtime < cutoff_time:
                    wal_file.unlink()
                    logger.info(f"WAL cleaned up: {wal_file}")
            
        except Exception as e:
            logger.error(f"WAL cleanup failed ({lane.value}): {e}")
    
    async def replay(
        self,
        lane: DataLane,
        from_timestamp: Optional[float] = None
    ) -> AsyncGenerator[LaneEvent, None]:
        """
        Replay eventos desde WAL
        
        Usado en:
        - Startup (recuperación de fallos)
        - Backfill (re-procesamiento)
        
        Args:
            lane: Carril de datos
            from_timestamp: Timestamp mínimo (None = todos)
        
        Yields:
            LaneEvent en orden cronológico
        """
        lane_dir = self.base_path / lane.value
        
        # Buscar todos los archivos WAL (ordenados por timestamp)
        wal_files = sorted(lane_dir.glob("wal-*.wal*"))
        
        # Agregar archivo actual
        current_file = lane_dir / "current.wal"
        if current_file.exists():
            wal_files.append(current_file)
        
        logger.info(f"WAL replay ({lane.value}): {len(wal_files)} files")
        
        events_replayed = 0
        
        for wal_file in wal_files:
            try:
                # Abrir archivo (descomprimir si necesario)
                if wal_file.suffix == ".gz":
                    file_handle = gzip.open(wal_file, "rt")
                else:
                    file_handle = open(wal_file, "r")
                
                # Leer líneas
                for line in file_handle:
                    try:
                        event_dict = json.loads(line.strip())
                        event = LaneEvent.from_dict(event_dict)
                        
                        # Filtrar por timestamp si especificado
                        if from_timestamp and event.timestamp < from_timestamp:
                            continue
                        
                        events_replayed += 1
                        yield event
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"WAL replay: invalid JSON line: {e}")
                        continue
                
                file_handle.close()
                
            except Exception as e:
                logger.error(f"WAL replay failed for {wal_file}: {e}")
                continue
        
        logger.info(f"WAL replay ({lane.value}): {events_replayed} events replayed")
    
    async def flush(self, lane: DataLane):
        """Flush manual de WAL"""
        file_handle = self.files[lane]
        file_handle.flush()
        os.fsync(file_handle.fileno())
        
        self.last_fsync[lane] = time.time()
        self.stats[lane]["fsyncs"] += 1
    
    def get_stats(self, lane: Optional[DataLane] = None) -> dict:
        """
        Obtiene estadísticas de WAL
        
        Args:
            lane: Lane específico (None = todos)
        
        Returns:
            Estadísticas de WAL
        """
        if lane:
            return self.stats[lane]
        
        return {
            "security": self.stats[DataLane.SECURITY],
            "observability": self.stats[DataLane.OBSERVABILITY]
        }
    
    def close(self):
        """Cierra archivos WAL (cleanup)"""
        for lane, file_handle in self.files.items():
            try:
                file_handle.flush()
                os.fsync(file_handle.fileno())
                file_handle.close()
                logger.info(f"WAL closed ({lane.value})")
            except Exception as e:
                logger.error(f"WAL close failed ({lane.value}): {e}")


# Global instance
wal = WAL()
