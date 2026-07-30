#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
  if (argc < 3) {
    fprintf(stderr, "Usage: %s <pinned_prog_path> <pinned_link_path>\n", argv[0]);
    return 1;
  }
  const char *prog_path = argv[1];
  const char *link_path = argv[2];
  int prog_fd = bpf_obj_get(prog_path);
  if (prog_fd < 0) {
    fprintf(stderr, "ERROR: failed to open pinned program '%s': %d\n", prog_path, errno);
    return 1;
  }
  int link_fd = bpf_link_create(prog_fd, 0, BPF_LSM_MAC, NULL);
  if (link_fd < 0) {
    fprintf(stderr, "ERROR: failed to attach LSM program: %d\n", errno);
    close(prog_fd);
    return 1;
  }
  unlink(link_path);
  if (bpf_link_pin(link_fd, link_path) != 0) {
    fprintf(stderr, "ERROR: failed to pin link: %d\n", errno);
    close(link_fd);
    close(prog_fd);
    return 1;
  }
  printf("✅ Attached and pinned to %s\n", link_path);
  close(link_fd);
  close(prog_fd);
  return 0;
}
