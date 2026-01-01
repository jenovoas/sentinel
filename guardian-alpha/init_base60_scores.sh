#!/bin/bash
# Initialize base60_threat_scores map with harmonic values
# Primes = higher threat, highly composite = lower threat

echo "🔢 Initializing Base-60 Threat Scores..."
echo ""

# Highly composite numbers (low threat)
declare -A SCORES=(
    [1]=30    # Neutral
    [2]=35
    [3]=40
    [4]=35
    [5]=40
    [6]=30    # Highly composite
    [10]=30
    [12]=25   # Highly composite (many divisors)
    [15]=30
    [20]=30
    [24]=25   # Highly composite
    [30]=20   # Highly composite
    [60]=15   # Most divisors (highly harmonic)
    
    # Prime numbers (higher threat - dissonant)
    [7]=60
    [11]=65
    [13]=65
    [17]=60
    [19]=60
    [23]=65
    [29]=60
    [31]=65
    [37]=60
    [41]=60
    [43]=65
    [47]=60
    [53]=60
    [59]=65
    
    # Semi-primes and others (medium threat)
    [9]=45
    [14]=45
    [21]=45
    [22]=45
    [25]=45
    [26]=45
    [27]=45
    [33]=45
    [34]=45
    [35]=45
    [38]=45
    [39]=45
    [46]=45
    [49]=45
    [51]=45
    [55]=45
    [57]=45
    [58]=45
)

# Default for unspecified residues
DEFAULT_SCORE=50

# Update map
for residue in {0..59}; do
    score=${SCORES[$residue]:-$DEFAULT_SCORE}
    
    # Convert to hex for bpftool (little-endian)
    key_hex=$(printf "%02x 00 00 00" $residue)
    value_hex=$(printf "%02x 00 00 00" $score)
    
    echo "Residue $residue → Score $score"
    sudo bpftool map update name base60_threat_scores \
        key hex $key_hex \
        value hex $value_hex 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Failed to update residue $residue (map may not exist)"
        exit 1
    fi
done

echo ""
echo "✅ Base-60 threat scores initialized!"
echo ""
echo "Verification (first 10 entries):"
sudo bpftool map dump name base60_threat_scores 2>/dev/null | head -15
