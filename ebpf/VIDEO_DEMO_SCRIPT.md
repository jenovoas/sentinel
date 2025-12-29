# 🎬 Video Demo Script: Guardian-Alpha eBPF Protection

**Goal**: Demonstrate kernel-level blocking of unauthorized execution (AIOps hallucination scenario).
**Duration**: 1-2 minutes.

---

## 1. Preparation

Open **two** terminal windows (split screen preferred):
*   **Terminal 1 (Left)**: The attacker/demo console.
*   **Terminal 2 (Right)**: The kernel log monitor (`dmesg`).

**Terminal 2 Setup (Monitor):**
Run this to follow kernel logs in real-time:
```bash
sudo dmesg -w | grep "Guardian-Alpha"
```

**Terminal 1 Setup (Action):**
Navigate to the eBPF directory:
```bash
cd ~/sentinel/ebpf
clear
```

---

## 2. Recording Sequence

**[START RECORDING]**

### Step 1: Show Protection Status
Run the check to show it's active.
```bash
# Type clearly:
sudo bpftool prog show | grep guardian
```
*(Explain: "The Guardian-Alpha eBPF module is loaded in the kernel.")*

### Step 2: Show the Benchmark Results
Quickly cat recent results to prove performance.
```bash
cat BENCHMARK_REPORT.md | head -n 15
```
*(Explain: "We have confirmed strictly <1ms overhead for all system calls.")*

### Step 3: The Attack Simulation
Run the demo script which simulates an AI hallucination trying to run an unauthorized repair script.
```bash
# Type clearly:
./demo_aiopsdoom_blocked.sh
```

**[What happens]**:
1.  Script simulates AI recommending `rm -rf`.
2.  Script tries to run `/tmp/ai_hallucinated_fix.sh`.
3.  **Terminal 1**: Shows "✅ BLOCKED: Unauthorized execution intercepted".
4.  **Terminal 2**: Logs show `Guardian-Alpha [CRITICAL]: BLOCKED execution ...`.

### Step 4: Closing
Show that the critical data was NOT deleted.
```bash
ls -l /tmp/test_critical_data
```
*(Show the file `important.txt` is still there)*.

**[STOP RECORDING]**
