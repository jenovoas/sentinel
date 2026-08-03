// SPDX-License-Identifier: GPL-2.0
/* Attach LSM program(s) from an object file to their hooks and pin the links.
 * Usage: ./attach_lsm <obj_file> <pin_dir> [prog_name ...]
 * If no prog_name given, attaches all lsm/* programs found.
 */
#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <errno.h>
#include <linux/limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char **argv) {
  if (argc < 3) {
    fprintf(stderr, "Usage: %s <obj_file> <pin_dir> [prog_name ...]\n", argv[0]);
    return 1;
  }
  char *obj_file = argv[1];
  char *pin_dir = argv[2];

  mkdir(pin_dir, 0755);

  struct bpf_object *obj = bpf_object__open_file(obj_file, NULL);
  if (libbpf_get_error(obj)) {
    fprintf(stderr, "ERROR opening %s\n", obj_file);
    return 1;
  }
  if (bpf_object__load(obj)) {
    fprintf(stderr, "ERROR loading %s\n", obj_file);
    return 1;
  }

  struct bpf_program *prog;
  int attached = 0;
  bpf_object__for_each_program(prog, obj) {
    if (bpf_program__type(prog) != BPF_PROG_TYPE_LSM)
      continue;
    const char *name = bpf_program__name(prog);
    // If specific names requested, filter
    if (argc > 3) {
      int found = 0;
      for (int i = 3; i < argc; i++)
        if (strcmp(argv[i], name) == 0) { found = 1; break; }
      if (!found) continue;
    }
    struct bpf_link *link = bpf_program__attach_lsm(prog);
    if (libbpf_get_error(link)) {
      fprintf(stderr, "ERROR attaching %s\n", name);
      continue;
    }
    char pin[PATH_MAX];
    snprintf(pin, sizeof(pin), "%s/%s_link", pin_dir, name);
    unlink(pin);
    if (bpf_link__pin(link, pin)) {
      fprintf(stderr, "ERROR pinning link %s\n", name);
      bpf_link__destroy(link);
      continue;
    }
    printf("Attached + pinned: %s -> %s\n", name, pin);
    attached++;
  }

  if (attached == 0) {
    fprintf(stderr, "No LSM programs attached\n");
    bpf_object__close(obj);
    return 1;
  }
  printf("Done: %d LSM program(s) attached.\n", attached);
  bpf_object__close(obj);
  return 0;
}
