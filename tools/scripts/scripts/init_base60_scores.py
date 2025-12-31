#!/usr/bin/env python3
"""
Initialize Base-60 Threat Scores Map

Populates the base60_threat_scores eBPF map with threat scores
based on divisibility properties.

Prime residues = high threat
Highly composite residues = low threat
"""

import os
import sys
from bcc import BPF

# Threat score mapping based on divisibility
# Primes (1 divisor) = 100 (CRITICAL)
# Highly composite (many divisors) = 0-20 (BENIGN)

PRIMES_60 = {1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}
DIVISORS_60 = {1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60}

def count_divisors(n):
    """Count divisors of n that also divide 60."""
    return sum(1 for d in DIVISORS_60 if n % d == 0)

def calculate_threat_score(residue):
    """
    Calculate threat score for a Base-60 residue.
    
    Logic:
    - Primes (1 divisor): 90-100 (HIGH THREAT)
    - Few divisors (2-3): 50-70 (MEDIUM)
    - Many divisors (4+): 0-30 (LOW)
    """
    if residue == 0:
        return 0  # Perfect harmony (divisible by all)
    
    if residue in PRIMES_60:
        return 95  # Prime = anomaly
    
    divisor_count = count_divisors(residue)
    
    if divisor_count >= 4:
        return 10  # Highly composite = benign
    elif divisor_count == 3:
        return 30
    elif divisor_count == 2:
        return 60
    else:
        return 90  # Only 1 divisor (prime)

def main():
    # Load eBPF program (just to access maps)
    bpf_prog = """
    #include <uapi/linux/bpf.h>
    
    BPF_ARRAY(base60_threat_scores, u32, 60);
    """
    
    b = BPF(text=bpf_prog)
    threat_scores = b["base60_threat_scores"]
    
    print("Initializing Base-60 Threat Scores...")
    print("=" * 60)
    
    for residue in range(60):
        score = calculate_threat_score(residue)
        threat_scores[residue] = score
        
        divisors = count_divisors(residue)
        status = "PRIME" if residue in PRIMES_60 else f"{divisors} div"
        
        print(f"Residue {residue:2d}: score={score:3d} ({status})")
    
    print("=" * 60)
    print("✅ Base-60 threat scores initialized successfully")
    print()
    print("Verification:")
    print(f"  - Residue 0 (perfect): {threat_scores[0]}")
    print(f"  - Residue 1 (prime): {threat_scores[1]}")
    print(f"  - Residue 30 (composite): {threat_scores[30]}")

if __name__ == "__main__":
    main()
