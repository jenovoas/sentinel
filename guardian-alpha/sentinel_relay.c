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

#define SHM_PATH "/tmp/truthsync_shm"
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

int main() {
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
