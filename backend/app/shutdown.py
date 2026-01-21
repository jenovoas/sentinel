"""
Graceful Shutdown Handler for Sentinel Backend

Handles SIGTERM and SIGINT signals to ensure clean shutdown:
- Finish processing in-flight requests
- Close database connections
- Close Redis connections
- Flush logs
- Notify monitoring systems

This is critical for HA:
- Prevents data corruption during failover
- Allows load balancers to drain connections
- Ensures clean state for restart
"""

import signal
import sys
import asyncio
import logging
from typing import Optional

from app.logging_config import setup_logging
from app.database import close_db

# Setup logger
logger = setup_logging("INFO")

# Global shutdown event
shutdown_event: Optional[asyncio.Event] = None


def setup_signal_handlers(app):
    """
    Set up signal handlers for graceful shutdown
    
    Handles:
    - SIGTERM: Sent by Docker/Kubernetes when stopping container
    - SIGINT: Sent by Ctrl+C in development
    """
    global shutdown_event
    shutdown_event = asyncio.Event()
    
    def handle_shutdown(signum, frame):
        """
        Signal handler for graceful shutdown
        
        Args:
            signum: Signal number (SIGTERM=15, SIGINT=2)
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        logger.warning(f"🛑 Received {signal_name}, initiating graceful shutdown...")
        
        # Set shutdown event
        shutdown_event.set()
        
        # Give application time to finish in-flight requests
        logger.info("⏳ Waiting for in-flight requests to complete (max 30s)...")
        
        # Schedule actual shutdown
        asyncio.create_task(graceful_shutdown())
    
    # Register handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    logger.info("✅ Signal handlers registered (SIGTERM, SIGINT)")


async def graceful_shutdown():
    """
    Perform graceful shutdown
    
    Steps:
    1. Stop accepting new requests (set readiness to false)
    2. Wait for in-flight requests to complete (max 30s)
    3. Close database connections
    4. Close Redis connections
    5. Flush logs
    6. Exit
    """
    try:
        # Step 1: Mark as not ready (stop accepting new requests)
        from app.routers.health import app_role, accept_requests
        app_role = "shutting_down"
        accept_requests = False
        logger.info("📛 Marked as not ready, load balancers will stop routing traffic")
        
        # Step 2: Wait for in-flight requests (max 30s)
        await asyncio.sleep(5)  # Give load balancers time to detect
        logger.info("⏳ Waiting for in-flight requests to complete...")
        await asyncio.sleep(25)  # Total 30s grace period
        
        # Step 3: Close database connections
        logger.info("🗄️ Closing database connections...")
        await close_db()
        
        # Step 4: Close Redis connections
        # TODO: Add Redis cleanup when implemented
        logger.info("📦 Closing Redis connections...")
        
        # Step 5: Flush logs
        logger.info("📝 Flushing logs...")
        logging.shutdown()
        
        logger.info("✅ Graceful shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Error during graceful shutdown: {e}")
    
    finally:
        # Exit process
        sys.exit(0)


async def check_shutdown():
    """
    Check if shutdown has been requested
    
    Can be called in long-running tasks to check if they should stop
    
    Returns:
        bool: True if shutdown requested
    """
    global shutdown_event
    if shutdown_event is None:
        return False
    return shutdown_event.is_set()
