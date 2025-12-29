#!/bin/bash
# test_injection.sh - Sentinel Forensics Validation

# 1. Create a dummy process that stays alive
python3 -c "import time; print('Dummy process started...'); time.sleep(100)" &
DUMMY_PID=$!

echo "🚀 Dummy process started with PID: $DUMMY_PID"

# 2. Pattern to detect (common shellcode fragment)
# \x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb
PATTERN=$(printf "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb")

# 3. Inject pattern into dummy process memory via /proc/pid/mem
# We need to find a writable region
MAP_LINE=$(grep "rw-p" /proc/$DUMMY_PID/maps | head -n 1)
ADDR=$(echo $MAP_LINE | cut -d'-' -f1)
ADDR_HEX=$((0x$ADDR))

echo "💉 Injecting shellcode pattern at $ADDR in PID $DUMMY_PID"

# Use python to write to the memory at specific address
python3 -c "
import os
pid = $DUMMY_PID
addr = $ADDR_HEX
pattern = b'$PATTERN'
with open(f'/proc/{pid}/mem', 'wb') as f:
    f.seek(addr)
    f.write(pattern)
"

echo "✅ Injection complete. Check forensics logs for ALERT."

# 4. Wait a bit and then cleanup
sleep 10
kill $DUMMY_PID
