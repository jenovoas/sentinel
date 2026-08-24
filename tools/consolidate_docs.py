import os
import shutil
import glob
from pathlib import Path

# Paths
ROOT_DIR = "/home/jnovoas/Proyectos/sentinel"
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROVEN_DIR = os.path.join(DOCS_DIR, "proven")
RESEARCH_DIR = os.path.join(DOCS_DIR, "research")
ARCHIVE_DIR = os.path.join(DOCS_DIR, "archive")
ARCHIVE_LEGACY = os.path.join(ARCHIVE_DIR, "legacy")
ARCHIVE_2025 = os.path.join(ARCHIVE_DIR, "2025-12-21")

# Create dirs
for d in [PROVEN_DIR, RESEARCH_DIR, ARCHIVE_DIR, ARCHIVE_LEGACY, ARCHIVE_2025, os.path.join(ARCHIVE_DIR, "duplicates")]:
    os.makedirs(d, exist_ok=True)

# Master files mapping (Target -> [List of keywords or exact names to merge])
MERGE_PLAN = {
    os.path.join(PROVEN_DIR, "BENCHMARKS.md"): ["BENCHMARK", "FINAL_RESULTS", "VALIDATION_RESULTS"],
    os.path.join(PROVEN_DIR, "CLAIMS.md"): ["PATENT_MASTER", "EVIDENCE_LSM", "VICTORIA_TECNICA", "IP_CONSOLIDATION"],
    os.path.join(PROVEN_DIR, "ARCHITECTURE_PROVEN.md"): ["TRUTHSYNC_ARCHITECTURE", "AIOPS_SHIELD", "DUAL_LANE_IMPLEMENTATION", "SEGURIDAD_COMO_LEY", "ARCHITECTURE"],
    os.path.join(PROVEN_DIR, "EVIDENCE.md"): ["EVIDENCE", "FORENSE"],
    os.path.join(PROVEN_DIR, "TESTS.md"): ["TEST"],
    os.path.join(RESEARCH_DIR, "CLAIMS_THEORETICAL.md"): ["CLAIMS_THEORETICAL", "THEORY"],
    os.path.join(RESEARCH_DIR, "FUTURE_WORK.md"): ["FUTURE", "ROADMAP", "PROXIMOS_PASOS"],
    os.path.join(RESEARCH_DIR, "EXPERIMENTS.md"): ["EXP_0", "EXPERIMENT"],
    os.path.join(RESEARCH_DIR, "VISION.md"): ["VISION", "MASTER_PLAN", "STRATEGY"],
}

# The root masters (as per plan)
ROOT_MASTERS = ["README.md", "README_es.md", "GETTING_STARTED.md", "CONTRIBUTING.md", "DOCUMENTATION_INDEX.md", "TODO.md", "AGENTS.md", "CLAUDE.md", "CODEBUDDY.md", "GEMINI.md", "MEMORY.md", "QODER.md"] 

print("Scanning markdown files...")
all_mds = [f for f in glob.glob(os.path.join(DOCS_DIR, "**/*.md"), recursive=True) if "archive" not in f and "proven" not in f and "research" not in f]
all_mds_root = glob.glob(os.path.join(ROOT_DIR, "*.md"))
all_mds.extend([f for f in all_mds_root if os.path.basename(f) not in ROOT_MASTERS])

print(f"Found {len(all_mds)} candidate MD files for consolidation/archive.")

def append_to_master(master_path, source_path):
    with open(master_path, 'a', encoding='utf-8') as master:
        master.write(f"\n\n<!-- SOURCE: {os.path.basename(source_path)} -->\n\n")
        try:
            with open(source_path, 'r', encoding='utf-8') as src:
                master.write(src.read())
        except Exception as e:
            master.write(f"(Error reading {source_path}: {e})")
            
processed = set()

# Process merges
for master, keywords in MERGE_PLAN.items():
    if not os.path.exists(master):
        with open(master, 'w', encoding='utf-8') as f:
            f.write(f"# {os.path.basename(master).replace('.md', '')}\n\nConsolidated master document.\n")
    
    for md in all_mds:
        if md in processed: continue
        name = os.path.basename(md).upper()
        if any(k in name for k in keywords):
            append_to_master(master, md)
            shutil.copy2(md, os.path.join(ARCHIVE_2025, os.path.basename(md)))
            try:
                os.unlink(md)
            except OSError:
                pass
            processed.add(md)

# The rest: move to legacy archive (ignoring special dirs)
special_dirs = ["proven", "research", "archive"]
moved_count = 0
for md in all_mds:
    if md in processed: continue
    
    # Don't touch if it's already in the target structure
    rel = os.path.relpath(md, DOCS_DIR)
    if any(rel.startswith(d) for d in special_dirs): 
        continue
        
    try:
        dst = os.path.join(ARCHIVE_LEGACY, os.path.basename(md))
        if os.path.exists(dst):
            dst = os.path.join(ARCHIVE_DIR, "duplicates", f"dup_{moved_count}_{os.path.basename(md)}")
        shutil.copy2(md, dst)
        try:
            os.unlink(md)
        except OSError:
            pass
        moved_count += 1
    except OSError as e:
        print(f"Failed to copy {md}: {e}")
        
print(f"Consolidation complete. Moved {moved_count} extraneous files to archive.")
