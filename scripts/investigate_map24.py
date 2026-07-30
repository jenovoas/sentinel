import subprocess

for i in range(5):
    res = subprocess.run(["sudo", "bpftool", "map", "lookup", "id", "24", "key", "hex", "00", "00", "00", "00"], capture_output=True, text=True)
    print(f"Sample {i}: {res.stdout.strip()}")
