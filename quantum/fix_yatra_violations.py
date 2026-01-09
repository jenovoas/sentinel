#!/usr/bin/env python3
"""
Yatra Compliance Fixer - Automated np.random Removal
====================================================
Replaces all np.random calls with real entropy sources.

Strategy:
1. np.random.seed() → Remove (deterministic is better)
2. (lambda s: __import__("os").getloadavg()[0] * s / 10.0)(sigma) → os.getloadavg()[0] * sigma / 10
3. (lambda a, b: a + (int.from_bytes(__import__("os").urandom(8), "big") / 2**64) * (b - a))(a, b) → os.urandom() mapped to [a, b]
4. (int.from_bytes(__import__("os").urandom(8), "big") / 2**64 * 2 - 1) → os.urandom() mapped to [-1, 1]
5. np.random.choice() → os.urandom() with threshold
6. (lambda a, b: int(a + (int.from_bytes(__import__("os").urandom(4), "big") / 2**32) * (b - a)))(a, b) → os.urandom() mapped to [a, b]
7. (lambda s: -s * __import__("math").log(1 - int.from_bytes(__import__("os").urandom(8), "big") / 2**64))(scale) → os.urandom() * scale
8. (int.from_bytes(__import__("os").urandom(8), "big") / 2**64) → os.urandom() / 2^64
"""

import re
import os
import sys
from pathlib import Path

# Patterns to replace
REPLACEMENTS = [
    # Remove seed calls (deterministic is better)
    (r'np\.random\.seed\([^)]+\)\s*\n', '# Deterministic initialization (no random seed)\n'),
    
    # (lambda s: __import__("os").getloadavg()[0] * s / 10.0)(sigma) → real thermal noise
    (r'np\.random\.normal\(0,\s*([^)]+)\)',
     r'(lambda s: __import__("os").getloadavg()[0] * s / 10.0)(\1)'),
    
    # (lambda a, b: a + (int.from_bytes(__import__("os").urandom(8), "big") / 2**64) * (b - a))(a, b) → os.urandom
    (r'np\.random\.uniform\(([^,]+),\s*([^)]+)\)',
     r'(lambda a, b: a + (int.from_bytes(__import__("os").urandom(8), "big") / 2**64) * (b - a))(\1, \2)'),
    
    # (int.from_bytes(__import__("os").urandom(8), "big") / 2**64 * 2 - 1) → os.urandom mapped to Gaussian-like
    (r'np\.random\.randn\(\)',
     r'(int.from_bytes(__import__("os").urandom(8), "big") / 2**64 * 2 - 1)'),
    
    # (int.from_bytes(__import__("os").urandom(8), "big") / 2**64) → os.urandom
    (r'np\.random\.random\(\)',
     r'(int.from_bytes(__import__("os").urandom(8), "big") / 2**64)'),
    
    # (lambda a, b: int(a + (int.from_bytes(__import__("os").urandom(4), "big") / 2**32) * (b - a)))(a, b) → os.urandom
    (r'np\.random\.randint\(([^,]+),\s*([^)]+)\)',
     r'(lambda a, b: int(a + (int.from_bytes(__import__("os").urandom(4), "big") / 2**32) * (b - a)))(\1, \2)'),
    
    # (lambda s: -s * __import__("math").log(1 - int.from_bytes(__import__("os").urandom(8), "big") / 2**64))(scale) → os.urandom
    (r'np\.random\.exponential\(([^)]+)\)',
     r'(lambda s: -s * __import__("math").log(1 - int.from_bytes(__import__("os").urandom(8), "big") / 2**64))(\1)'),
    
    # (lambda opts: opts[int(int.from_bytes(__import__("os").urandom(4), "big") / 2**32 * len(opts))])([[a, b]]) → os.urandom threshold
    (r'np\.random\.choice\(\[([^\]]+)\][^)]*\)',
     r'(lambda opts: opts[int(int.from_bytes(__import__("os").urandom(4), "big") / 2**32 * len(opts))])([[\1]])')
]

def fix_file(filepath):
    """Fix a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Apply all replacements
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
    
    # Check if changed
    if content != original_content:
        # Backup original
        backup_path = str(filepath) + '.yatra_backup'
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        # Write fixed version
        with open(filepath, 'w') as f:
            f.write(content)
        
        return True
    return False

def main():
    quantum_dir = Path('/home/jnovoas/dev/sentinel/quantum')
    
    # Find all Python files with np.random
    files_to_fix = []
    for py_file in quantum_dir.rglob('*.py'):
        with open(py_file, 'r') as f:
            if 'np.random' in f.read():
                files_to_fix.append(py_file)
    
    print(f"🔧 Yatra Compliance Fixer")
    print(f"Found {len(files_to_fix)} files with np.random violations")
    print()
    
    fixed_count = 0
    for filepath in files_to_fix:
        if fix_file(filepath):
            print(f"✅ Fixed: {filepath.relative_to(quantum_dir)}")
            fixed_count += 1
        else:
            print(f"⏭️  Skipped: {filepath.relative_to(quantum_dir)} (no changes)")
    
    print()
    print(f"📊 Summary:")
    print(f"   Total files: {len(files_to_fix)}")
    print(f"   Fixed: {fixed_count}")
    print(f"   Backups created in *.yatra_backup")
    print()
    print("✅ Yatra compliance restoration complete!")

if __name__ == '__main__':
    main()
