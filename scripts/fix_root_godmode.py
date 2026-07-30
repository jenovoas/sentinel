import subprocess

# Key for UID 0 (4 bytes): 00 00 00 00
# Value 1 (1 byte): 01
cmd = ["sudo", "bpftool", "map", "update", "id", "24", "key", "hex", "00", "00", "00", "00", "value", "hex", "01"]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Update output:", res.stdout, res.stderr)

cmd_dump = ["sudo", "bpftool", "map", "dump", "id", "24"]
res_dump = subprocess.run(cmd_dump, capture_output=True, text=True)
print("Dump output:\n", res_dump.stdout)
