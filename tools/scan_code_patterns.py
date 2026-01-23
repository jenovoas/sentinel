#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path

# Configuration
IGNORED_DIRS = {
    '.git', '.venv', 'venv', '__pycache__', 'node_modules', 
    'dist', 'build', '.mypy_cache', '.pytest_cache', '.gemini',
    'coverage', 'htmlcov'
}

IGNORED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
    '.pyc', '.pyo', '.so', '.o', '.a', '.obj', 
    '.pdf', '.zip', '.tar', '.gz', '.whl',
    '.json', '.lock', '.map', '.css', '.scss' 
}

# Regex Patterns
PATTERN_FLOAT = re.compile(r'\b\d+\.\d+\b')
PATTERN_NUMPY = re.compile(r'\b(import\s+numpy|from\s+numpy|np\.|numpy\.)')
# Matches assignments like `x = 5` or `y = "hello"` at the end of a line (implying no trailing comment) 
# We capture the value group to see if it's a number or string
PATTERN_HARDCODED_ASSIGNMENT = re.compile(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(?P<value>\d+(\.\d+)?|\"[^\"]*\"|\ Chars*\")\s*$')

# We also want to catch just raw numbers in function calls or lists if possible, but that's noisy. 
# The user asked for "hardcoded data without appropriate comment". 
# The assignment check is the most reliable heuristic for "magic constants".

def is_text_file(file_path):
    """Simple check to see if a file is text (not binary)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, IOError):
        return False

def scan_file(file_path, issues):
    rel_path = os.path.relpath(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Could not read {rel_path}: {e}")
        return

    file_issues = []

    for i, line in enumerate(lines):
        lineno = i + 1
        line_stripped = line.strip()
        
        # Skip empty lines and full comment lines
        if not line_stripped:
            continue
        if line_stripped.startswith('#') or line_stripped.startswith('//'):
            continue

        # Check for Floats/Decimals
        floats = PATTERN_FLOAT.findall(line)
        if floats:
            file_issues.append({
                'line': lineno,
                'type': 'FLOAT_DECIMAL',
                'content': line_stripped,
                'details': f"Found: {', '.join(floats)}"
            })

        # Check for Numpy
        if PATTERN_NUMPY.search(line):
            file_issues.append({
                'line': lineno,
                'type': 'NUMPY_USAGE',
                'content': line_stripped,
                'details': "Numpy usage detected"
            })

        # Check for Hardcoded assignments without comments
        match = PATTERN_HARDCODED_ASSIGNMENT.match(line)
        if match:
            # If it matched, it means the line ends right after the value, so no comment follows on the same line. 
            # We should also check if the PREVIOUS line was a comment?
            # The prompt says "without the appropriate comment", often implying inline or preceding. 
            # Checking preceding is harder in a single pass without state, but let's just flag it for review.
            
            # Simple heuristic: if the variable name is uppercase (CONSTANT), we might be more lenient? 
            # Or usually constants ARE the hardcoded ones we want to flag if uncommented. 
            
            val = match.group('value')
            # Ignore obvious booleans or small integers if desired, but user asked for "hardcoded data".
            # We'll report it.
            file_issues.append({
                'line': lineno,
                'type': 'HARDCODED_NO_COMMENT',
                'content': line_stripped,
                'details': f"Assignment of {val} without inline comment"
            })

    if file_issues:
        issues[rel_path] = file_issues

def main():
    parser = argparse.ArgumentParser(description="Scan project for specific code patterns.")
    parser.add_argument('root_dir', nargs='?', default='.', help='Root directory to scan')
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_dir)
    print(f"Scanning directory: {root_dir}")
    
    all_issues = {}

    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            path_obj = Path(file_path)
            
            if path_obj.suffix in IGNORED_EXTENSIONS:
                continue

            # Only scan likely source code or text files
            if is_text_file(file_path):
                scan_file(file_path, all_issues)

    # Report
    if not all_issues:
        print("No issues found matching the criteria.")
        return

    print("\n=== Scan Results ===\n")
    
    # Sort by file path
    for file_path in sorted(all_issues.keys()):
        print(f"File: {file_path}")
        for issue in all_issues[file_path]:
            print(f"  [Line {issue['line']}] {issue['type']}: {issue['details']}")
            print(f"    Code: {issue['content']}")
        print("-" * 40)

    print(f"\nTotal files with issues: {len(all_issues)}")

if __name__ == "__main__":
    main()
