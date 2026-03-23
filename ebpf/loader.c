#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <errno.h>
#include <linux/limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char **argv) {
  struct bpf_object *obj = NULL;
  struct bpf_link *link = NULL;
  struct bpf_program *prog;
  struct bpf_map *map;
  int err;
  char pin_dir[PATH_MAX];
  char pin_path[PATH_MAX];

  if (argc < 3) {
    fprintf(stderr, "Usage: %s <obj_file> <pin_dir>\n", argv[0]);
    return 1;
  }

  const char *filename = argv[1];
  const char *base_pin_dir = argv[2];

  // Create pin directory if it doesn't exist
  if (access(base_pin_dir, F_OK) == -1) {
    if (mkdir(base_pin_dir, 0755) < 0 && errno != EEXIST) {
      fprintf(stderr, "ERROR: creating dir %s failed: %s\n", base_pin_dir,
              strerror(errno));
      return 1;
    }
  }

  // Open and load the BPF object file
  obj = bpf_object__open_file(filename, NULL);
  if (libbpf_get_error(obj)) {
    fprintf(stderr, "ERROR: opening BPF object file failed\n");
    return 1;
  }

  // Load the program into the kernel
  err = bpf_object__load(obj);
  if (err) {
    fprintf(stderr, "ERROR: loading BPF object file failed: %d\n", err);
    goto cleanup;
  }

  // Pin all maps
  bpf_object__for_each_map(map, obj) {
    const char *map_name = bpf_map__name(map);
    
    // Skip special maps
    if (strstr(map_name, ".rodata") || strstr(map_name, ".bss") || strstr(map_name, ".data")) {
      continue;
    }
    snprintf(pin_path, sizeof(pin_path), "%s/%s", base_pin_dir, map_name);

    // Unpin if exists (to overwrite)
    unlink(pin_path);

    err = bpf_map__pin(map, pin_path);
    if (err) {
      fprintf(stderr, "ERROR: pinning map %s to %s failed: %d\n", map_name,
              pin_path, err);
      goto cleanup;
    }
    printf("Pinned map: %s\n", pin_path);
  }

  // Find the LSM program
  prog = bpf_object__find_program_by_name(obj, "guardian_cognitive");
  if (!prog) {
    fprintf(stderr, "ERROR: finding program failed\n");
    goto cleanup;
  }

  // Attach the LSM program
  link = bpf_program__attach_lsm(prog);
  if (libbpf_get_error(link)) {
    fprintf(stderr, "ERROR: attaching LSM program failed: %ld\n",
            libbpf_get_error(link));
    goto cleanup;
  }

  // Pin the link
  snprintf(pin_path, sizeof(pin_path), "%s/guardian_link", base_pin_dir);
  unlink(pin_path); // Remove old link pin
  err = bpf_link__pin(link, pin_path);
  if (err) {
    fprintf(stderr, "ERROR: pinning link to %s failed: %d\n", pin_path, err);
    goto cleanup;
  }

  printf("Successfully loaded, attached, and pinned LSM program!\n");

  // We can exit now, the link is pinned.
  return 0;

cleanup:
  if (link)
    bpf_link__destroy(link);
  bpf_object__close(obj);
  return 1;
}
