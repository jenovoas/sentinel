#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/events"
    print(f"🔌 Connecting to {uri}...")
    try:
        async with websockets.connect(uri, origin="http://localhost:8000") as websocket:
            print("✅ Connected to Battlefield Stream!")
            
            # Send a ping to verify bidirectional comms
            await websocket.send("ping")
            response = await websocket.recv()
            print(f"📩 Received: {response}")
            
            print("👀 Listening for events (press Ctrl+C to stop)...")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"\n🚨 EVENT RECEIVED:")
                print(f"   Type: {data.get('type')}")
                print(f"   Decision: {data['data'].get('decision_type')}")
                print(f"   Confidence: {data['data'].get('confidence')}")
                print(f"   Patterns: {data['data'].get('patterns')}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\n👋 Disconnected")
