import subprocess

# Client web applications and backend binaries paths
client_web_paths = [
    "/home/jnovoas/laespiguita_web/services/target/release/bakery-api",
    "/usr/bin/postgres",
    "/usr/libexec/postgres",
    "/usr/bin/nginx"
]

map_ids = ["25", "48"]

for map_id in map_ids:
    print(f"--- Adding Client Web Paths to Whitelist Map ID {map_id} ---")
    for path in client_web_paths:
        raw_bytes = path.encode('utf-8') + b'\x00'
        padded_bytes = raw_bytes.ljust(256, b'\x00')
        hex_key = [f"{b:02x}" for b in padded_bytes]
        
        cmd = ["sudo", "bpftool", "map", "update", "id", map_id, "key", "hex"] + hex_key + ["value", "hex", "01"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error inserting {path} into Map {map_id}: {res.stderr}")
        else:
            print(f"✔ Inserted: {path}")

