#!/bin/bash
# Sentinel Forensics Injection Test

echo "💉 [TEST] Simulating malicious injection..."

# 1. Start a dummy process
sleep 100 &
PID=$!
echo "📡 Dummy process started with PID: $PID"

# 2. Pattern to inject (standard x64 execve shellcode)
# Shellcode: \x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb
PATTERN=$(printf '\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb')

# 3. Wait for scanner to be ready (manually run forensics first)
echo "🔍 Injecting pattern into PID $PID..."

# Use gdb or simple dd to write to /proc/pid/mem if permissions allow
# For this test, we'll just use a python snippet to write to the process's stack or heap
python3 -c "
import os
pid = $PID
pattern = b'$PATTERN'
with open(f'/proc/{pid}/maps', 'r') as f:
    for line in f:
        if 'rw' in line: # Find a writable region
            addr_range = line.split()[0]
            start = int(addr_range.split('-')[0], 16)
            try:
                with open(f'/proc/{pid}/mem', 'rb+') as mem:
                    mem.seek(start)
                    mem.write(pattern)
                print(f'✅ Successfully injected at {hex(start)}')
                break
            except Exception as e:
                continue
"

echo "🧪 Injection complete. Check forensics logs for ALERT."

# Keep process alive for a bit
sleep 5
kill $PID
echo "🏁 Test dummy cleaned up."
