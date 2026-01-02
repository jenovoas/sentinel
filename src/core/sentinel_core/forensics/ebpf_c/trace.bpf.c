#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct event_t {
  u32 pid;
  u32 _pad; // Explicit padding for 8-byte alignment of 'ts'
  u64 ts;
  char comm[16];
};

struct {
  __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
  __uint(key_size, sizeof(u32));
  __uint(value_size, sizeof(u32));
} suspicious_events SEC(".maps");

struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __uint(max_entries, 1024);
  __uint(key_size, sizeof(u32));
  __uint(value_size, sizeof(u8));
} freeze_commands SEC(".maps");

struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __uint(max_entries, 64);
  __uint(key_size, sizeof(u32));
  __uint(value_size, sizeof(u8));
} whitelist_uids SEC(".maps");

SEC("tracepoint/syscalls/sys_exit_execve")
int trace_exit_execve(struct trace_event_raw_sys_exit *ctx) {
  if (ctx->ret != 0)
    return 0; // Ignore failed execve calls

  u64 uid_gid = bpf_get_current_uid_gid();
  u32 uid = (u32)uid_gid;

  // Check if UID is in whitelist
  u8 *is_whitelisted = bpf_map_lookup_elem(&whitelist_uids, &uid);
  if (is_whitelisted) {
    return 0; // Never block whitelisted users
  }

  u32 pid = bpf_get_current_pid_tgid() >> 32;

  // Check if this PID is marked for freezing
  u8 *should_freeze = bpf_map_lookup_elem(&freeze_commands, &pid);
  if (should_freeze) {
    bpf_send_signal(19); // SIGSTOP (19 is SIGSTOP on x86_64)
    return 0;
  }

  u64 ts = bpf_ktime_get_ns();

  struct event_t event = {.pid = pid, .ts = ts, ._pad = 0};
  bpf_get_current_comm(&event.comm, sizeof(event.comm));

  bpf_perf_event_output(ctx, &suspicious_events, BPF_F_CURRENT_CPU, &event,
                        sizeof(event));
  return 0;
}

char _license[] SEC("license") = "GPL";
