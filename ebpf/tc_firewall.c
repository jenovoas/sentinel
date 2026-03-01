#include "vmlinux.h"
#include <bpf/bpf_endian.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

// Constantes definidas directamente (vmlinux.h ya tiene las estructuras)
#define ETH_P_IP 0x0800
#define TC_ACT_OK 0
#define TC_ACT_SHOT 2

/* Blacklist Map: IPv4 Addr (u32) -> Flag (u8) */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u32);   // Source IP
    __type(value, u8);  // 1 = Blocked
} blacklist SEC(".maps");

/* Configuration Map: Global System State */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, u32);
    __type(value, u32);  // 0=Normal, 1=Panic/Quarantine
} config_map SEC(".maps");

/* Event Map for Userspace Communication */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} tc_events SEC(".maps");

struct dropped_packet {
    u32 src_ip;
    u32 dst_ip;
    u64 timestamp;
};

// TC BPF program
SEC("tc")
int tc_firewall_prog(struct __sk_buff *ctx) {
    // 0. Reflex Arc: Check Panic Mode first
    u32 key = 0;
    u32 *mode = bpf_map_lookup_elem(&config_map, &key);
    if (mode && *mode == 1) {
        return TC_ACT_SHOT;  // SYSTEM SEALED: Total Quarantine
    }

    // Load packet data
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    // Parse Ethernet header (14 bytes)
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return TC_ACT_OK;

    // Only process IPv4 packets
    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return TC_ACT_OK;

    // Parse IPv4 header
    struct iphdr *iph = data + sizeof(struct ethhdr);
    if ((void *)(iph + 1) > data_end)
        return TC_ACT_OK;

    // Get source IP
    u32 src_ip = iph->saddr;
    u32 dst_ip = iph->daddr;

    // Check Blacklist
    u8 *blocked = bpf_map_lookup_elem(&blacklist, &src_ip);

    if (blocked && *blocked == 1) {
        // Submit event to ring buffer
        struct dropped_packet *event;
        event = bpf_ringbuf_reserve(&tc_events, sizeof(*event), 0);
        if (event) {
            event->src_ip = src_ip;
            event->dst_ip = dst_ip;
            event->timestamp = bpf_ktime_get_ns();
            bpf_ringbuf_submit(event, 0);
        }

        return TC_ACT_SHOT;
    }

    return TC_ACT_OK;
}

char LICENSE[] SEC("license") = "GPL";
