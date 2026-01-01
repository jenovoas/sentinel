#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

// Match kernel struct
struct threat_decision {
  unsigned int pid;
  unsigned int ppid;
  unsigned char action;
  unsigned char _pad[3];
  unsigned int score;
  unsigned long long timestamp;
  char filename[64];
};

// Rust SHM Header
struct message_header {
  unsigned int magic;
  unsigned short msg_type;
  unsigned short pad;
  unsigned int length;
};

#define SHM_PATH "/var/run/sentinel/truthsync_shm"
#define CONTROL_SIZE 64
#define MAGIC 0xDEADBEEF
#define MSG_PROCESS_TEXT 0x01

static int handle_event(void *ctx, void *data, size_t data_sz) {
  printf("DEBUG: Received event size %zu\n", data_sz);
  unsigned char *raw = data;
  for (int i = 0; i < 16 && i < data_sz; i++)
    printf("%02x ", raw[i]);
  printf("\n");

  struct threat_decision *e = data;

  // Write to SHM (File-linked)
  int fd = open(SHM_PATH, O_RDWR);
  if (fd < 0)
    return 0;

  void *ptr = mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
  if (ptr == MAP_FAILED) {
    close(fd);
    return 0;
  }

  struct message_header *hdr = (struct message_header *)(ptr + CONTROL_SIZE);
  hdr->magic = MAGIC;
  hdr->msg_type = MSG_PROCESS_TEXT;
  hdr->length = strlen(e->filename);

  char *payload = (char *)(ptr + CONTROL_SIZE + sizeof(struct message_header));
  strncpy(payload, e->filename, 64);

  munmap(ptr, 4096);
  close(fd);

  return 0;
}

// Mock validation for Semantic Shell
int validate_cmd(char *cmd) {
  // In a real scenario, this would check SHM or call an internal policy engine
  // For now, we simulate a check
  // If cmd contains "rm -rf /", block it.
  if (strstr(cmd, "rm -rf /") != NULL)
    return -1;
  return 0; // Approved
}

int main(int argc, char **argv) {
  // Check for semantic validation flag
  if (argc > 1 && strcmp(argv[1], "--semantic-validate") == 0) {
    if (argc < 3) {
      fprintf(stderr, "Usage: %s --semantic-validate <cmd>\n", argv[0]);
      return 1;
    }
    if (validate_cmd(argv[2]) == 0) {
      // Print nothing or simple success? Python script expects return code 0
      // and stdout Python script: "Sentinel APPROVED: {cmd}" logic is inside
      // python. Python script checks returncode == 0. If return code 0, python
      // prints "APPROVED".
      return 0;
    } else {
      fprintf(stderr, "Semantic Policy Violation\n");
      return 1;
    }
    return 0;
  }

  struct ring_buffer *rb = NULL;
  int map_fd;

  printf("🚀 Sentinel High-Performance Relay (C Version) Starting...\n");

  map_fd = bpf_obj_get("/sys/fs/bpf/decision_ringbuf");
  if (map_fd < 0) {
    perror("Failed to open pinned map");
    return 1;
  }

  rb = ring_buffer__new(map_fd, handle_event, NULL, NULL);
  if (!rb) {
    fprintf(stderr, "Failed to create ring buffer\n");
    return 1;
  }

  printf("✅ Relay ACTIVE. Monitoring events...\n");

  while (1) {
    ring_buffer__poll(rb, 100);
  }

  return 0;
}
