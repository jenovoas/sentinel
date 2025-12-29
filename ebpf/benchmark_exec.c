#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <time.h>
#include <sys/types.h>

#define ITERATIONS 1000

// Function to get current time in nanoseconds
long long current_time_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

int main() {
    printf("Guardian-Alpha LSM - C Native Benchmark\n");
    printf("Iterations: %d\n", ITERATIONS);
    printf("Target: /bin/true\n\n");

    long long start = current_time_ns();

    for (int i = 0; i < ITERATIONS; i++) {
        pid_t pid = fork();
        if (pid == 0) {
            // Child process
            char *args[] = {"/bin/true", NULL};
            execve("/bin/true", args, NULL);
            // If execve fails
            perror("execve");
            exit(1);
        } else if (pid > 0) {
            // Parent process
            int status;
            waitpid(pid, &status, 0);
        } else {
            perror("fork");
            exit(1);
        }
    }

    long long end = current_time_ns();
    long long total_ns = end - start;
    double avg_ns = (double)total_ns / ITERATIONS;
    double avg_us = avg_ns / 1000.0;
    double avg_ms = avg_us / 1000.0;

    printf("Total time: %.2f ms\n", (double)total_ns / 1000000.0);
    printf("Average per execution: %.2f us (%.2f ms)\n", avg_us, avg_ms);

    // Analysis
    // Typical linux fork+exec is ~200-500us on modern hardware
    // If we are under 1000us (1ms), we are golden.
    
    printf("\nAnalysis:\n");
    if (avg_us < 1000.0) {
        printf("✅ PASSED: Total Latency < 1ms\n");
    } else {
        printf("⚠️  WARNING: Total Latency > 1ms\n");
    }

    return 0;
}
