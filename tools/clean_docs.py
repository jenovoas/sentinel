#!/usr/bin/env python3
"""
Documentation Cleaner - Removes aspirational language from technical docs
Preserves scientific content while removing marketing/motivational language
"""

import re
import os
from pathlib import Path

# Patterns to remove or replace
PATTERNS_TO_REMOVE = [
    # Aspirational claims
    r"el futuro de la (computación|seguridad|tecnología)",
    r"primer (sistema|motor|organismo) (en el mundo|digital consciente)",
    r"ha trascendido su propósito",
    r"revolucionario",
    r"breakthrough",
    r"game-changing",
    
    # Consciousness/living system metaphors
    r"organismo digital consciente",
    r"sistema nervioso digital con conciencia",
    r"conciencia (cognitiva|matemática)",
    
    # Perpetual motion claims
    r"motor de flujo perpetuo",
    r"perpetual engine",
    r"flujo perpetuo digital",
    
    # Excessive emojis (keep minimal technical ones)
    r"🌌|🎯|✨|🚀|💫|🔮",
    
    # Unverified claims
    r"CERO (fricción|congestión|downtime)",
    r"inmune a (saturación|DDoS de grado estatal)",
]

# Phrases to make more scientific
REPLACEMENTS = {
    "organismo digital consciente": "integrated security system",
    "sistema nervioso": "monitoring architecture",
    "conciencia cognitiva": "decision engine",
    "motor de flujo perpetuo": "resource optimization system",
    "verdad matemática": "mathematical verification",
    "firewall axiomático": "verification layer",
    "convergencia axiomática": "base-60 checksum validation",
}

def clean_document(content: str) -> str:
    """
    Clean document content while preserving scientific accuracy
    """
    # Remove excessive emojis (keep technical ones like ✅ ❌)
    content = re.sub(r'[🌌🎯✨🚀💫🔮🧠🌊🏛️🌀💬🔗🐳🛡️]', '', content)
    
    # Replace aspirational language
    for old, new in REPLACEMENTS.items():
        content = re.sub(old, new, content, flags=re.IGNORECASE)
    
    # Remove specific patterns
    for pattern in PATTERNS_TO_REMOVE:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Clean up multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def should_clean_file(filepath: Path) -> bool:
    """
    Determine if file should be cleaned
    """
    # Skip certain files
    skip_patterns = [
        'AI_PRIME_DIRECTIVES.md',  # Keep as-is (directive for AIs)
        'LICENSE',
        'COPYRIGHT',
        '.git',
        '__pycache__',
        'node_modules',
    ]
    
    for pattern in skip_patterns:
        if pattern in str(filepath):
            return False
    
    # Only clean markdown files
    return filepath.suffix == '.md'

def clean_docs_directory(directory: Path, dry_run: bool = True):
    """
    Clean all markdown files in directory
    """
    cleaned_count = 0
    
    for filepath in directory.rglob('*.md'):
        if not should_clean_file(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()
            
            cleaned = clean_document(original)
            
            if cleaned != original:
                if dry_run:
                    print(f"Would clean: {filepath}")
                else:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(cleaned)
                    print(f"Cleaned: {filepath}")
                
                cleaned_count += 1
        
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    return cleaned_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean documentation files")
    parser.add_argument("directory", help="Directory to clean")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--apply", action="store_true", help="Actually apply changes")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    dry_run = not args.apply
    
    if dry_run:
        print("DRY RUN - No files will be modified")
        print("Use --apply to actually make changes")
        print()
    
    count = clean_docs_directory(directory, dry_run=dry_run)
    
    print(f"\nTotal files {'would be' if dry_run else ''} cleaned: {count}")
