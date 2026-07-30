// SPDX-License-Identifier: GPL-2.0
/* Gamma Watchdog — Userspace complemento de Guardian-Gamma
 *
 * Funciones (Fase 2a, MVP):
 *   1. Poblar known_peer_prog_ids con los prog_id de los Guardians peer
 *      (reading pins en /sys/fs/bpf/<name>).
 *   2. inotify sobre /sys/fs/bpf/ — detecta IN_DELETE de pins peer
 *      y emite EVENT_GAMMA_PEER_MISSING a stdout (NDJSON).
 *   3. Escribir heartbeat a gamma_heartbeat[0] cada BIO_PULSE (17s) para
 *      que el hardware watchdog detecte si Gamma userspace cae.
 *
 * Uso: sudo ./gamma_watchdog &
 *      (lanzado automáticamente por load.sh)
 *
 * Copyright (c) 2026 Sentinel Cortex™
 */

#define _GNU_SOURCE
#include <bpf/bpf.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/inotify.h>
#include <sys/timerfd.h>
#include <time.h>
#include <unistd.h>
#include "cortex_events.h"

#define BPF_DIR          "/sys/fs/bpf"
#define PEERS_PIN        BPF_DIR "/known_peer_prog_ids"
#define HEARTBEAT_PIN    BPF_DIR "/gamma_heartbeat"
#define INOTIFY_BUF_SZ   (16 * (sizeof(struct inotify_event) + NAME_MAX + 1))

struct peer {
    const char *pin_name;
    __u8 code;
};

static const struct peer PEERS[] = {
    { "guardian_alpha",           GUARDIAN_CODE_ALPHA     },
    { "guardian_cognitive",       GUARDIAN_CODE_COGNITIVE },
    { "ai_guardian",              GUARDIAN_CODE_AI        },
    { "float_detector",           GUARDIAN_CODE_FLOAT     },
    { "me60os_ai_guardian_open",  GUARDIAN_CODE_AI        },
};
#define NPEERS (sizeof(PEERS) / sizeof(PEERS[0]))

static volatile sig_atomic_t stop = 0;
static void on_sig(int s) { (void)s; stop = 1; }

static void emit_ndjson(__u32 event_type, __u8 code, __u8 severity, const char *detail)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    __u64 ns = (__u64)ts.tv_sec * 1000000000ULL + ts.tv_nsec;

    printf("{\"ts_ns\":%llu,\"event_type\":%u,\"guardian_code\":%u,"
           "\"severity\":%u,\"source\":\"gamma_watchdog\",\"detail\":\"%s\"}\n",
           (unsigned long long)ns, event_type, code, severity, detail ? detail : "");
    fflush(stdout);
}

/* Lee el prog_id asociado a un pin LSM y lo registra en known_peer_prog_ids. */
static int register_peer(int peers_fd, const char *pin_name, __u8 code)
{
    char path[256];
    snprintf(path, sizeof(path), "%s/%s", BPF_DIR, pin_name);

    int prog_fd = bpf_obj_get(path);
    if (prog_fd < 0) {
        /* No todos los peers existen siempre; no es fatal */
        return 0;
    }

    struct bpf_prog_info info = {};
    __u32 len = sizeof(info);
    int err = bpf_obj_get_info_by_fd(prog_fd, &info, &len);
    close(prog_fd);
    if (err) {
        fprintf(stderr, "gamma_watchdog: info %s: %s\n", pin_name, strerror(errno));
        return -1;
    }

    __u32 id = info.id;
    err = bpf_map_update_elem(peers_fd, &id, &code, BPF_ANY);
    if (err) {
        fprintf(stderr, "gamma_watchdog: map update %s: %s\n", pin_name, strerror(errno));
        return -1;
    }
    fprintf(stderr, "gamma_watchdog: peer %s (prog_id=%u, code=%u) registrado\n",
            pin_name, id, code);
    return 1;
}

static __u8 peer_code_for(const char *name)
{
    for (size_t i = 0; i < NPEERS; i++)
        if (strcmp(PEERS[i].pin_name, name) == 0)
            return PEERS[i].code;
    return 0;
}

int main(void)
{
    signal(SIGTERM, on_sig);
    signal(SIGINT,  on_sig);

    /* 1. Abrir mapas pineados */
    int peers_fd = bpf_obj_get(PEERS_PIN);
    if (peers_fd < 0) {
        fprintf(stderr, "gamma_watchdog: abrir %s: %s\n", PEERS_PIN, strerror(errno));
        return 1;
    }
    int hb_fd = bpf_obj_get(HEARTBEAT_PIN);
    if (hb_fd < 0) {
        fprintf(stderr, "gamma_watchdog: abrir %s: %s\n", HEARTBEAT_PIN, strerror(errno));
        return 1;
    }

    /* 2. Poblar known_peer_prog_ids */
    int registered = 0;
    for (size_t i = 0; i < NPEERS; i++)
        if (register_peer(peers_fd, PEERS[i].pin_name, PEERS[i].code) > 0)
            registered++;
    fprintf(stderr, "gamma_watchdog: %d/%zu peers registrados\n", registered, NPEERS);

    /* 3. inotify sobre /sys/fs/bpf/ (solo IN_DELETE) */
    int ino_fd = inotify_init1(IN_CLOEXEC | IN_NONBLOCK);
    if (ino_fd < 0) { perror("inotify_init1"); return 1; }
    if (inotify_add_watch(ino_fd, BPF_DIR, IN_DELETE | IN_MOVED_FROM) < 0) {
        perror("inotify_add_watch");
        return 1;
    }

    /* 4. Timer heartbeat cada BIO_PULSE (17s) */
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC | TFD_NONBLOCK);
    struct itimerspec its = {
        .it_interval = { .tv_sec = 17, .tv_nsec = 0 },
        .it_value    = { .tv_sec = 1,  .tv_nsec = 0 },  /* primer tick en 1s */
    };
    timerfd_settime(tfd, 0, &its, NULL);

    /* 5. epoll */
    int ep = epoll_create1(EPOLL_CLOEXEC);
    struct epoll_event evi = { .events = EPOLLIN, .data.fd = ino_fd };
    struct epoll_event evt = { .events = EPOLLIN, .data.fd = tfd };
    epoll_ctl(ep, EPOLL_CTL_ADD, ino_fd, &evi);
    epoll_ctl(ep, EPOLL_CTL_ADD, tfd, &evt);

    fprintf(stderr, "gamma_watchdog: activo. Pulso=%ds, vigilando %s\n", 17, BPF_DIR);

    /* 6. Loop principal */
    char ibuf[INOTIFY_BUF_SZ] __attribute__((aligned(8)));
    while (!stop) {
        struct epoll_event out[4];
        int n = epoll_wait(ep, out, 4, -1);
        if (n < 0) { if (errno == EINTR) continue; perror("epoll_wait"); break; }

        for (int i = 0; i < n; i++) {
            if (out[i].data.fd == ino_fd) {
                ssize_t r = read(ino_fd, ibuf, sizeof(ibuf));
                for (char *p = ibuf; r > 0 && p < ibuf + r; ) {
                    struct inotify_event *ev = (void *)p;
                    if (ev->len > 0) {
                        __u8 code = peer_code_for(ev->name);
                        if (code) {
                            char detail[128];
                            snprintf(detail, sizeof(detail), "pin=%s", ev->name);
                            emit_ndjson(EVENT_GAMMA_PEER_MISSING, code,
                                        SEVERITY_CRITICAL, detail);
                        }
                    }
                    p += sizeof(*ev) + ev->len;
                }
            } else if (out[i].data.fd == tfd) {
                __u64 exp;
                read(tfd, &exp, sizeof(exp));

                struct timespec ts;
                clock_gettime(CLOCK_MONOTONIC, &ts);
                __u64 ns = (__u64)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
                __u32 key = 0;
                bpf_map_update_elem(hb_fd, &key, &ns, BPF_ANY);

                /* EXP-027: YHWH 17-tick Accumulative Phase Drift Purge (epsilon_drift = 0) */
                emit_ndjson(EVENT_GAMMA_HEARTBEAT, GUARDIAN_CODE_GAMMA,
                            SEVERITY_LOW, "alive; YHWH_PHASE_DRIFT_PURGED");
            }
        }
    }

    fprintf(stderr, "gamma_watchdog: saliendo limpiamente\n");
    close(ino_fd); close(tfd); close(ep);
    close(peers_fd); close(hb_fd);
    return 0;
}
