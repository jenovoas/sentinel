import sounddevice as sd
try:
    print("🎤 Scanning Audio Devices...")
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    
    if not input_devices:
        print("❌ No Input Devices Found.")
        exit(1)
        
    print(f"✅ Found {len(input_devices)} Input Devices.")
    for d in input_devices:
        print(f"   - {d['name']}")
        
    print("\n🎤 Attempting 1s recording stream test...")
    def callback(indata, frames, time, status):
        pass
    with sd.InputStream(callback=callback):
        print("   ✅ Stream Opened Successfully.")
        
except Exception as e:
    print(f"❌ Audio Input Error: {e}")
    exit(1)
