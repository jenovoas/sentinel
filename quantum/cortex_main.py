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

import sys
import os
import time
import signal
import logging
import argparse

sys.path.append(os.getcwd())

from quantum.liquid_memory_adapter import LiquidMemory
from quantum.gpu_controller import gpu_controller

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("CORTEX")

# Global State
memory = None
SHUTDOWN_REQUESTED = False

def signal_handler(sig, frame):
    """Handles SIGINT/SIGTERM for graceful shutdown."""
    global SHUTDOWN_REQUESTED
    logger.warning(f"🛑 RECEIVED SIGNAL {sig}. INITIATING SHUTDOWN SEQUENCE...")
    SHUTDOWN_REQUESTED = True

def main():
    global memory, SHUTDOWN_REQUESTED
    
    # Parse Args
    parser = argparse.ArgumentParser(description="Sentinel Cortex v7.0")
    parser.add_argument("--rust", action="store_true", help="Enable Rust Core")
    parser.add_argument("--gpu3gb", action="store_true", help="Optimize for 3GB GPU")
    parser.add_argument("--hybrid", action="store_true", help="Enable Intel/NVIDIA Hybrid Mode")
    args = parser.parse_args()
    
    logger.info("⚡ STARTING SENTINEL CORTEX v7.0")
    logger.info(f"   Mode: Rust={args.rust}, GPU={args.gpu3gb}, Hybrid={args.hybrid}")
    
    # Register Signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 1. Initialize Memory
    try:
        memory = LiquidMemory(size_scale=10) # 10MB Init
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
            # Simulate Workload / Maintenance Cycle
            
            # 1. Stabilize Fluid
            # In a real app, this would be triggered by 'store' events or a background thread.
            # Here we just keep the lattice alive.
            # memory.lattice.stabilize_fluid(1) # Python slow path
            
            # In Rust Hybrid mode, stabilization happens on Rust side during operations.
            
            # 2. Report Status
            status = gpu_controller.report_status()
            
            # 3. Adaptive Sleep
            # Sleep defines the "Tick Rate" of the cortex.
            time.sleep(1.0) 
            
    except Exception as e:
        logger.error(f"⚠️ UNEXPECTED CRASH: {e}")
        
    # 4. Graceful Shutdown
    logger.info("💾 SAVING STATE BEFORE EXIT...")
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
