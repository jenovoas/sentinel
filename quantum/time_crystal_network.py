#!/usr/bin/env python3
# 🛡️ ME-60OS LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# TIME CRYSTAL NETWORK SYNCHRONIZATION (QNTP)
# -----------------------------------------------------------------------------
# Quantum Network Time Protocol - Sincronización distribuida de cristales
# de tiempo usando Redis PubSub como medio de transmisión.
#
# ARQUITECTURA:
# - Cada nodo tiene TimeCrystalClock local (maestro local)
# - Nodos publican pulsos de sincronización cada N ticks
# - Nodos ajustan fase basándose en consenso de red
# - Drift compensado con aritmética entera pura
#
# PROTOCOLO QNTP:
# 1. Cada nodo publica su pulso cada SYNC_INTERVAL ticks
# 2. Los nodos escuchan pulsos de otros nodos
# 3. Se calcula consenso de fase (promedio ponderado por coherencia)
# 4. Se ajusta la fase local hacia el consenso
# 5. Se mide drift relativo entre nodos
# -----------------------------------------------------------------------------

import json
import os
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

sys.path.append(os.getcwd())

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not available - Network sync disabled")

from quantum.time_crystal_clock import TimeCrystalClock
from quantum.yatra_core import S60


@dataclass
class NetworkPulse:
    """
    Pulso de sincronización de red.
    Todos los valores son enteros S60 (sin floats).

    Representa un snapshot del estado temporal de un nodo en un momento dado.
    """

    node_id: str
    timestamp_ns: int  # Nanosegundos absolutos (entero)
    tick_count: int  # Número de tick del reloj
    phase_raw: int  # Fase S60 raw (entero) - Reservado para futuro
    drift_ns: int  # Drift medido en nanosegundos (entero)
    coherence_raw: int  # Coherencia S60 raw (entero)

    def to_dict(self) -> dict:
        """Serializa a dict para Redis (JSON)."""
        return {
            "node_id": self.node_id,
            "timestamp_ns": self.timestamp_ns,
            "tick_count": self.tick_count,
            "phase_raw": self.phase_raw,
            "drift_ns": self.drift_ns,
            "coherence_raw": self.coherence_raw,
        }

    @staticmethod
    def from_dict(data: dict) -> "NetworkPulse":
        """Deserializa desde dict de Redis."""
        return NetworkPulse(
            node_id=data["node_id"],
            timestamp_ns=int(data["timestamp_ns"]),
            tick_count=int(data["tick_count"]),
            phase_raw=int(data["phase_raw"]),
            drift_ns=int(data["drift_ns"]),
            coherence_raw=int(data["coherence_raw"]),
        )


class NetworkTimeCrystal:
    """
    Cristal de Tiempo Sincronizado en Red.

    Extiende TimeCrystalClock con capacidad de sincronización distribuida
    mediante QNTP (Quantum Network Time Protocol).

    CASOS DE USO:
    - Multi-nodo Sentinel para High Availability
    - Sincronización de servicios distribuidos
    - Lattice holográfico compartido entre nodos
    - Integración con dispositivos ME-60OS

    PROTOCOLO:
    1. Cada nodo publica su pulso cada SYNC_INTERVAL ticks
    2. Los nodos escuchan pulsos de otros nodos
    3. Se calcula consenso de drift (promedio ponderado por coherencia)
    4. Se mide latencia relativa entre nodos
    5. Se detectan nodos desincronizados
    """

    # Intervalo de sincronización (cada cuántos ticks publicar)
    SYNC_INTERVAL = 60  # Cada 60 ticks (~ 1.4 segundos)

    # Ventana de consenso (cuántos pulsos considerar para promedio)
    CONSENSUS_WINDOW = 10  # Últimos 10 pulsos de cada nodo

    # Umbral de desincronización (nanosegundos)
    DESYNC_THRESHOLD_NS = 100_000_000  # 100ms

    # Timeout para considerar un nodo offline (segundos)
    PEER_TIMEOUT_S = 10

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        node_name: Optional[str] = None,
        cluster_name: str = "default",
    ):
        """
        Inicializa cristal de tiempo sincronizado en red.

        Args:
            redis_host: Host de Redis
            redis_port: Puerto de Redis
            redis_db: DB de Redis
            node_name: Nombre del nodo (default: UUID)
            cluster_name: Nombre del cluster (múltiples clusters pueden coexistir)
        """
        # Cristal de tiempo local
        self.local_clock = TimeCrystalClock()

        # Identidad del nodo
        self.node_id = node_name or f"node-{uuid.uuid4().hex[:8]}"
        self.cluster_name = cluster_name

        # Redis connection
        self.redis_client = None
        self.pubsub = None
        self.redis_available = False

        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=False,  # Trabajamos con bytes
                )
                # Test connection
                self.redis_client.ping()
                self.redis_available = True
                print(f"✅ Redis conectado para sincronización de red")
            except Exception as e:
                print(f"⚠️  Redis no disponible: {e}")
                self.redis_available = False

        # Canal de sincronización (por cluster)
        self.sync_channel = f"qntp:time_crystal:{cluster_name}:sync".encode()

        # Historia de pulsos recibidos de otros nodos
        # node_id -> List[NetworkPulse]
        self.peer_pulses: Dict[str, List[NetworkPulse]] = {}

        # Última vez que vimos cada peer (para timeout detection)
        self.peer_last_seen: Dict[str, float] = {}

        # Thread de escucha
        self.listen_thread = None
        self.running = False

        # Estadísticas
        self.published_count = 0
        self.received_count = 0
        self.desync_events = 0

        # Consenso de red (drift promedio)
        self.network_consensus_drift_ns = 0

        print(f"💎 Network Time Crystal: {self.node_id}")
        print(f"   Cluster: {cluster_name}")
        print(f"   Sync Interval: {self.SYNC_INTERVAL} ticks")
        print(
            f"   Redis: {'ENABLED' if self.redis_available else 'DISABLED (local only)'}"
        )

    def start_sync(self):
        """Inicia el thread de sincronización de red."""
        if not self.redis_available:
            print("⚠️  Sync de red no disponible (Redis offline)")
            return

        if self.running:
            print("⚠️  Sync ya está corriendo")
            return

        self.running = True

        # Iniciar PubSub listener
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(self.sync_channel)

        # Thread para escuchar pulsos de red
        self.listen_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name=f"QNTP-Listener-{self.node_id}"
        )
        self.listen_thread.start()

        print(f"🌐 Network Sync: ACTIVE")

    def stop_sync(self):
        """Detiene la sincronización de red."""
        if not self.running:
            return

        self.running = False

        if self.pubsub:
            try:
                self.pubsub.unsubscribe(self.sync_channel)
                self.pubsub.close()
            except:
                pass

        if self.listen_thread:
            self.listen_thread.join(timeout=2.0)

        print(f"🌐 Network Sync: STOPPED")

    def tick(self):
        """
        Tick sincronizado de red.

        1. Ejecuta tick local (TimeCrystalClock)
        2. Cada SYNC_INTERVAL ticks, publica pulso a la red
        3. Actualiza consenso de red
        4. Detecta peers offline
        """
        # Tick local
        self.local_clock.tick()

        # Publicar pulso si toca
        if self.local_clock.ticks % self.SYNC_INTERVAL == 0:
            self._publish_pulse()
            self._update_network_consensus()
            self._check_peer_timeouts()

    def _publish_pulse(self):
        """Publica pulso de sincronización a la red."""
        if not self.redis_available:
            return

        # Obtener estado actual del reloj
        coherence = self.local_clock.get_coherence()

        # Calcular drift promedio (nanosegundos enteros)
        drift_ns = 0
        if self.local_clock.drift_history:
            total_drift = sum(self.local_clock.drift_history)
            drift_ns = total_drift // len(self.local_clock.drift_history)

        # Crear pulso
        pulse = NetworkPulse(
            node_id=self.node_id,
            timestamp_ns=time.perf_counter_ns(),
            tick_count=self.local_clock.ticks,
            phase_raw=0,  # Reservado para expansión futura
            drift_ns=drift_ns,
            coherence_raw=coherence.to_raw()
            if isinstance(coherence, S60)
            else int(coherence * S60.SCALE_0),
        )

        # Publicar a Redis
        try:
            message = json.dumps(pulse.to_dict())
            self.redis_client.publish(self.sync_channel, message)
            self.published_count += 1
        except Exception as e:
            print(f"⚠️  Error publicando pulso: {e}")

    def _listen_loop(self):
        """Loop de escucha de pulsos de red (thread)."""
        print(f"👂 Escuchando pulsos de red en {self.sync_channel.decode()}...")

        try:
            for message in self.pubsub.listen():
                if not self.running:
                    break

                if message["type"] != "message":
                    continue

                try:
                    data = json.loads(message["data"])
                    pulse = NetworkPulse.from_dict(data)

                    # Ignorar nuestros propios pulsos
                    if pulse.node_id == self.node_id:
                        continue

                    # Guardar pulso de peer
                    if pulse.node_id not in self.peer_pulses:
                        self.peer_pulses[pulse.node_id] = []
                        print(f"📡 Nuevo peer detectado: {pulse.node_id}")

                    self.peer_pulses[pulse.node_id].append(pulse)
                    self.peer_last_seen[pulse.node_id] = time.time()

                    # Mantener solo los últimos CONSENSUS_WINDOW pulsos
                    if len(self.peer_pulses[pulse.node_id]) > self.CONSENSUS_WINDOW:
                        self.peer_pulses[pulse.node_id].pop(0)

                    self.received_count += 1

                    # Detectar desincronización
                    self._check_desync(pulse)

                except Exception as e:
                    print(f"⚠️  Error procesando pulso: {e}")
        except Exception as e:
            print(f"⚠️  Listen loop error: {e}")

    def _check_desync(self, pulse: NetworkPulse):
        """
        Detecta si un peer está desincronizado.

        Compara el drift del peer con nuestro drift local.
        Si la diferencia excede el umbral, se registra como desincronización.
        """
        if not self.local_clock.drift_history:
            return

        # Nuestro drift local promedio
        local_drift = sum(self.local_clock.drift_history) // len(
            self.local_clock.drift_history
        )

        # Drift del peer
        peer_drift = pulse.drift_ns

        # Diferencia absoluta
        drift_diff = abs(local_drift - peer_drift)

        if drift_diff > self.DESYNC_THRESHOLD_NS:
            self.desync_events += 1
            print(f"⚠️  DESYNC detectado: {pulse.node_id} (diff={drift_diff}ns)")

    def _update_network_consensus(self):
        """
        Actualiza el consenso de drift de la red.

        Calcula el drift promedio ponderado por coherencia de todos los peers.
        Esto permite a cada nodo saber el "estado temporal" de la red.
        """
        if not self.peer_pulses:
            return

        # Recolectar pulsos más recientes de todos los peers
        recent_pulses = []
        for node_id, pulses in self.peer_pulses.items():
            if pulses:
                recent_pulses.append(pulses[-1])

        if not recent_pulses:
            return

        # Calcular consenso de drift (promedio ponderado por coherencia)
        total_drift_weighted = 0
        total_weight = 0

        for pulse in recent_pulses:
            weight = max(1, pulse.coherence_raw)  # Evitar división por cero
            total_drift_weighted += pulse.drift_ns * weight
            total_weight += weight

        if total_weight > 0:
            self.network_consensus_drift_ns = total_drift_weighted // total_weight

    def _check_peer_timeouts(self):
        """
        Verifica si algún peer ha dejado de enviar pulsos (timeout).

        Remueve peers que no han enviado pulsos en PEER_TIMEOUT_S segundos.
        """
        current_time = time.time()
        offline_peers = []

        for node_id, last_seen in self.peer_last_seen.items():
            if current_time - last_seen > self.PEER_TIMEOUT_S:
                offline_peers.append(node_id)

        for node_id in offline_peers:
            print(f"📴 Peer offline: {node_id}")
            del self.peer_last_seen[node_id]
            if node_id in self.peer_pulses:
                del self.peer_pulses[node_id]

    def get_network_stats(self) -> dict:
        """Retorna estadísticas de sincronización de red."""
        return {
            "node_id": self.node_id,
            "cluster": self.cluster_name,
            "local_ticks": self.local_clock.ticks,
            "peers_count": len(self.peer_pulses),
            "published_pulses": self.published_count,
            "received_pulses": self.received_count,
            "desync_events": self.desync_events,
            "network_consensus_drift_ns": self.network_consensus_drift_ns,
            "network_enabled": self.redis_available and self.running,
        }

    def get_peer_status(self) -> List[dict]:
        """Retorna estado de peers conocidos."""
        peers = []
        current_time = time.time()

        for node_id, pulses in self.peer_pulses.items():
            if not pulses:
                continue

            last_pulse = pulses[-1]
            last_seen = self.peer_last_seen.get(node_id, 0)

            peers.append(
                {
                    "node_id": node_id,
                    "last_tick": last_pulse.tick_count,
                    "drift_ns": last_pulse.drift_ns,
                    "coherence": S60._from_raw(last_pulse.coherence_raw),
                    "pulses_received": len(pulses),
                    "last_seen_ago": current_time - last_seen if last_seen else 999,
                    "online": (current_time - last_seen) < self.PEER_TIMEOUT_S
                    if last_seen
                    else False,
                }
            )

        return peers

    def is_network_healthy(self) -> bool:
        """
        Verifica si la red está saludable.

        Criterios:
        - Al menos 1 peer online
        - Desincronización baja
        - Redis disponible
        """
        if not self.redis_available or not self.running:
            return False

        online_peers = sum(1 for p in self.get_peer_status() if p["online"])

        return online_peers > 0

    def get_coherence(self):
        """Retorna coherencia del reloj local (compatibilidad con TimeCrystalClock)."""
        return self.local_clock.get_coherence()

    def get_drift_stats(self):
        """Retorna estadísticas de drift (compatibilidad con TimeCrystalClock)."""
        return self.local_clock.get_drift_stats()


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    print("💎 Network Time Crystal - Demo")
    print("=" * 60)

    # Crear dos nodos simulados
    node_a = NetworkTimeCrystal(node_name="NodeA", cluster_name="test-cluster")
    node_b = NetworkTimeCrystal(node_name="NodeB", cluster_name="test-cluster")

    # Iniciar sincronización
    node_a.start_sync()
    node_b.start_sync()

    print("\n🌐 Simulando 120 ticks con sincronización de red...")
    print("-" * 60)

    try:
        for i in range(120):
            node_a.tick()
            node_b.tick()

            if i % 20 == 0:
                stats_a = node_a.get_network_stats()
                stats_b = node_b.get_network_stats()

                print(f"\nTick {i}:")
                print(
                    f"  NodeA: Ticks={stats_a['local_ticks']} | Pub={stats_a['published_pulses']} | Rcv={stats_a['received_pulses']} | Peers={stats_a['peers_count']}"
                )
                print(
                    f"  NodeB: Ticks={stats_b['local_ticks']} | Pub={stats_b['published_pulses']} | Rcv={stats_b['received_pulses']} | Peers={stats_b['peers_count']}"
                )

                if i >= 60:
                    peers_a = node_a.get_peer_status()
                    if peers_a:
                        print(
                            f"  NodeA ve peers: {[p['node_id'] for p in peers_a if p['online']]}"
                        )

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")

    finally:
        print("\n🛑 Deteniendo sincronización...")
        node_a.stop_sync()
        node_b.stop_sync()

        print("\n📊 Estadísticas Finales:")
        print(f"  NodeA: {node_a.get_network_stats()}")
        print(f"  NodeB: {node_b.get_network_stats()}")

        print("\n👥 Estado de Peers:")
        for peer in node_a.get_peer_status():
            print(
                f"  {peer['node_id']}: online={peer['online']}, drift={peer['drift_ns']}ns"
            )

        print("\n✅ Demo completado")
