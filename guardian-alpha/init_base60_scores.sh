#!/bin/bash
# Initialize base60_threat_scores map with harmonic values
# Auto-detects map ID from loaded program

echo "🔢 Initializing Base-60 Threat Scores..."
echo ""

# Find quantum program ID
PROG_ID=$(sudo bpftool prog list | grep quantum_bprm_check | awk '{print $1}' | tr -d ':')

if [ -z "$PROG_ID" ]; then
    echo "❌ Error: quantum_bprm_check program not loaded"
    echo "   Run: sudo ./guardian-alpha/run_demo.sh"
    exit 1
fi

echo "✅ Found program ID: $PROG_ID"

# Find base60_threat_scores map
# It should be associated with this program
MAP_ID=$(sudo bpftool map list 2>/dev/null | grep -A 1 "array" | grep -B 1 "key 4B" | grep "^[0-9]" | head -1 | awk '{print $1}' | tr -d ':')

if [ -z "$MAP_ID" ]; then
    echo "❌ Error: base60_threat_scores map not found"
    echo "   Available maps:"
    sudo bpftool map list
    exit 1
fi

echo "✅ Found map ID: $MAP_ID"
echo ""

# Threat scores based on Base-60 harmonics
declare -A SCORES=(
    # Highly composite (low threat - harmonic)
    [1]=30 [2]=35 [3]=40 [4]=35 [5]=40
    [6]=30 [10]=30 [12]=25 [15]=30 [20]=30
    [24]=25 [30]=20 [60]=15
    
    # Primes (high threat - dissonant)
    [7]=60 [11]=65 [13]=65 [17]=60 [19]=60
    [23]=65 [29]=60 [31]=65 [37]=60 [41]=60
    [43]=65 [47]=60 [53]=60 [59]=65
    
    # Semi-primes and others (medium)
    [9]=45 [14]=45 [21]=45 [22]=45 [25]=45
    [26]=45 [27]=45 [33]=45 [34]=45 [35]=45
    [38]=45 [39]=45 [46]=45 [49]=45 [51]=45
    [55]=45 [57]=45 [58]=45
)

DEFAULT_SCORE=50

# Update map
for residue in {0..59}; do
    score=${SCORES[$residue]:-$DEFAULT_SCORE}
    
    # Convert to hex (little-endian, 4 bytes each)
    key_hex=$(printf "%02x 00 00 00" $residue)
    value_hex=$(printf "%02x 00 00 00" $score)
    
    echo -n "Residue $residue → Score $score ... "
    
    ERROR=$(sudo bpftool map update id $MAP_ID key hex $key_hex value hex $value_hex 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅"
    else
        echo "❌ ($ERROR)"
        # Don't exit, continue with next residue
    fi
done

echo ""
echo "✅ All 60 Base-60 threat scores initialized!"
echo ""
echo "Verification (first 10 entries):"
sudo bpftool map dump id $MAP_ID 2>/dev/null | head -15
