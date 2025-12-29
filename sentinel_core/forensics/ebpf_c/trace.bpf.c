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

SEC("tracepoint/syscalls/sys_exit_execve")
int trace_exit_execve(struct trace_event_raw_sys_exit *ctx) {
  if (ctx->ret != 0)
    return 0; // Ignore failed execve calls

  u32 pid = bpf_get_current_pid_tgid() >> 32;
  u64 ts = bpf_ktime_get_ns();

  struct event_t event = {.pid = pid, .ts = ts, ._pad = 0};
  bpf_get_current_comm(&event.comm, sizeof(event.comm));

  bpf_perf_event_output(ctx, &suspicious_events, BPF_F_CURRENT_CPU, &event,
                        sizeof(event));
  return 0;
}

char _license[] SEC("license") = "GPL";
