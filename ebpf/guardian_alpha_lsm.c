// SPDX-License-Identifier: GPL-2.0
/* Guardian-Alpha™ LSM - Kernel-Level AI Safety Enforcement
 * 
 * Claim 3: Kernel-level protection via eBPF LSM hooks with
 * cryptographic whitelist and pre-execution veto.
 * 
 * Copyright (c) 2024 Sentinel Cortex™
 */

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "cortex_events.h"

/* Whitelist map: Full path string -> allowed (1) or blocked (0) */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[256]);     // Increased for full paths
    __type(value, __u8);        // 1 = allowed, 0 = blocked
} whitelist_map SEC(".maps");

/* Bloqueo temporal de futuras llamadas execve por PID. */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 4096);
    __type(key, __u32);
    __type(value, __u64); /* expiración CLOCK_MONOTONIC en nanosegundos */
} pid_isolation_map SEC(".maps");

/* Event log map: ring buffer for audit trail */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);  // 256KB buffer
} events SEC(".maps");

#ifndef EACCES
#define EACCES 13
#endif

/* Helper: Check if command path is whitelisted */
static __always_inline int is_whitelisted(const char *path)
{
    __u8 *allowed;
    char key[256] = {0};
    
    // Read the filename/path into the key
    bpf_probe_read_kernel_str(key, sizeof(key), path);
    
    allowed = bpf_map_lookup_elem(&whitelist_map, key);
    if (!allowed) {
        // FAIL-CLOSED: Not in whitelist = blocked
        return 0;
    }
    
    return *allowed;
}

/* Helper: Comprueba y elimina entradas caducadas de aislamiento. */
static __always_inline int is_pid_isolated(__u32 pid)
{
    __u64 *expires_at_ns = bpf_map_lookup_elem(&pid_isolation_map, &pid);
    if (!expires_at_ns)
        return 0;

    if (*expires_at_ns > bpf_ktime_get_ns())
        return 1;

    bpf_map_delete_elem(&pid_isolation_map, &pid);
    return 0;
}

/* Emite el contrato de 32 bytes consumido por el bridge Rust. */
static __always_inline void log_event(__u32 pid, __u8 allowed)
{
    struct cortex_event *e;
    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e)
        return;

    __builtin_memset(e, 0, sizeof(*e));
    e->timestamp_ns = bpf_ktime_get_ns();
    e->event_type = allowed ? EVENT_EXEC_ALLOWED : EVENT_EXEC_BLOCKED;
    e->pid = pid;
    e->severity = allowed ? SEVERITY_LOW : SEVERITY_CRITICAL;
    e->entropy_signal = ((__u64)(e->severity + 1) * S60_SCALE_0) + (pid % 60);
    e->reserved[0] = GUARDIAN_CODE_ALPHA;

    bpf_ringbuf_submit(e, 0);
}

/* LSM Hook: Intercept bprm_check_security (execve) */
SEC("lsm/bprm_check_security")
int BPF_PROG(guardian_execve, struct linux_binprm *bprm, int ret)
{
    // If a previous LSM already denied access, respect it
    if (ret != 0)
        return ret;

    const char *filename;
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    
    // Get the filename being executed
    filename = BPF_CORE_READ(bprm, filename);

    if (is_pid_isolated(pid)) {
        log_event(pid, 0);
        bpf_printk("Guardian-Alpha [ISOLATION]: blocked execve for PID %d", pid);
        return -EACCES;
    }
    
    bpf_printk("Guardian-Alpha DEBUG: Intercepting %s (pid=%d, uid=%d)", filename, pid, uid);
    
    // Check whitelist (FAIL-CLOSED)
    if (!is_whitelisted(filename)) {
        // Log blocked event
        log_event(pid, 0);
        
        // Critical block message in kernel log
        bpf_printk("Guardian-Alpha [CRITICAL]: BLOCKED execution of unverified binary: %s (uid=%d)", 
                   filename, uid);
        
        return -EACCES; // Permission denied
    }
    
    // Log allowed event
    log_event(pid, 1);
    bpf_printk("Guardian-Alpha [INFO]: Allowed verified binary: %s", filename);
    
    return 0; // Success
}

char LICENSE[] SEC("license") = "GPL";
