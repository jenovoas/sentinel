// SPDX-License-Identifier: GPL-2.0
/* Guardian-Alpha LSM - Kernel-Level Process Execution Control
 * 
 * ME-60OS Security Module - Ring 0 Guardian
 * 
 * PURPOSE:
 * - Pre-execution veto for unverified binaries
 * - Whitelist-based access control at LSM hook level
 * - Audit trail via ring buffer for userspace monitoring
 * 
 * ARCHITECTURE:
 * - Hook: bprm_check_security (intercepts execve syscall)
 * - Policy: FAIL-CLOSED (not in whitelist = blocked)
 * - Logging: Ring buffer (256KB) for event streaming
 * 
 * Copyright (c) 2024-2026 ME-60OS Development Team
 */

#include "guardian_core.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

/* Path buffer size (aligned to eBPF limits) */
#define PATH_MAX 256

/* Whitelist map: Full path string -> allowed (1) or blocked (0) */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[PATH_MAX]);     /* Full path */
    __type(value, __u8);             /* 1 = allowed */
} whitelist_map SEC(".maps");

/* Event log map: ring buffer for audit trail to userspace */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);  /* 256KB buffer */
} events SEC(".maps");

/* Event structure for audit trail */
struct guardian_event {
    __u32 pid;              /* Process ID */
    __u32 uid;              /* User ID */
    __u64 timestamp_ns;     /* Nanosecond timestamp (entero) */
    __u8 action;            /* 0 = blocked, 1 = allowed */
    __u8 reserved[3];       /* Alignment padding */
    char filename[PATH_MAX]; /* Executed binary path */
};

/* Helper: Check if binary path is whitelisted
 * 
 * Returns:
 *   1 = allowed (in whitelist)
 *   0 = blocked (not in whitelist or lookup failed)
 */
static __always_inline int is_whitelisted(const char *path)
{
    __u8 *allowed;
    char key[PATH_MAX];
    int i;
    
    /* Initialize key buffer to zeros (eBPF verifier requirement) */
    /* Use __builtin_memset is safer/faster if available, loop is portable */
    for (i = 0; i < PATH_MAX; i++) {
        key[i] = 0;
    }
    
    /* Read the filename/path into the key buffer */
    long ret = bpf_probe_read_kernel_str(key, sizeof(key), path);
    if (ret < 0) {
        /* Read failed - fail closed */
        return 0;
    }
    
    /* Lookup in whitelist map */
    allowed = bpf_map_lookup_elem(&whitelist_map, key);
    if (!allowed) {
        /* FAIL-CLOSED: Not in whitelist = blocked */
        return 0;
    }
    
    return *allowed;
}

/* Helper: Log event to ring buffer for userspace consumption
 * 
 * Events are consumed by userspace daemon for:
 * - Security monitoring
 * - Audit logging
 * - Alerting on blocked executions
 */
static __always_inline void log_event(__u32 pid, __u32 uid, 
                                      const char *filename, 
                                      __u8 action)
{
    struct guardian_event *e;
    
    /* Reserve space in ring buffer */
    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) {
        /* Ring buffer full - event dropped (non-fatal) */
        return;
    }
    
    /* Populate event structure */
    e->pid = pid;
    e->uid = uid;
    e->action = action;
    e->timestamp_ns = bpf_ktime_get_ns();  /* Entero puro (nanosegundos) */
    e->reserved[0] = 0;
    e->reserved[1] = 0;
    e->reserved[2] = 0;
    
    /* Copy filename (bounded by eBPF verifier) */
    bpf_probe_read_kernel_str(e->filename, sizeof(e->filename), filename);
    
    /* Submit event to userspace */
    bpf_ringbuf_submit(e, 0);
}

/* LSM Hook: Intercept binary execution (execve syscall)
 * 
 * HOOK POINT: bprm_check_security
 * TIMING: After binary is loaded, before execution starts
 * POLICY: Whitelist-based FAIL-CLOSED
 * 
 * Returns:
 *   0 = Allow execution
 *   -EACCES = Deny execution (permission denied)
 */
SEC("lsm/bprm_check_security")
int BPF_PROG(guardian_execve, struct linux_binprm *bprm, int ret)
{
    const char *filename;
    __u32 pid;
    __u32 uid;
    int whitelisted;
    
    /* If a previous LSM already denied access, respect it */
    if (ret != 0) {
        return ret;
    }
    
    /* Extract process metadata */
    pid = bpf_get_current_pid_tgid() >> 32;
    uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    
    /* Get the filename being executed (using BPF CO-RE) */
    filename = BPF_CORE_READ(bprm, filename);
    if (!filename) {
        /* Failed to read filename - fail closed */
        bpf_printk("Guardian-Alpha [ERROR]: Failed to read filename (pid=%d)", pid);
        return -EACCES;
    }
    
    /* Debug trace (visible in /sys/kernel/debug/tracing/trace_pipe) */
    bpf_printk("Guardian-Alpha: Checking %s (pid=%d, uid=%d)", filename, pid, uid);
    
    /* Check whitelist (FAIL-CLOSED policy) */
    whitelisted = is_whitelisted(filename);
    
    if (!whitelisted) {
        /* BLOCKED - Not in whitelist */
        log_event(pid, uid, filename, 0);
        
        /* Critical block message in kernel log */
        bpf_printk("Guardian-Alpha [BLOCK]: Denied execution of %s (uid=%d)", 
                   filename, uid);
        
        return -EACCES;  /* Permission denied */
    }
    
    /* ALLOWED - In whitelist */
    log_event(pid, uid, filename, 1);
    bpf_printk("Guardian-Alpha [ALLOW]: Verified binary %s", filename);
    
    return 0;  /* Success - allow execution */
}

/* BPF program metadata */
char LICENSE[] SEC("license") = "GPL";
char VERSION[] SEC("version") = "1.0.0";

/* Version and build info for userspace */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u64);
} build_info SEC(".maps");