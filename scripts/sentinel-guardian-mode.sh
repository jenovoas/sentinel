#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

readonly BPF_DIR=/sys/fs/bpf/guardian_alpha
readonly LINK_PIN="$BPF_DIR/guardian_link"
readonly MAP_PIN="$BPF_DIR/whitelist_map"
readonly MODE_PIN="$BPF_DIR/guardian_mode_map"
readonly ROLLBACK_HELPER=/usr/local/libexec/sentinel-guardian-rollback
readonly ROLLBACK_TIMER=sentinel-guardian-auto-rollback.timer

if [[ $EUID -ne 0 ]]; then
    echo "run as root" >&2
    exit 1
fi
[[ -e $LINK_PIN && -e $MAP_PIN && -e $MODE_PIN ]] || {
    echo "Guardian is not attached with the current policy maps" >&2
    exit 1
}

declare -a key_bytes
build_key() {
    local path=$1 padding
    key_bytes=()
    read -r -a key_bytes <<< "$(printf '%s' "$path" | od -An -v -tx1 | tr '\n' ' ')"
    padding=$((256 - ${#key_bytes[@]}))
    (( padding > 0 )) || { echo "path does not fit BPF whitelist key: $path" >&2; return 1; }
    while (( padding > 0 )); do
        key_bytes+=(00)
        padding=$((padding - 1))
    done
    [[ ${#key_bytes[@]} -eq 256 ]] || { echo "invalid whitelist key size for $path" >&2; return 1; }
}

lookup_path() {
    local path=$1
    build_key "$path"
    bpftool map lookup pinned "$MAP_PIN" key hex "${key_bytes[@]}" >/dev/null
}

require_whitelisted_command() {
    local tool=$1 path
    path=$(command -v "$tool") || { echo "required recovery command is missing: $tool" >&2; return 1; }
    lookup_path "$path" || { echo "required command is not whitelisted: $path" >&2; return 1; }
}

case ${1:-} in
    enforce)
        delay=${2:-300}
        [[ $delay =~ ^[0-9]+$ ]] && (( delay >= 60 && delay <= 900 )) || {
            echo "rollback delay must be between 60 and 900 seconds" >&2
            exit 2
        }
        [[ -x $ROLLBACK_HELPER ]] || { echo "rollback helper is missing: $ROLLBACK_HELPER" >&2; exit 1; }
        for tool in bash sh sudo systemctl rm bpftool sshd; do
            require_whitelisted_command "$tool"
        done
        while IFS=: read -r _ _ _ _ _ _ login_shell; do
            [[ -x $login_shell ]] && lookup_path "$login_shell" || {
                [[ ! -x $login_shell ]] || { echo "login shell is not whitelisted: $login_shell" >&2; exit 1; }
            }
        done < /etc/passwd
        lookup_path "$ROLLBACK_HELPER" || { echo "rollback helper is not whitelisted: $ROLLBACK_HELPER" >&2; exit 1; }
        for tool in agetty login nginx docker containerd runc; do
            if path=$(command -v "$tool"); then
                lookup_path "$path" || { echo "critical command is not whitelisted: $path" >&2; exit 1; }
            fi
        done
        for path in /usr/lib/openssh/sshd-session /usr/lib/openssh/sshd-auth; do
            if [[ -x $path ]]; then
                lookup_path "$path" || { echo "SSH session executable is not whitelisted: $path" >&2; exit 1; }
            fi
        done
        systemd-run --quiet --unit=sentinel-guardian-auto-rollback \
            --on-active="${delay}s" "$ROLLBACK_HELPER"
        systemctl is-active --quiet "$ROLLBACK_TIMER" || {
            echo "automatic rollback timer did not become active; enforcement remains off" >&2
            exit 1
        }
        bpftool map update pinned "$MODE_PIN" key hex 00 00 00 00 value hex 01 00 00 00 any
        echo "Guardian enforcement enabled with ${delay}s automatic rollback."
        echo "Verify a new SSH session and the public frontend before running: $0 confirm"
        ;;
    audit)
        bpftool map update pinned "$MODE_PIN" key hex 00 00 00 00 value hex 00 00 00 00 any || {
            "$ROLLBACK_HELPER" --detach
            exit 1
        }
        systemctl stop "$ROLLBACK_TIMER" 2>/dev/null || true
        echo "Guardian is in audit-only mode."
        ;;
    confirm)
        bpftool map lookup pinned "$MODE_PIN" key hex 00 00 00 00 | grep -Eq 'value: 01 00 00 00' || {
            echo "Guardian is not enforcing; nothing to confirm" >&2
            exit 1
        }
        systemctl is-active --quiet "$ROLLBACK_TIMER" || {
            echo "automatic rollback timer is not active; refusing confirmation" >&2
            exit 1
        }
        systemctl stop "$ROLLBACK_TIMER"
        systemctl is-active --quiet "$ROLLBACK_TIMER" && {
            echo "could not cancel automatic rollback; enforcement remains guarded" >&2
            exit 1
        }
        echo "Automatic rollback cancelled; keep monitoring SSH and frontend health."
        ;;
    *)
        echo "usage: $0 {enforce [rollback-seconds]|audit|confirm}" >&2
        exit 2
        ;;
esac
