// SPDX-License-Identifier: GPL-2.0
/*
 * ME-60OS LSM Attach Utility
 * 
 * Purpose: Attach LSM eBPF program to kernel
 * Usage: ./lsm_attach <pinned_prog_path> <pinned_link_path>
 * 
 * Copyright (c) 2026 ME-60OS Development Team
 */

#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
  if (argc < 3) {
    fprintf(stderr, "Usage: %s <pinned_prog_path> <pinned_link_path>\n",
            argv[0]);
    fprintf(stderr, "\nExample:\n");
    fprintf(stderr, "  %s /sys/fs/bpf/guardian_lsm /sys/fs/bpf/guardian_link\n",
            argv[0]);
    return 1;
  }

  const char *prog_path = argv[1];
  const char *link_path = argv[2];

  // Get file descriptor for the pinned program
  int prog_fd = bpf_obj_get(prog_path);
  if (prog_fd < 0) {
    fprintf(stderr, "ERROR: failed to open pinned program '%s': %d\n",
            prog_path, errno);
    return 1;
  }

  // Attach the program using BPF_LINK_CREATE
  // For LSM, attach_type is BPF_LSM_MAC
  // target_fd is 0 for LSM
  int link_fd = bpf_link_create(prog_fd, 0, BPF_LSM_MAC, NULL);
  if (link_fd < 0) {
    fprintf(stderr, "ERROR: failed to attach LSM program: %d\n", errno);
    close(prog_fd);
    return 1;
  }

  // Pin the link to keep it active
  // Delete existing pin if any
  unlink(link_path);

  int err = bpf_obj_pin(link_fd, link_path);
  if (err) {
    fprintf(stderr, "ERROR: failed to pin link to '%s': %d\n", link_path,
            errno);
    close(link_fd);
    close(prog_fd);
    return 1;
  }

  printf("✅ Successfully attached and pinned LSM link!\n");
  printf("   Program: %s\n", prog_path);
  printf("   Link: %s\n", link_path);

  close(link_fd);
  close(prog_fd);
  return 0;
}
