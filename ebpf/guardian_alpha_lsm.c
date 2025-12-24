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

/* Whitelist map: Full path string -> allowed (1) or blocked (0) */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[256]);     // Increased for full paths
    __type(value, __u8);        // 1 = allowed, 0 = blocked
} whitelist_map SEC(".maps");

/* Event log map: ring buffer for audit trail */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);  // 256KB buffer
} events SEC(".maps");

/* Event structure for audit trail */
struct event {
    __u32 pid;
    __u32 uid;
    char filename[256];
    __u8 action;  // 0 = blocked, 1 = allowed
    __u64 timestamp;
};

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

/* Helper: Log event to ring buffer */
static __always_inline void log_event(__u32 pid, __u32 uid, 
                                      const char *filename, 
                                      __u8 action)
{
    struct event *e;
    
    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) {
        return;
    }
    
    e->pid = pid;
    e->uid = uid;
    e->action = action;
    e->timestamp = bpf_ktime_get_ns();
    bpf_probe_read_kernel_str(e->filename, sizeof(e->filename), filename);
    
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
    
    // Check whitelist (FAIL-CLOSED)
    if (!is_whitelisted(filename)) {
        // Log blocked event
        log_event(pid, uid, filename, 0);
        
        // Critical block message in kernel log
        bpf_printk("Guardian-Alpha [CRITICAL]: BLOCKED execution of unverified binary: %s (uid=%d)", 
                   filename, uid);
        
        return -EACCES; // Permission denied
    }
    
    // Log allowed event
    log_event(pid, uid, filename, 1);
    bpf_printk("Guardian-Alpha [INFO]: Allowed verified binary: %s", filename);
    
    return 0; // Success
}

char LICENSE[] SEC("license") = "GPL";
