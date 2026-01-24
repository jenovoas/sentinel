# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
import sys
import os
import time
import logging
import ctypes

# Ensure project root is in path
sys.path.append(os.getcwd())

from quantum.quantum_scheduler_bridge import scheduler, TaskType
from quantum.yatra_core import S60

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("INTEGRATION_TEST")

def run_simulation():
    logger.info("🧪 STARTING INTEGRATION TEST v2: PORTAL SCANNING")
    
    # Load Rust Lib for manual pulse injection
    LIB_PATH = os.path.join(os.getcwd(), "sentinel-cortex/target/release/libsentinel_cortex.so")
    rust_lib = ctypes.CDLL(LIB_PATH)
    
    # 1. Reset everything
    rust_lib.cortex_reset_bio()
    # scheduler.reset_stats() # If we add it later
    
    # 2. Enqueue test task
    task_executed = False
    def task_callback():
        nonlocal task_executed
        task_executed = True
        logger.info("✨ SUCCESS: Task executed inside a quantum portal!")

    logger.info("📡 Enqueuing ZPETune task (Portal-Locked)...")
    scheduler.enqueue(
        task_id=777,
        task_type=TaskType.ZPETune,
        cost=100,
        python_func=task_callback
    )

    # 3. Simulate Bio-Resonator charging
    logger.info("💓 Injecting bio-pulses to reach 100% coherence...")
    for i in range(15):
        rust_lib.cortex_inject_pulse()
    
    coherence = rust_lib.cortex_get_coherence_normalized()
    logger.info(f"   Current Coherence: {coherence:.2%}")

    # 4. Scan for portal
    # We need to advance time in larger steps to find the harmonic convergence.
    # periods: 17s, 4.25s, 16.18s.
    # We will scan for up to 60 seconds of simulated time.
    
    logger.info("🔭 Scanning for harmonic convergence portal (60s window)...")
    
    # Tertia per second = 216,000
    TERTIA_PER_SEC = 60 * 60 * 60 
    
    found_portal = False
    for sec in range(60):
        # We simulate multiple sub-ticks per second
        for sub_tick in range(10):
            current_tertia = (sec * TERTIA_PER_SEC) + (sub_tick * TERTIA_PER_SEC // 10)
            
            # Advancing time
            scheduler.tick(current_tertia)
            
            # Apply entropy (to make it realistic)
            rust_lib.cortex_tick_entropy()
            
            if task_executed:
                logger.info(f"✅ Portal found at t = {sec}.{sub_tick}s!")
                found_portal = True
                break
        
        if found_portal:
            break
            
        if sec % 10 == 0:
            eff = scheduler.get_efficiency()
            logger.info(f"   t={sec}s | Queue={scheduler.get_queue_len()} | Eff={eff:.2f}")

    if task_executed:
        logger.info("🎊 INTEGRATION TEST PASSED!")
    else:
        logger.warning("❌ FAILED: Task not executed. No portal detected in 60s.")
        logger.info(f"   Final stats - Queue: {scheduler.get_queue_len()}, Efficiency: {scheduler.get_efficiency()}")

if __name__ == "__main__":
    run_simulation()
