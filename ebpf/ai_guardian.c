// SPDX-License-Identifier: GPL-2.0
/*
 * ME-60OS AI Guardian - LSM Hook with Dynamic Whitelist
 * 
 * Blocks destructive syscalls BEFORE execution (Ring 0).
 * Specifically targets processes identified as AI agents.
 * 
 * Copyright (c) 2026 ME-60OS Development Team
 */

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "cortex_events.h"

#define PATH_MAX 256
#define ALLOW_AI 1
#define BLOCK_AI 0

#ifndef EPERM
#define EPERM 1
#endif

/* Map of AI agent PIDs (updatable from userspace) */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);    // PID
    __type(value, __u8);   // 1 = AI agent, 0 = normal
} ai_agents_map SEC(".maps");

/* Dynamic whitelist of paths (updatable without reboot) */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10000);
    __type(key, char[PATH_MAX]);  // Full Path
    __type(value, __u64);         // Policy ID (ALLOW_AI, BLOCK_AI)
} ai_whitelist_map SEC(".maps");

/* Block/Allow Statistics */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 3);
    __type(key, __u32);
    __type(value, __u64);
} stats_map SEC(".maps");

#define STAT_CHECKS 0
#define STAT_BLOCKS 1
#define STAT_ALLOWS 2

/* Ring Buffer for Cortex Events (Kernel → Userspace) */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256KB buffer
} cortex_events SEC(".maps");

/*
 * Helper: Calculate S60 Entropy Signal from Path
 * 
 * Simple hash-based entropy calculation.
 * Maps path characteristics to S60 raw value.
 * 
 * S60::SCALE_0 = 46656000000 (base unit)
 * High entropy (blocked) = 0.85 * SCALE_0 = 39657600000
 * Low entropy (allowed)  = 0.15 * SCALE_0 = 6998400000
 */
static __always_inline __u64 calculate_entropy_s60(const char *path, int blocked)
{
    const __u64 SCALE_0 = 46656000000ULL;
    
    if (blocked) {
        // High entropy: S60(0, 51, 0) = 0.85
        return (SCALE_0 * 85) / 100;
    } else {
        // Low entropy: S60(0, 9, 0) = 0.15
        return (SCALE_0 * 15) / 100;
    }
}

/*
 * Helper: Send Event to Cortex via Ring Buffer
 */
static __always_inline void send_cortex_event(
    __u32 event_type,
    __u32 pid,
    __u64 entropy_signal,
    __u8 severity)
{
    struct cortex_event *e;
    
    e = bpf_ringbuf_reserve(&cortex_events, sizeof(*e), 0);
    if (!e) {
        // Ring buffer full, drop event (non-blocking)
        return;
    }
    
    e->timestamp_ns = bpf_ktime_get_ns();
    e->event_type = event_type;
    e->pid = pid;
    e->entropy_signal = entropy_signal;
    e->severity = severity;
    
    bpf_ringbuf_submit(e, 0);
}


/*
 * LSM Hook: file_open
 * 
 * Executed BEFORE the kernel opens a file.
 * Logic:
 * 1. Check if current process is an AI agent.
 * 2. Get file path.
 * 3. Check path against dynamic whitelist.
 * 4. Return -EPERM if not allowed.
 */
SEC("lsm/file_open")
int BPF_PROG(me60os_ai_guardian_open, struct file *file)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u8 *is_ai;
    char path[PATH_MAX];
    __u64 *policy;
    __u32 key;
    __u64 *count;
    
    // 1. Check if process is marked as AI agent
    is_ai = bpf_map_lookup_elem(&ai_agents_map, &pid);
    if (!is_ai || *is_ai == 0) {
        // Not an AI agent, allow operation
        return 0;
    }
    
    // 2. Get file path
    bpf_d_path(&file->f_path, path, sizeof(path));
    
    // 3. Check dynamic whitelist
    policy = bpf_map_lookup_elem(&ai_whitelist_map, path);
    
    // 4. Update stats
    key = STAT_CHECKS;
    count = bpf_map_lookup_elem(&stats_map, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    // 5. Deterministic decision
    if (!policy || *policy != ALLOW_AI) {
        // Path NOT in whitelist or explicitly blocked
        key = STAT_BLOCKS;
        count = bpf_map_lookup_elem(&stats_map, &key);
        if (count) __sync_fetch_and_add(count, 1);
        
        // Log blocked event
        bpf_printk("ME-60OS AI_GUARDIAN: BLOCKED file_open pid=%d path=%s", pid, path);
        
        // Send to Cortex: High entropy (threat detected)
        __u64 entropy = calculate_entropy_s60(path, 1);
        send_cortex_event(EVENT_FILE_BLOCKED, pid, entropy, SEVERITY_HIGH);
        
        return -EPERM;  // Operation not permitted
    }
    
    // Allow (found in whitelist)
    key = STAT_ALLOWS;
    count = bpf_map_lookup_elem(&stats_map, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    // Send to Cortex: Low entropy (normal operation)
    __u64 entropy = calculate_entropy_s60(path, 0);
    send_cortex_event(EVENT_FILE_ALLOWED, pid, entropy, SEVERITY_LOW);
    
    return 0;
}

/*
 * LSM Hook: bprm_check_security
 * 
 * Executed BEFORE the kernel executes a binary.
 */
SEC("lsm/bprm_check_security")
int BPF_PROG(me60os_ai_guardian_exec, struct linux_binprm *bprm)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u8 *is_ai;
    char path[PATH_MAX];
    __u64 *policy;
    __u32 key;
    __u64 *count;
    
    // 1. Check if process is marked as AI agent
    is_ai = bpf_map_lookup_elem(&ai_agents_map, &pid);
    if (!is_ai || *is_ai == 0) {
        return 0;
    }
    
    // 2. Get binary path
    bpf_probe_read_kernel_str(path, sizeof(path), bprm->filename);
    
    // 3. Check dynamic whitelist
    policy = bpf_map_lookup_elem(&ai_whitelist_map, path);
    
    // 4. Update stats
    key = STAT_CHECKS;
    count = bpf_map_lookup_elem(&stats_map, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    // 5. Deterministic decision
    if (!policy || *policy != ALLOW_AI) {
        key = STAT_BLOCKS;
        count = bpf_map_lookup_elem(&stats_map, &key);
        if (count) __sync_fetch_and_add(count, 1);
        
        bpf_printk("ME-60OS AI_GUARDIAN: BLOCKED exec pid=%d binary=%s", pid, path);
        
        // Send to Cortex: Critical severity (exec blocked)
        __u64 entropy = calculate_entropy_s60(path, 1);
        send_cortex_event(EVENT_EXEC_BLOCKED, pid, entropy, SEVERITY_CRITICAL);
        
        return -EPERM;
    }
    
    key = STAT_ALLOWS;
    count = bpf_map_lookup_elem(&stats_map, &key);
    if (count) __sync_fetch_and_add(count, 1);
    
    // Send to Cortex: Normal exec allowed
    __u64 entropy = calculate_entropy_s60(path, 0);
    send_cortex_event(EVENT_EXEC_ALLOWED, pid, entropy, SEVERITY_LOW);
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
