#!/usr/bin/env python3
import sys

def to_base60(n):
    if n == 0:
        return "0"
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvw"
    res = ""
    while n > 0:
        res = digits[n % 60] + res
        n //= 60
    return res

def explain_residue(n):
    divisors = [i for i in range(1, 61) if 60 % i == 0]
    is_prime = n in [1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
    is_highly_composite = n in [6, 12, 30, 60]
    
    print(f"--- Analysis for Residue: {n} ---")
    print(f"Base-60 Notation: {to_base60(n)}")
    if is_prime:
        print("SCORING: 95 (HIGH THREAT - Prime Residue)")
    elif is_highly_composite:
        print("SCORING: 10 (BENIGN - Highly Composite)")
    else:
        score = 100 - (len([d for d in divisors if n % d == 0]) * 10)
        print(f"SCORING: {max(0, score)} (Calculated via Divisor Density)")
    
    print(f"Divisors of 60 that divide {n}: {[d for d in divisors if n % d == 0]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: base60_debug <residue_number>")
    else:
        try:
            val = int(sys.argv[1])
            explain_residue(val % 60)
        except ValueError:
            print("Please provide a valid integer.")
