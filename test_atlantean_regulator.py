#!/usr/bin/env python3
import json
import sys
import os
from quantum.atlantic_regulator import MaatStabilizer

def test_atlantean_regulator(json_path):
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found.")
        return

    print(f"📂 Loading Crystal Data: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    maat = MaatStabilizer()
    
    print("\n⚖️  RUNNING MAAT SIMULATION ON CASCADE RESULTS\n" + "="*50)
    print(f"{'STAGES':<8} | {'OLD SPEED':<10} | {'ACCURACY':<10} | {'MAAT ACTION':<25} | {'NEW SPEED':<10}")
    print("-" * 75)
    
    for entry in data:
        stages = entry.get('num_stages', 0)
        speed = entry.get('speedup_measured', 1.0)
        acc = entry.get('accuracy', 100.0) / 100.0 # Normalize to 0-1
        
        new_speed, mode = maat.regulate(acc, speed)
        
        # Color coding
        status_color = ""
        if "SACRIFICE" in mode: status_color = "\033[91m"
        elif "PURE" in mode: status_color = "\033[92m"
        else: status_color = "\033[93m"
        
        print(f"{stages:<8} | {speed:<10.2f} | {acc:<10.4f} | {status_color}{mode:<25}\033[0m | {new_speed:.2f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='buffer_cascade_results.json', help="Input JSON file")
    args = parser.parse_args()
    
    test_atlantean_regulator(args.input)
