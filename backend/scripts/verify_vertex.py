#!/usr/bin/env python3
import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.config import get_settings
from app.services.vertex_service import vertex_service

async def verify_vertex_connection():
    print("🛡️ SENTINEL VERTEX AI VERIFICATION CLIENT 🛡️")
    print("---------------------------------------------")
    
    settings = get_settings()
    print(f"🔹 Project: {settings.google_cloud_project}")
    print(f"🔹 Location: {settings.google_cloud_location}")
    print(f"🔹 Model: {settings.vertex_model_name}")
    print("---------------------------------------------")

    if not settings.google_cloud_project:
        print("❌ ERROR: GOOGLE_CLOUD_PROJECT is not set.")
        print("   Please set it in your .env file or environment.")
        return

    print("🔄 Initializing Vertex Service...")
    if not vertex_service.initialize():
        print("❌ Initialization Failed. Check credentials and permissions.")
        return

    print("✅ Initialization Successful.")
    print("🧠 Testing Gemini Generation...")
    
    prompt = "Hello Sentinel via Vertex AI. Are you ready?"
    print(f"   Prompt: '{prompt}'")
    
    response = await vertex_service.generate_content(prompt)
    
    if response:
        print("---------------------------------------------")
        print(f"🟢 RESPONSE:\n{response}")
        print("---------------------------------------------")
        print("✅ VERIFICATION COMPLETE: Vertex AI is operational.")
    else:
        print("❌ ERROR: No response generated.")

if __name__ == "__main__":
    asyncio.run(verify_vertex_connection())
