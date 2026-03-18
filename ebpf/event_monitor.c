// SPDX-License-Identifier: GPL-2.0
/*
 * ME-60OS Event Monitor
 * 
 * Purpose: Consume eBPF RingBuffer events and output as JSON to stdout.
 * Bridge: Kernel RingBuffer -> Standard Output -> Python Adaptor
 * 
 * Copyright (c) 2026 ME-60OS Development Team
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>

#define MAX_ERR_LOG 256

// Must match struct burst_event in burst_sensor.c
struct burst_event {
    __u64 timestamp;
    __u64 pps;
    __u32 burst_detected;
    __u32 severity;
};

// Callback for ring buffer events
static int handle_event(void *ctx, void *data, size_t data_sz) {
    const struct burst_event *e = data;
    
    // Output JSON to stdout (flushed immediately)
    printf("{\"timestamp\": %llu, \"pps\": %llu, \"severity\": %u}\n",
           e->timestamp, e->pps, e->severity);
    fflush(stdout);
    
    return 0;
}

int main(int argc, char **argv) {
    struct bpf_object *obj = NULL;
    struct ring_buffer *rb = NULL;
    int map_fd;
    int err;

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <bpf_object_file>\n", argv[0]);
        return 1;
    }

    const char *filename = argv[1];

    // Open BPF object
    obj = bpf_object__open_file(filename, NULL);
    if (libbpf_get_error(obj)) {
        fprintf(stderr, "ERROR: opening BPF object file failed\n");
        return 1;
    }

    // Load BPF object (maps are created here)
    err = bpf_object__load(obj);
    if (err) {
        fprintf(stderr, "ERROR: loading BPF object failed: %d\n", err);
        goto cleanup;
    }

    // Find the ring buffer map
    map_fd = bpf_object__find_map_fd_by_name(obj, "burst_events");
    if (map_fd < 0) {
        fprintf(stderr, "ERROR: finding 'burst_events' map failed\n");
        goto cleanup;
    }

    // Set up ring buffer polling
    rb = ring_buffer__new(map_fd, handle_event, NULL, NULL);
    if (!rb) {
        fprintf(stderr, "ERROR: creating ring buffer failed\n");
        goto cleanup;
    }

    fprintf(stderr, "✅ Event Monitor started. Listening for bursts...\n");

    // Main polling loop
    while (1) {
        err = ring_buffer__poll(rb, 100 /* timeout ms */);
        if (err == -EINTR) {
            continue;
        }
        if (err < 0) {
            fprintf(stderr, "ERROR: polling ring buffer: %d\n", err);
            break;
        }
    }

cleanup:
    if (rb) ring_buffer__free(rb);
    if (obj) bpf_object__close(obj);
    return 0;
}
