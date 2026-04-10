import subprocess
import hashlib

files_to_check = {
    "docs/S60_HARDWARE_SPEC.md": "b4619bc6efd3549def46794c12463cdf82f3f51963de567c84b9c8d4937b72e8",
    "quantum/hardware_synthesis.py": "8df20a1646a070c560aa968bc165715fc677cc8e01064d4169acac298551e65b",
    "quantum/numerical_control_unit.py": "9f32a269c12e546de60b0d7b3dc509a66ca036d66b1a9fed2f01fe5b5886d2c4",
    "quantum/vimana_orbital_ascent_sim.py": "a7191b31d05b86cf8e894f0000be6cde3d6da7a3ec94d00b47f29b29ae0b98dc"
}

def get_sha256(content):
    return hashlib.sha256(content).hexdigest()

print(f"{'FILE':<40} | {'COMMIT':<8} | {'SHA256 MATCH?'}")
print("-" * 70)

for file_path, target_hash in files_to_check.items():
    # Get all commits that modified this file
    try:
        commits = subprocess.check_output(["git", "rev-list", "--all", "--", file_path]).decode().splitlines()
        for commit in commits:
            try:
                content = subprocess.check_output(["git", "show", f"{commit}:{file_path}"], stderr=subprocess.DEVNULL)
                current_hash = get_sha256(content)
                match = "✅ YES" if current_hash == target_hash else f"❌ {current_hash[:8]}..."
                print(f"{file_path:<40} | {commit[:8]} | {match}")
                if current_hash == target_hash:
                    # Found it! Restore it to a temporary location for verification
                    with open(f"RECOVERED_{file_path.replace('/', '_')}", "wb") as f:
                        f.write(content)
            except:
                continue
    except:
        print(f"File {file_path} not found in history.")
