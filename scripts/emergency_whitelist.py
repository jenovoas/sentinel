import sys
import os

# Ensure the project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sentinel_core.ebpf.map_manager import MapManager

def unblock_tools():
    manager = MapManager()
    tools = [
        "/usr/bin/curl",
        "/usr/bin/systemctl",
        "/usr/local/bin/ollama",
        "/usr/bin/git",
        "/bin/rm",
        "/usr/bin/cat"
    ]
    
    print("🔓 [Emergency] Unblocking development tools...")
    for tool in tools:
        if manager.whitelist_binary(tool):
            print(f"✅ Unblocked: {tool}")
        else:
            print(f"❌ Failed to unblock: {tool}")

if __name__ == "__main__":
    unblock_tools()
