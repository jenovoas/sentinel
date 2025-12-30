#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

// Sentinel Threat Simulator - C Edition (Static & Minimal)
// Designed to run inside the Sentinel Initrd environment

int main(int argc, char *argv[]) {
  printf("[SIMULATOR] Starting malicious process PID: %d\n", getpid());

  // 1. Create an RWX anonymous mapping
  size_t size = 4096;
  void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE | PROT_EXEC,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

  if (ptr == MAP_FAILED) {
    perror("[SIMULATOR] mmap failed");
    return 1;
  }

  // 2. Inject patterns (AIOpsDoom + NOP sled + shellcode hint)
  // The Hunter uses Aho-Corasick to match these.
  unsigned char payload[] = {0x90, 0x90, 0x90, 0x90, // NOP sled
                             '/',  'b',  'i',  'n',  '/', 's', 'h', 0,   'A',
                             'I',  'O',  'p',  's',  'D', 'o', 'o', 'm', ' ',
                             'I',  'n',  'j',  'e',  'c', 't', 'i', 'o', 'n'};

  memcpy(ptr, payload, sizeof(payload));
  printf("[SIMULATOR] Payload injected into RWX memory at %p\n", ptr);
  printf("[SIMULATOR] Waiting for The Hunter (PID 1) to find us...\n");

  // 3. Busy loop or sleep to stay alive for the scanner
  while (1) {
    sleep(1);
    printf("[SIMULATOR] Heartbeat... (Still alive)\n");
  }

  return 0;
}
