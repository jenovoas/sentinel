// SPDX-License-Identifier: GPL-2.0
/*
 * Sentinel Cortex™ - Burst Sensor (eBPF XDP)
 * 
 * Purpose: Detect incoming traffic bursts and signal to userspace
 * Part of: Cognitive OS Kernel - Proof of Concept
 * Claim: Guardian Beta (eBPF) feeding Guardian Alpha (LSTM)
 * 
 * Copyright (c) 2025 Sentinel Cortex™ - All Rights Reserved
 */

#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

/* Ring buffer for sending events to userspace */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); // 256KB ring buffer
} burst_events SEC(".maps");

/* Per-CPU packet counter */
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, __u32);
    __type(value, __u64);
    __uint(max_entries, 1);
} pkt_count SEC(".maps");

/* Timestamp of last check */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __type(key, __u32);
    __type(value, __u64);
    __uint(max_entries, 1);
} last_check SEC(".maps");

/* Burst event structure */
struct burst_event {
    __u64 timestamp;      // Nanoseconds since boot
    __u64 pps;            // Packets per second
    __u32 burst_detected; // 1 if burst, 0 if normal
    __u32 severity;       // 0=low, 1=medium, 2=high, 3=critical
};

/* Configuration */
#define BURST_THRESHOLD_LOW     1000    // 1K pps
#define BURST_THRESHOLD_MEDIUM  10000   // 10K pps
#define BURST_THRESHOLD_HIGH    50000   // 50K pps
#define BURST_THRESHOLD_CRITICAL 100000 // 100K pps
#define CHECK_INTERVAL_NS       1000000000ULL // 1 second

SEC("xdp")
int detect_burst(struct xdp_md *ctx)
{
    __u32 key = 0;
    __u64 *count, *last_ts;
    __u64 now, elapsed_ns, pps;
    struct burst_event *event;
    
    // Get current timestamp (nanoseconds since boot)
    now = bpf_ktime_get_ns();
    
    // Increment packet counter
    count = bpf_map_lookup_elem(&pkt_count, &key);
    if (!count) {
        return XDP_PASS;
    }
    __sync_fetch_and_add(count, 1);
    
    // Check if it's time to calculate PPS
    last_ts = bpf_map_lookup_elem(&last_check, &key);
    if (!last_ts) {
        return XDP_PASS;
    }
    
    elapsed_ns = now - *last_ts;
    
    // Only check every CHECK_INTERVAL_NS (1 second)
    if (elapsed_ns < CHECK_INTERVAL_NS) {
        return XDP_PASS;
    }
    
    // Calculate packets per second
    // PPS = (packets * 1,000,000,000) / elapsed_ns
    pps = (*count * 1000000000ULL) / elapsed_ns;
    
    // Determine severity
    __u32 severity = 0;
    __u32 burst_detected = 0;
    
    if (pps >= BURST_THRESHOLD_CRITICAL) {
        severity = 3;
        burst_detected = 1;
    } else if (pps >= BURST_THRESHOLD_HIGH) {
        severity = 2;
        burst_detected = 1;
    } else if (pps >= BURST_THRESHOLD_MEDIUM) {
        severity = 1;
        burst_detected = 1;
    } else if (pps >= BURST_THRESHOLD_LOW) {
        severity = 0;
        burst_detected = 1;
    }
    
    // Send event to userspace if burst detected
    if (burst_detected) {
        event = bpf_ringbuf_reserve(&burst_events, sizeof(*event), 0);
        if (event) {
            event->timestamp = now;
            event->pps = pps;
            event->burst_detected = burst_detected;
            event->severity = severity;
            bpf_ringbuf_submit(event, 0);
        }
    }
    
    // Reset counter and timestamp
    *count = 0;
    *last_ts = now;
    
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
