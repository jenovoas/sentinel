#!/usr/bin/env bash
set -euo pipefail

readonly BPF_DIR=/sys/fs/bpf/guardian_alpha
readonly LINK_PIN="$BPF_DIR/guardian_link"
readonly PROGRAM_PIN="$BPF_DIR/guardian_prog"
readonly WHITELIST_PIN="$BPF_DIR/whitelist_map"
readonly MODE_PIN="$BPF_DIR/guardian_mode_map"
readonly EVENTS_PIN="$BPF_DIR/events"
readonly RODATA_PIN="$BPF_DIR/guardian_rodata"

if [[ $EUID -ne 0 ]]; then
    echo "run as root" >&2
    exit 1
fi

detach=${1:-}
if [[ -e $MODE_PIN ]] && bpftool map update pinned "$MODE_PIN" \
    key hex 00 00 00 00 value hex 00 00 00 00 any; then
    echo "Guardian returned to audit-only mode."
else
    echo "Guardian mode map unavailable; detaching the pinned LSM link." >&2
    detach=--detach
fi

if [[ $detach == --detach ]]; then
    rm -f "$LINK_PIN"
    [[ ! -e $LINK_PIN ]] || { echo "failed to detach Guardian link" >&2; exit 1; }
    rm -f "$PROGRAM_PIN" "$WHITELIST_PIN" "$MODE_PIN" "$EVENTS_PIN" "$RODATA_PIN"
    echo "Guardian link detached."
elif [[ -n $detach ]]; then
    echo "usage: $0 [--detach]" >&2
    exit 2
fi
