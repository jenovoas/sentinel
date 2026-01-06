#!/usr/bin/env python3
"""
Quantum-AI Base-60 Latency Benchmark
Measures precise latency of Base-60 threat scoring in kernel space
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from bcc import BPF
import time
import statistics
import subprocess

# BCC-compatible eBPF code with latency measurement
bpf_code = """
#include <uapi/linux/ptrace.h>

#define BASE60_MODULO 60

BPF_ARRAY(base60_scores, u32, 60);
BPF_HISTOGRAM(latency_hist, u64);
BPF_ARRAY(latency_stats, u64, 5);

#define STAT_COUNT 0
#define STAT_MIN 1
#define STAT_MAX 2
#define STAT_SUM 3

int quantum_bprm_check(struct pt_regs *ctx) {
    u64 start_ns = bpf_ktime_get_ns();
    
    // Get process pattern
    u64 pattern = bpf_get_current_pid_tgid();
    
    // Calculate Base-60 residue
    u32 residue = pattern % BASE60_MODULO;
    
    // Lookup threat score
    u32 *score_ptr = base60_scores.lookup(&residue);
    u32 threat_score = score_ptr ? *score_ptr : 50;
    
    // Measure latency
    u64 end_ns = bpf_ktime_get_ns();
    u64 latency_ns = end_ns - start_ns;
    
    // Update histogram
    latency_hist.increment(bpf_log2l(latency_ns));
    
    // Update stats
    u32 idx;
    u64 *val;
    
    idx = STAT_COUNT;
    val = latency_stats.lookup(&idx);
    if (val) (*val)++;
    
    idx = STAT_SUM;
    val = latency_stats.lookup(&idx);
    if (val) (*val) += latency_ns;
    
    idx = STAT_MIN;
    val = latency_stats.lookup(&idx);
    if (val && (*val == 0 || latency_ns < *val)) *val = latency_ns;
    
    idx = STAT_MAX;
    val = latency_stats.lookup(&idx);
    if (val && latency_ns > *val) *val = latency_ns;
    
    return 0;
}
"""

print("=" * 80)
print("Quantum-AI Base-60 Latency Benchmark")
print("=" * 80)
print()

# Load eBPF program
print("[1/5] Loading eBPF program...")
b = BPF(text=bpf_code)

# Initialize Base-60 scores
print("[2/5] Initializing Base-60 scores...")
base60_scores = b["base60_scores"]
PRIMES_60 = {1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}

for residue in range(60):
    if residue == 0:
        score = 0
    elif residue in PRIMES_60:
        score = 95
    else:
        divisors_60 = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60]
        count = sum(1 for d in divisors_60 if residue % d == 0)
        if count >= 4:
            score = 10
        elif count == 3:
            score = 30
        elif count == 2:
            score = 60
        else:
            score = 90
    
    base60_scores[residue] = base60_scores.Leaf(score)

print("✅ Scores initialized")

# Attach to syscall
print("[3/5] Attaching to sys_execve...")
b.attach_kprobe(event=b.get_syscall_fnname("execve"), fn_name="quantum_bprm_check")
print("✅ Attached")

# Generate test load
print("[4/5] Generating test load (1000 execve calls)...")
print("   This will take ~10 seconds...")

for i in range(1000):
    subprocess.run(["/bin/true"], capture_output=True)
    if i % 100 == 0:
        print(f"   Progress: {i}/1000")

print("✅ Test load complete")

# Collect statistics
print("\n[5/5] Collecting statistics...")
time.sleep(1)  # Let final events process

stats = b["latency_stats"]
count = stats[0].value
total_ns = stats[3].value
min_ns = stats[1].value
max_ns = stats[2].value

if count > 0:
    avg_ns = total_ns / count
else:
    avg_ns = 0

print("\n" + "=" * 80)
print("LATENCY RESULTS")
print("=" * 80)
print()
print(f"Total measurements: {count}")
print(f"Min latency:        {min_ns:,} ns ({min_ns/1000:.2f} μs)")
print(f"Max latency:        {max_ns:,} ns ({max_ns/1000:.2f} μs)")
print(f"Avg latency:        {avg_ns:,.0f} ns ({avg_ns/1000:.2f} μs)")
print()

# Print histogram
print("Latency Distribution (log2 scale):")
print("-" * 80)
b["latency_hist"].print_log2_hist("latency (ns)")

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)
print()
print(f"Target latency:     <1,000 ns (1 μs)")
print(f"Achieved:           {avg_ns:.0f} ns ({avg_ns/1000:.2f} μs)")
print()

if avg_ns < 1000:
    print("✅ PASSED: Sub-microsecond latency achieved")
    print(f"   Performance: {1000/avg_ns:.1f}x better than 1 μs target")
else:
    print(f"⚠️  ABOVE TARGET: {avg_ns/1000:.2f} μs (target: 1 μs)")

print()
print("Components breakdown (estimated):")
print("  - bpf_ktime_get_ns():     ~20 ns")
print("  - Modulo operation:       ~3 ns")
print("  - Map lookup:             ~50 ns")
print("  - Overhead/other:         ~" + f"{max(0, avg_ns - 73):.0f} ns")
print()
print("=" * 80)
