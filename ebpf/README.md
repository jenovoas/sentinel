# eBPF LSM Guardian - Security Interception Layer

## 🎯 Overview
This component provides kernel-level security enforcement using Linux Security Module (LSM) hooks via eBPF. It intercepts critical system operations (such as `execve`) to apply security policies before the operation is allowed to proceed.

## 📁 Component Structure

```
ebpf/
├── guardian_alpha_lsm.c       # eBPF LSM program (intercepts execve)
├── Makefile                   # Build system
├── load.sh                    # Loading and pinning script
├── watchdog_service.py        # System health monitor
└── README.md                  # This file
```

## ⚙️ Functional Description
The Guardian operates in kernel space (Ring 0) and implements:
1. **Syscall Interception**: Pre-execution veto of system calls.
2. **Policy Enforcement**: Validation of operations against a maintained policy map.
3. **Audit Telemetry**: Generation of security event logs via BPF Ring Buffer.
4. **Resilience**: Integrated monitoring to ensure the security layer remains active.

## 🔬 Technical Architecture

### eBPF LSM Hook
The primary hook used is `lsm/bprm_check_security`, which provides the ability to inspect binary parameters before execution.

```c
SEC("lsm/bprm_check_security")
int BPF_PROG(guardian_execve, struct linux_binprm *bprm)
{
    // Implementation logic for binary inspection
    // Return -EACCES to deny execution
}
```

### Policy Map
A hash map used to store allow/deny decisions for specific binary hashes or paths.

```c
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[64]);      
    __type(value, __u8);        
} policy_map;
```

## 🚀 Deployment

### Prerequisites
- Linux Kernel >= 5.7 with `CONFIG_BPF_LSM=y`
- `clang`, `llvm`, `libbpf`, and `bpftool` installed.

### Build and Load
```bash
make
sudo ./load.sh
```

## 📊 Performance and Characteristics
- **Latency**: Interception overhead is typically < 10 microseconds.
- **Enforcement**: Ring 0 execution ensures the security layer cannot be disabled from unprivileged user space.
- **Reliability**: Use of systemd watchdogs or external monitors to ensure continuity of service.

---
**Status**: Stable / Integrated  
**Last Update**: January 2026
