#!/usr/bin/env python3
# 🛡️ ME-60OS LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# TEST: NETWORK TIME CRYSTAL SYNCHRONIZATION
# -----------------------------------------------------------------------------
# Prueba de sincronización multi-nodo usando NetworkTimeCrystal.
# Simula múltiples nodos Sentinel sincronizándose a través de Redis.
# -----------------------------------------------------------------------------

import os
import sys
import threading
import time
from typing import List

sys.path.append(os.getcwd())

from quantum.time_crystal_network import NetworkTimeCrystal


class NodeSimulator:
    """Simula un nodo Sentinel con su propio thread."""

    def __init__(self, node_name: str, cluster: str = "test-cluster"):
        self.node_name = node_name
        self.crystal = NetworkTimeCrystal(
            node_name=node_name,
            cluster_name=cluster,
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", 6379)),
        )
        self.running = False
        self.thread = None
        self.total_ticks = 0

    def start(self):
        """Inicia el nodo en su propio thread."""
        print(f"🚀 Starting node: {self.node_name}")
        self.crystal.start_sync()
        self.running = True
        self.thread = threading.Thread(
            target=self._run_loop, daemon=True, name=f"Node-{self.node_name}"
        )
        self.thread.start()

    def stop(self):
        """Detiene el nodo."""
        print(f"🛑 Stopping node: {self.node_name}")
        self.running = False
        self.crystal.stop_sync()
        if self.thread:
            self.thread.join(timeout=2.0)

    def _run_loop(self):
        """Loop principal del nodo (tick continuo)."""
        while self.running:
            self.crystal.tick()
            self.total_ticks += 1
            time.sleep(0.02)  # ~50 ticks/segundo

    def get_status(self) -> dict:
        """Retorna estado actual del nodo."""
        stats = self.crystal.get_network_stats()
        peers = self.crystal.get_peer_status()
        online_peers = [p for p in peers if p["online"]]

        return {
            "node_id": self.node_name,
            "ticks": stats["local_ticks"],
            "peers_count": len(online_peers),
            "published": stats["published_pulses"],
            "received": stats["received_pulses"],
            "desync_events": stats["desync_events"],
            "consensus_drift": stats["network_consensus_drift_ns"],
            "online_peers": [p["node_id"] for p in online_peers],
        }


def test_two_nodes():
    """Test básico: 2 nodos sincronizándose."""
    print("\n" + "=" * 70)
    print("TEST 1: SINCRONIZACIÓN DE 2 NODOS")
    print("=" * 70)

    # Crear nodos
    node1 = NodeSimulator("Alpha")
    node2 = NodeSimulator("Beta")

    # Iniciar nodos
    node1.start()
    time.sleep(1)  # Dar tiempo a Alpha para establecerse
    node2.start()

    print("\n⏳ Esperando sincronización (30 segundos)...\n")

    try:
        for i in range(30):
            time.sleep(1)

            if (i + 1) % 5 == 0:
                status1 = node1.get_status()
                status2 = node2.get_status()

                print(f"\n📊 T+{i + 1}s:")
                print(
                    f"  Alpha: Ticks={status1['ticks']} | Peers={status1['peers_count']} | Pub={status1['published']} | Rcv={status1['received']}"
                )
                print(
                    f"  Beta:  Ticks={status2['ticks']} | Peers={status2['peers_count']} | Pub={status2['published']} | Rcv={status2['received']}"
                )

                if status1["peers_count"] > 0 and status2["peers_count"] > 0:
                    print(f"  ✅ Nodos sincronizados")
                    print(f"     Alpha ve: {status1['online_peers']}")
                    print(f"     Beta ve:  {status2['online_peers']}")
                else:
                    print(f"  🟡 Esperando sincronización...")

    except KeyboardInterrupt:
        print("\n⚠️  Test interrumpido")

    finally:
        node1.stop()
        node2.stop()

        # Estadísticas finales
        final1 = node1.get_status()
        final2 = node2.get_status()

        print("\n" + "=" * 70)
        print("RESULTADOS TEST 1:")
        print("=" * 70)
        print(
            f"Alpha: Pub={final1['published']} | Rcv={final1['received']} | Desync={final1['desync_events']}"
        )
        print(
            f"Beta:  Pub={final2['published']} | Rcv={final2['received']} | Desync={final2['desync_events']}"
        )

        success = (
            final1["received"] > 0
            and final2["received"] > 0
            and final1["peers_count"] > 0
            and final2["peers_count"] > 0
        )

        if success:
            print("\n✅ TEST 1: PASSED - Nodos se sincronizaron correctamente")
        else:
            print("\n❌ TEST 1: FAILED - Nodos no se sincronizaron")

        return success


def test_multi_node():
    """Test avanzado: 4 nodos formando una red."""
    print("\n" + "=" * 70)
    print("TEST 2: RED DE 4 NODOS")
    print("=" * 70)

    # Crear 4 nodos
    nodes = [
        NodeSimulator("Node-A"),
        NodeSimulator("Node-B"),
        NodeSimulator("Node-C"),
        NodeSimulator("Node-D"),
    ]

    # Iniciar nodos escalonadamente
    for i, node in enumerate(nodes):
        node.start()
        time.sleep(0.5)  # Delay entre nodos

    print("\n⏳ Ejecutando red distribuida (20 segundos)...\n")

    try:
        for i in range(20):
            time.sleep(1)

            if (i + 1) % 5 == 0:
                print(f"\n📊 T+{i + 1}s:")
                for node in nodes:
                    status = node.get_status()
                    print(
                        f"  {status['node_id']}: "
                        f"Ticks={status['ticks']} | "
                        f"Peers={status['peers_count']} | "
                        f"Pub={status['published']} | "
                        f"Rcv={status['received']}"
                    )

    except KeyboardInterrupt:
        print("\n⚠️  Test interrumpido")

    finally:
        # Detener todos los nodos
        for node in nodes:
            node.stop()

        # Estadísticas finales
        print("\n" + "=" * 70)
        print("RESULTADOS TEST 2:")
        print("=" * 70)

        all_synced = True
        for node in nodes:
            final = node.get_status()
            print(
                f"{final['node_id']}: "
                f"Pub={final['published']} | "
                f"Rcv={final['received']} | "
                f"Peers={final['peers_count']} | "
                f"Desync={final['desync_events']}"
            )

            # Cada nodo debería ver a los otros 3
            if final["peers_count"] < 3:
                all_synced = False

        if all_synced:
            print("\n✅ TEST 2: PASSED - Todos los nodos se sincronizaron")
        else:
            print("\n❌ TEST 2: FAILED - Sincronización incompleta")

        return all_synced


def test_node_failure():
    """Test de resiliencia: Simula falla de un nodo."""
    print("\n" + "=" * 70)
    print("TEST 3: RESILIENCIA (FALLA DE NODO)")
    print("=" * 70)

    # Crear 3 nodos
    node1 = NodeSimulator("Node-1")
    node2 = NodeSimulator("Node-2")
    node3 = NodeSimulator("Node-3")

    # Iniciar todos
    node1.start()
    node2.start()
    node3.start()

    print("\n⏳ Fase 1: Red estable (10s)...")
    time.sleep(10)

    status1 = node1.get_status()
    status2 = node2.get_status()
    status3 = node3.get_status()

    print("\n📊 Estado antes de falla:")
    print(f"  Node-1: Peers={status1['peers_count']}")
    print(f"  Node-2: Peers={status2['peers_count']}")
    print(f"  Node-3: Peers={status3['peers_count']}")

    # Simular falla de Node-2
    print("\n💥 Simulando falla de Node-2...")
    node2.stop()

    print("\n⏳ Fase 2: Red recuperándose (15s)...")
    time.sleep(15)

    # Los nodos 1 y 3 deberían detectar que Node-2 está offline
    status1 = node1.get_status()
    status3 = node3.get_status()

    print("\n📊 Estado después de falla:")
    print(f"  Node-1: Peers={status1['peers_count']} (debería ser 1)")
    print(f"  Node-3: Peers={status3['peers_count']} (debería ser 1)")

    # Recuperar Node-2
    print("\n🔄 Recuperando Node-2...")
    node2 = NodeSimulator("Node-2")  # Recrear
    node2.start()

    print("\n⏳ Fase 3: Reintegración (10s)...")
    time.sleep(10)

    status1 = node1.get_status()
    status2 = node2.get_status()
    status3 = node3.get_status()

    print("\n📊 Estado después de recuperación:")
    print(f"  Node-1: Peers={status1['peers_count']} (debería ser 2)")
    print(f"  Node-2: Peers={status2['peers_count']} (debería ser 2)")
    print(f"  Node-3: Peers={status3['peers_count']} (debería ser 2)")

    # Limpiar
    node1.stop()
    node2.stop()
    node3.stop()

    # Verificar recuperación
    success = (
        status1["peers_count"] >= 2
        and status2["peers_count"] >= 2
        and status3["peers_count"] >= 2
    )

    print("\n" + "=" * 70)
    if success:
        print("✅ TEST 3: PASSED - Red se recuperó de la falla")
    else:
        print("❌ TEST 3: FAILED - Red no se recuperó completamente")

    return success


def main():
    print("💎" + "=" * 68 + "💎")
    print("   NETWORK TIME CRYSTAL - SUITE DE TESTS DE SINCRONIZACIÓN")
    print("💎" + "=" * 68 + "💎")

    # Verificar Redis
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        print("\n✅ Redis: DISPONIBLE")
    except Exception as e:
        print(f"\n❌ Redis: NO DISPONIBLE - {e}")
        print("\n⚠️  Los tests requieren Redis. Inicia Redis y vuelve a intentar:")
        print("    docker-compose up -d redis")
        print("    # o")
        print("    redis-server")
        return

    # Ejecutar tests
    results = []

    try:
        # Test 1: Dos nodos
        results.append(("Test 1: 2 Nodos", test_two_nodes()))

        time.sleep(2)  # Pausa entre tests

        # Test 2: Multi-nodo
        results.append(("Test 2: 4 Nodos", test_multi_node()))

        time.sleep(2)

        # Test 3: Resiliencia
        results.append(("Test 3: Resiliencia", test_node_failure()))

    except KeyboardInterrupt:
        print("\n\n⚠️  Suite de tests interrumpida")

    # Reporte final
    print("\n\n" + "=" * 70)
    print("REPORTE FINAL DE TESTS")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")

    print("\n" + "=" * 70)
    print(f"RESULTADO: {passed}/{total} tests pasados")
    print("=" * 70)

    if passed == total:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("   La sincronización de red está funcionando correctamente")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
        print("   Revisa la configuración de Redis y la conectividad de red")


if __name__ == "__main__":
    main()
