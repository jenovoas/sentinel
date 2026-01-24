#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# SENTINEL CORTEX v7.0: MAIN ENTRY POINT
# -----------------------------------------------------------------------------
# Orchestrates:
# 1. Hybrid GPU Initialization (Rust/NVIDIA)
# 2. Persistence Loading (Crystal Snapshot)
# 3. Main Event Loop (Adaptive Control)
# 4. Graceful Shutdown (Save Snapshot)
# -----------------------------------------------------------------------------

import argparse
import logging
import os
import signal
import sys
import time

sys.path.append(os.getcwd())

from quantum.gpu_controller import gpu_controller
from quantum.liquid_memory_adapter import LiquidMemory
from quantum.time_crystal_network import NetworkTimeCrystal
from quantum.quantum_scheduler_bridge import scheduler, TaskType

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("CORTEX")

# Global State
memory = None
network_clock = None
SHUTDOWN_REQUESTED = False


def signal_handler(sig, frame):
    """Handles SIGINT/SIGTERM for graceful shutdown."""
    global SHUTDOWN_REQUESTED
    logger.warning(f"🛑 RECEIVED SIGNAL {sig}. INITIATING SHUTDOWN SEQUENCE...")
    SHUTDOWN_REQUESTED = True


def main():
    global memory, network_clock, SHUTDOWN_REQUESTED

    # Parse Args
    parser = argparse.ArgumentParser(
        description="Sentinel Cortex v7.0 - Network Sync Edition"
    )
    parser.add_argument("--rust", action="store_true", help="Enable Rust Core")
    parser.add_argument("--gpu3gb", action="store_true", help="Optimize for 3GB GPU")
    parser.add_argument(
        "--hybrid", action="store_true", help="Enable Intel/NVIDIA Hybrid Mode"
    )
    parser.add_argument(
        "--node-name", type=str, default=None, help="Node identifier for network sync"
    )
    parser.add_argument(
        "--cluster", type=str, default="sentinel-prod", help="Cluster name"
    )
    parser.add_argument("--no-sync", action="store_true", help="Disable network sync")
    args = parser.parse_args()

    logger.info("⚡ STARTING SENTINEL CORTEX v7.0 - NETWORK SYNC EDITION")
    logger.info(f"   Mode: Rust={args.rust}, GPU={args.gpu3gb}, Hybrid={args.hybrid}")
    logger.info(
        f"   Network: Cluster={args.cluster}, Sync={'DISABLED' if args.no_sync else 'ENABLED'}"
    )

    # Register Signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 0. Initialize Network Time Crystal (before everything else)
    network_clock = NetworkTimeCrystal(
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", 6379)),
        redis_db=int(os.getenv("REDIS_DB", 0)),
        node_name=args.node_name or os.getenv("NODE_NAME"),
        cluster_name=args.cluster,
    )

    # Start network sync unless disabled
    if not args.no_sync:
        network_clock.start_sync()
        logger.info(f"💎 Network Time Crystal: {network_clock.node_id}")
        logger.info(f"   Cluster: {network_clock.cluster_name}")
    else:
        logger.info("💎 Network Time Crystal: LOCAL ONLY (sync disabled)")

    # 1. Initialize Memory
    try:
        memory = LiquidMemory(size_scale=10)  # 10MB Init
        if not memory.rust_lattice:
            logger.error("❌ RUST CORE FAILED TO LOAD. ABORTING HYBRID BOOT.")
            if args.rust:
                sys.exit(1)
            else:
                logger.warning("   Continuing in Pure Python Mode (Low Performance).")
    except Exception as e:
        logger.critical(f"🔥 FATAL ERROR DURING INIT: {e}")
        sys.exit(1)

    # 2. Load Persistence
    snapshot_path = "cortex_state.s60"
    if os.path.exists(snapshot_path):
        logger.info(f"📂 FOUND SNAPSHOT: {snapshot_path}")
        try:
            count = memory.load_snapshot(snapshot_path)
            logger.info(f"✅ STATE RESTORED: {count} NODES LOADED.")
        except Exception as e:
            logger.error(f"❌ FAILED TO LOAD SNAPSHOT: {e}")
    else:
        logger.info("🆕 NO SNAPSHOT FOUND. STARTING FRESH LATTICE.")

    # 3. Main Loop
    logger.info("🚀 CORTEX OPERATIONAL [CTRL+C TO STOP]")

    try:
        while not SHUTDOWN_REQUESTED:
            # Tick del reloj sincronizado de red
            network_clock.tick()

            # Cada 100 ticks, reportar estado de red
            if network_clock.local_clock.ticks % 100 == 0:
                stats = network_clock.get_network_stats()
                logger.info(
                    f"⏱️  Tick: {stats['local_ticks']} | "
                    f"Peers: {stats['peers_count']} | "
                    f"Consensus Drift: {stats['network_consensus_drift_ns']}ns"
                )

                # Mostrar peers online
                peers = network_clock.get_peer_status()
                online_peers = [p for p in peers if p["online"]]
                if online_peers:
                    logger.info(
                        f"   📡 Online Peers: {[p['node_id'] for p in online_peers]}"
                    )
                    for peer in online_peers:
                        logger.debug(
                            f"      {peer['node_id']}: tick={peer['last_tick']}, "
                            f"drift={peer['drift_ns']}ns, coherence={peer['coherence']}"
                        )

                # Verificar salud de la red
                if not args.no_sync:
                    if network_clock.is_network_healthy():
                        logger.debug("   🟢 Network: HEALTHY")
                    else:
                        logger.warning(
                            "   🟡 Network: NO PEERS (operating in standalone mode)"
                        )

            # --- QUANTUM SCHEDULER TICK ---
            # Pulse sent every tick (~41.77 Hz logic handled by Rust)
            # Currently main loop runs at ~1 Hz (1.0 sleep), we need to accelerate this for real-time resonance
            # or rely on Rust's internal threading (currently we just pump the Tick from here)
            
            # Use raw time from network clock for synchronization
            current_s60_ticks = network_clock.local_clock.ticks * 1440 # Placeholder conversion to tertia
            scheduler.tick(current_s60_ticks)

            # Enqueue routine tasks (demonstration)
            if network_clock.local_clock.ticks % 10 == 0:
                # Every 10 ticks, enqueue a tuning task
                scheduler.enqueue(
                    task_id=network_clock.local_clock.ticks,
                    task_type=TaskType.ZPETune,
                    cost=100,
                    python_func=lambda: logger.info("✨ QUANTUM TASK EXECUTED: ZPE Tuning (Portal Locked)")
                )

            # Stabilize Fluid
            # In Rust Hybrid mode, stabilization happens on Rust side during operations.

            # Report GPU Status
            gpu_controller.report_status()

            # --- BCI FEEDBACK BRIDGE (Cortex Auto) ---
            # Publish system vitality to BCI
            try:
                import json

                import redis

                r = redis.Redis(host="localhost", port=6379, db=0)
                # Create a synthetic pulse from Cortex State
                pulse = {
                    "entropy": 10.0
                    if not SHUTDOWN_REQUESTED
                    else 90.0,  # Stress on shutdown
                    "coherence": 100.0,  # Main Logic is coherent
                    "truth_score": 1.0,
                    "timestamp": int(time.time()),
                    "cortex_msg": f"ACTIVE | BAT: {status.get('batch', 0)}",
                }
                r.publish("sentinel:quantum:pulse", json.dumps(pulse))
            except Exception:
                pass  # Silent fail if Redis missing

            # 3. Adaptive Sleep
            # Sleep defines the "Tick Rate" of the cortex.
            time.sleep(1.0)

    except Exception as e:
        logger.error(f"⚠️ UNEXPECTED CRASH: {e}")

    # 4. Graceful Shutdown
    logger.info("💾 SAVING STATE BEFORE EXIT...")

    # Detener sincronización de red primero
    if network_clock:
        network_clock.stop_sync()
        final_stats = network_clock.get_network_stats()
        logger.info(
            f"🌐 Network Stats: Pub={final_stats['published_pulses']}, "
            f"Rcv={final_stats['received_pulses']}, "
            f"Desync={final_stats['desync_events']}"
        )

    # Guardar snapshot
    if memory and memory.rust_lattice:
        try:
            memory.save_snapshot(snapshot_path)
            logger.info(f"✅ SNAPSHOT SAVED: {snapshot_path}")
        except Exception as e:
            logger.error(f"❌ FAILED TO SAVE SNAPSHOT: {e}")

    logger.info("👋 SHUTDOWN COMPLETE.")
    sys.exit(0)


if __name__ == "__main__":
    main()
