# CPU Security Audit: Hardware Features

**Date**: December 31, 2025
**Host**: Sentinel Cortex Node-1

## Executive Summary
The host CPU **does not support** hardware-enforced Control-flow Enforcement Technology (CET) or Shadow Stacks. This means ROP (Return-Oriented Programming) and JOP (Jump-Oriented Programming) attacks must be mitigated via software controls (eBPF, ASLR, DEP).

## Findings

### 1. Intel CET / AMD Shadow Stack
- **Status**: ❌ NOT DETECTED
- **Flags searched**: `cet`, `ibt`, `shstk`
- **Result**: None present in `/proc/cpuinfo`.

### 2. Available Protections
The CPU *does* support the following standard extensions:
- **NX (No-Execute)**: Supported.
- **SMEP (Supervisor Mode Execution Prevention)**: ✅ Supported.
- **SMAP (Supervisor Mode Access Prevention)**: ✅ Supported.
- **SGX (Software Guard Extensions)**: ✅ Supported (`sgx`, `sgx_lc`).
- **MPX (Memory Protection Extensions)**: ✅ Supported.

## Recommendations / Compensating Controls

Since Hardware Shadow Stacks are unavailable, Sentinel Cortex relies on:

1.  **eBPF CFI (Control Flow Integrity)**:
    - *Status*: Implemented in `guardian-alpha`.
    - *Mechanism*: Monitoring `sys_execve` and `bprm_check` calls to detect anomalous parent-child relationships.

2.  **Semantic Threat Analysis (Phase 1)**:
    - *Status*: Implemented.
    - *Mechanism*: Pre-execution path analysis blocking known ROP chains or shellcode loaders (e.g., `| sh`).

3.  **Future Mitigation**:
    - Enable **Clang CFI** during compilation of eBPF programs.
    - Enforce **SafeStack** (software shadow stack) in Rust components (`truth_sync`).
