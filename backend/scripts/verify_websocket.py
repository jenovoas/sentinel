import asyncio
import websockets
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WS_URL = "ws://localhost:8000/ws/events"

async def test_websocket():
    logger.info(f"🔌 Connecting to {WS_URL}...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            logger.info("✅ Connected to WebSocket!")
            
            # Esperar mensajes
            logger.info("⏳ Waiting for messages (timeout 10s)...")
            try:
                # Esperar hasta 10 segundos por un mensaje
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                
                logger.info(f"📩 Message received: {message[:100]}...") # Log first 100 chars
                
                try:
                    data = json.loads(message)
                    if data.get("type") == "decision":
                        logger.info("✅ RECEIVED VALID DECISION EVENT")
                        logger.info(f"   Details: {json.dumps(data['data'], indent=2)}")
                        return True
                    else:
                        logger.warning(f"⚠️ Received unknown message type: {data.get('type')}")
                        return False
                        
                except json.JSONDecodeError:
                    logger.error("❌ Failed to decode JSON message")
                    return False
                    
            except asyncio.TimeoutError:
                logger.error("❌ Timeout waiting for message. Is traffic generation running?")
                return False
                
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    if success:
        logger.info("🏆 WEBSOCKET TEST PASSED")
        sys.exit(0)
    else:
        logger.error("💀 WEBSOCKET TEST FAILED")
        sys.exit(1)
