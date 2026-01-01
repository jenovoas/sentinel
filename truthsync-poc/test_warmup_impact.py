#!/usr/bin/env python3
import time
import numpy as np
from multiprocessing import shared_memory
import os

def test_warmup_impact():
    name = "sentinel_warmup_test"
    size = 10 * 1024 * 1024  # 10MB to make it measurable
    
    print(f"🧪 Testing SHM Warmup Impact ({size/1024/1024:.1f} MB)")
    
    # 1. Create fresh buffer
    try:
        shm = shared_memory.SharedMemory(name=name, create=True, size=size)
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=name)
        shm.unlink()
        shm = shared_memory.SharedMemory(name=name, create=True, size=size)

    # 2. Cold Access Test
    start_cold = time.perf_counter_ns()
    # Write to a few pages spread out
    for i in range(0, size, 4096):
        shm.buf[i] = 1
    end_cold = time.perf_counter_ns()
    cold_latency = (end_cold - start_cold) / 1000
    
    # 3. Warm-up
    print("🔄 Performing Warm-up (touching all pages)...")
    start_warmup = time.perf_counter_ns()
    # Read every page to trigger the kernel to allocate physical RAM
    mv = memoryview(shm.buf)
    for i in range(0, size, 4096):
        _ = mv[i]
    end_warmup = time.perf_counter_ns()
    
    # 4. Warm Access Test
    start_warm = time.perf_counter_ns()
    for i in range(0, size, 4096):
        shm.buf[i] = 2
    end_warm = time.perf_counter_ns()
    warm_latency = (end_warm - start_warm) / 1000
    
    improvement = (cold_latency - warm_latency) / cold_latency * 100
    
    print(f"\n📊 Results:")
    print(f"   Cold Access Latency: {cold_latency:.2f} μs")
    print(f"   Warm Access Latency: {warm_latency:.2f} μs")
    print(f"   Optimization Gain:   {improvement:.2f}%")
    
    del mv  # Crucial to avoid BufferError
    shm.close()
    shm.unlink()
    
    return cold_latency, warm_latency

if __name__ == "__main__":
    test_warmup_impact()
