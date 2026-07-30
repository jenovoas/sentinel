import subprocess

# List of critical administrative binary paths to populate into whitelist_map (256 bytes key)
whitelisted_paths = [
    "/usr/sbin/sshd",
    "/usr/bin/bash",
    "/usr/bin/zsh",
    "/usr/bin/systemctl",
    "/usr/bin/python3",
    "/usr/bin/node",
    "/usr/bin/podman",
    "/usr/sbin/bpftool",
    "/usr/bin/journalctl",
    "/usr/bin/ls",
    "/usr/bin/cat",
    "/usr/bin/curl",
    "/home/jnovoas/.local/bin/sentinel-cortex",
    "/home/jnovoas/.cargo/bin/cargo"
]

map_ids = ["25", "48"] # Map 25 (guardian_execve) and Map 48 (guardian_cognitive)

for map_id in map_ids:
    print(f"--- Populating Whitelist Map ID {map_id} ---")
    for path in whitelisted_paths:
        # Convert path string to 256 bytes hex representation
        raw_bytes = path.encode('utf-8') + b'\x00'
        # Pad with zeros to 256 bytes
        padded_bytes = raw_bytes.ljust(256, b'\x00')
        hex_key = [f"{b:02x}" for b in padded_bytes]
        
        cmd = ["sudo", "bpftool", "map", "update", "id", map_id, "key", "hex"] + hex_key + ["value", "hex", "01"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error inserting {path} into Map {map_id}: {res.stderr}")
        else:
            print(f"✔ Inserted: {path}")

for map_id in map_ids:
    cmd_dump = ["sudo", "bpftool", "map", "dump", "id", map_id]
    res_dump = subprocess.run(cmd_dump, capture_output=True, text=True)
    print(f"\nDump output for Map ID {map_id}: {len(res_dump.stdout.splitlines())} lines/entries.")

