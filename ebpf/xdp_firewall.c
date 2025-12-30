#include "vmlinux.h"
#include <bpf/bpf_endian.h>
#include <bpf/bpf_helpers.h>

/* Define the Blacklist Map: IPv4 Addr (u32) -> Flag (u8) */
struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __uint(max_entries, 1024);
  __type(key, u32);  // Source IP
  __type(value, u8); // 1 = Blocked
} blacklist SEC(".maps");

/* Configuration Map: Global System State */
struct {
  __uint(type, BPF_MAP_TYPE_ARRAY);
  __uint(max_entries, 1);
  __type(key, u32);
  __type(value, u32); // 0=Normal, 1=Panic/Quarantine
} config_map SEC(".maps");

SEC("xdp")
int xdp_firewall_prog(struct xdp_md *ctx) {
  void *data_end = (void *)(long)ctx->data_end;
  void *data = (void *)(long)ctx->data;

  // 0. Reflex Arc: Check Panic Mode first (High Priority)
  u32 key = 0;
  u32 *mode = bpf_map_lookup_elem(&config_map, &key);
  if (mode && *mode == 1) {
    return XDP_DROP; // SYSTEM SEALED: Total Quarantine
  }

  // 1. Parse Ethernet Header
  struct ethhdr *eth = data;
  if ((void *)(eth + 1) > data_end)
    return XDP_PASS;

  // Only filter IPv4 packets
  // ETH_P_IP is 0x0800. In vmlinux.h it might be defined or we use literal.
  // vmlinux.h usually has enum generic constants.
  // Let's use 0x0800 directly or check if ETH_P_IP is available.
  // Usually it is not in vmlinux.h as a #define.
  // We use bpf_htons(0x0800).

  if (eth->h_proto != bpf_htons(0x0800))
    return XDP_PASS;

  // 2. Parse IP Header
  struct iphdr *ip = (void *)(eth + 1);
  if ((void *)(ip + 1) > data_end)
    return XDP_PASS;

  // 3. Check Blacklist
  u32 src_ip = ip->saddr;
  u8 *blocked = bpf_map_lookup_elem(&blacklist, &src_ip);

  if (blocked) {
    // bpf_printk("XDP: Dropped packet from %x\n", src_ip);
    return XDP_DROP;
  }

  return XDP_PASS;
}

char LICENSE[] SEC("license") = "GPL";
