# Implementation Plan - Claim 6: Cognitive Kernel POC

**Goal**: Validate Claim 6 (Cognitive Operating System Kernel) by implementing "Semantic Verification at Ring 0".

## Problem Description
Current implementations (Claim 3) rely on a static binary whitelist. While secure, this is "blind" to the *context* and *arguments* of the execution.
- `rm` is whitelisted (essential tool).
- `rm /tmp/junk` -> SAFE (should be allowed).
- `rm -rf /` -> MALICIOUS (should be blocked).

Traditional kernels cannot distinguish these. The "Cognitive Kernel" must understand the *intent* by analyzing arguments.

## Proposed Changes

### 1. New eBPF Program (`ebpf/guardian_cognitive.c`)
Create a new eBPF LSM module that extends `guardian_alpha_lsm.c` with:
- **Argument Access**: Use `bpf_bprm_opts` or `bpf_probe_read_user` to access command line arguments.
- **Semantic Pattern Matching**: Implement a lightweight "Micro-LLM" logic (heuristics) in C to detect destructive patterns.
    - Pattern 1: `rm` + `-rf` (Recursive Force delete)
    - Pattern 2: Target is `/` (Root directory) or Critical Paths.

### 2. User-Space Cognitive Engine (`ebpf/cognitive_daemon.py`) (Optional for basic POC)
- A daemon to update the "Semantic Rules Map".
- For this POC, we will hardcode the rules in eBPF or use a BPF Map for "Bad Patterns" to demonstrate dynamic updates.

### 3. Verification Script (`ebpf/test_cognitive.sh`)
- TestCase 1: `rm /tmp/testfile` -> ✅ ALLOWED
- TestCase 2: `rm -rf /tmp/testcritical` -> ❌ BLOCKED (Cognitive Block)

## Technical Challenges (eBPF Limitations)
- **Argument Limits**: Reading `argv` in eBPF has limits (loops, stack size). We will limit check to first 3 arguments and 64 bytes for POC.
- **Loop Unrolling**: eBPF verifier doesn't like infinite loops. We must unroll string comparison.

## Verification Plan

### Automated Tests
- `ebpf/test_cognitive.sh`

### Manual Verification
- Run destructive command Proyección Cuántica and observe "Cognitive Block" in dmesg.

## Success Criteria
- [ ] `rm` is allowed generally.
- [ ] `rm -rf /...` is specifically blocked.
- [ ] Latency remains < 1ms.
