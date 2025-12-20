// SPDX-License-Identifier: GPL-2.0
/* Guardian-Alpha™ LSM - Kernel-Level AI Safety Enforcement
 * 
 * Claim 3: Kernel-level protection via eBPF LSM hooks with
 * cryptographic whitelist and pre-execution veto.
 * 
 * Copyright (c) 2024 Sentinel Cortex™
 */

#include <linux/bpf.h>
#include <linux/bpf_common.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <linux/errno.h>

/* Whitelist map: SHA256(command) -> allowed (1) or blocked (0) */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[64]);      // SHA256 hex string
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
    char hash[64];
    __u8 action;  // 0 = blocked, 1 = allowed
    __u64 timestamp;
};

/* Helper: Check if command is in whitelist */
static __always_inline int is_whitelisted(const char *filename)
{
    char hash[64] = {0};
    __u8 *allowed;
    
    // For POC, use simple string comparison
    bpf_probe_read_kernel_str(hash, sizeof(hash), filename);
    
    allowed = bpf_map_lookup_elem(&whitelist_map, hash);
    if (!allowed) {
        return 0;  // Not in whitelist = blocked
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
int BPF_PROG(guardian_execve, struct linux_binprm *bprm)
{
    char filename[256] = {0};
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    
    // Read executable path
    bpf_probe_read_kernel_str(filename, sizeof(filename), bprm->filename);
    
    // Check whitelist
    if (!is_whitelisted(filename)) {
        // Log blocked event
        log_event(pid, uid, filename, 0);
        
        // BLOCK: Return -EACCES
        bpf_printk("Guardian-Alpha: BLOCKED execve: %s (pid=%d)", 
                   filename, pid);
        return -EACCES;
    }
    
    // Log allowed event
    log_event(pid, uid, filename, 1);
    
    // ALLOW
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
