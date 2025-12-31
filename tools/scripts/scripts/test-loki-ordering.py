#!/usr/bin/env python3
"""
Test Loki Unordered Writes

Sends logs with out-of-order timestamps to verify Loki accepts them
after enabling unordered_writes configuration.

Usage: python scripts/test-loki-ordering.py
"""

import requests
from datetime import datetime, timedelta
import time
import sys

LOKI_URL = "http://localhost:3100"


def send_log(timestamp: datetime, message: str) -> int:
    """
    Send a log entry to Loki
    
    Args:
        timestamp: Log timestamp
        message: Log message
        
    Returns:
        HTTP status code
    """
    payload = {
        "streams": [{
            "stream": {
                "job": "test-ordering",
                "level": "info",
                "source": "test-script"
            },
            "values": [
                [str(int(timestamp.timestamp() * 1e9)), message]
            ]
        }]
    }
    
    try:
        response = requests.post(
            f"{LOKI_URL}/loki/api/v1/push",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error: {e}")
        return 0


def main():
    print("🧪 Testing Loki unordered writes configuration...")
    print(f"   Target: {LOKI_URL}")
    print()
    
    now = datetime.now()
    
    # Send logs in REVERSE chronological order (newest first)
    logs = [
        (now, "Log 3 (newest - sent first)"),
        (now - timedelta(minutes=5), "Log 2 (middle - sent second)"),
        (now - timedelta(minutes=10), "Log 1 (oldest - sent last)"),
    ]
    
    results = []
    for ts, msg in logs:
        status = send_log(ts, msg)
        results.append(status)
        
        if status == 204:
            print(f"  ✅ {msg}: {status} (accepted)")
        else:
            print(f"  ❌ {msg}: {status} (rejected)")
        
        time.sleep(0.2)
    
    print()
    
    # Verify all logs were accepted
    if all(status == 204 for status in results):
        print("🎉 SUCCESS: All logs accepted (unordered writes working!)")
        print("   Loki is correctly configured to handle out-of-order timestamps.")
        return 0
    else:
        print("❌ FAILURE: Some logs were rejected")
        print("   Check Loki configuration:")
        print("   - Ensure unordered_writes: true in limits_config")
        print("   - Restart Loki after config changes")
        return 1


if __name__ == "__main__":
    sys.exit(main())
