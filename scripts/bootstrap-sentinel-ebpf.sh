#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

readonly BPF_DIR=/sys/fs/bpf/guardian_alpha
readonly PROGRAM_PIN="$BPF_DIR/guardian_prog"
readonly LINK_PIN="$BPF_DIR/guardian_link"
readonly MAP_PIN="$BPF_DIR/whitelist_map"
readonly MODE_PIN="$BPF_DIR/guardian_mode_map"
readonly SCRIPT_DIR=/usr/local/lib/sentinel/ebpf
readonly OBJECT="$SCRIPT_DIR/guardian_cognitive.o"
readonly ATTACHER="$SCRIPT_DIR/attacher"
readonly BATCH_FILE="/run/sentinel-ebpf-allowlist.${BASHPID}.batch"
readonly PATH_FILE="/run/sentinel-ebpf-allowlist.${BASHPID}.paths"

if [[ $EUID -ne 0 ]]; then
    echo "run as root" >&2
    exit 1
fi
command -v bpftool >/dev/null || { echo "bpftool is not installed" >&2; exit 1; }
[[ -r $OBJECT ]] || { echo "missing eBPF object: $OBJECT" >&2; exit 1; }
[[ -x $ATTACHER ]] || { echo "missing executable attacher: $ATTACHER" >&2; exit 1; }
[[ -e /sys/kernel/btf/vmlinux ]] || { echo "kernel BTF is unavailable" >&2; exit 1; }
grep -qw bpf /sys/kernel/security/lsm || { echo "BPF LSM is not enabled" >&2; exit 1; }

mkdir -p /sys/fs/bpf
if ! grep -Eq '^[^ ]+ /sys/fs/bpf bpf ' /proc/mounts; then
    mount -t bpf bpf /sys/fs/bpf
fi
mkdir -p "$BPF_DIR"

# Switch a compatible live program to audit before changing its allowlist.
# Refuse an in-place upgrade of a legacy program without the mode map.
if [[ -e $LINK_PIN ]]; then
    [[ -e $MODE_PIN ]] || { echo "attached Guardian has no safe mode map; refusing in-place upgrade" >&2; exit 1; }
    bpftool map update pinned "$MODE_PIN" key hex 00 00 00 00 value hex 00 00 00 00 any
fi

if [[ ! -e $PROGRAM_PIN ]]; then
    bpftool prog load "$OBJECT" "$PROGRAM_PIN" type lsm pinmaps "$BPF_DIR"
fi
[[ -e $MAP_PIN ]] || { echo "whitelist map was not pinned" >&2; exit 1; }
[[ -e $MODE_PIN ]] || { echo "Guardian mode map was not pinned" >&2; exit 1; }

# Array maps start at zero. Explicitly retain audit-only mode during bootstrap.
bpftool map update pinned "$MODE_PIN" key hex 00 00 00 00 value hex 00 00 00 00 any
: > "$BATCH_FILE"
: > "$PATH_FILE"
trap 'rm -f "$BATCH_FILE" "$PATH_FILE"' EXIT

add_host_inventory() {
    local root=$1
    [[ -d $root ]] || return 0
    find -H "$root" \( -type f -o -type l \) -perm /111 -print0 >> "$PATH_FILE"
}

for root in \
    /bin /sbin /usr/bin /usr/sbin \
    /usr/lib/openssh /usr/lib/systemd /usr/libexec \
    /usr/lib/docker /usr/lib/containerd \
    /usr/local/bin /usr/local/sbin /usr/local/libexec \
    /home/jnovoas/.local/bin /home/jnovoas/.cargo/bin; do
    add_host_inventory "$root"
done

# Container execution sees paths inside the container root, not the host's
# /var/lib/docker/.../merged prefix. Add those logical paths to the map.
if command -v docker >/dev/null 2>&1; then
    DOCKER_ROOT=$(docker info --format '{{.DockerRootDir}}') || {
        echo "Docker is installed but its executable inventory is unavailable" >&2
        exit 1
    }
    if [[ -d $DOCKER_ROOT/overlay2 ]]; then
        while IFS= read -r -d '' container_root; do
            while IFS= read -r -d '' candidate; do
                relative_path=/${candidate#"$container_root"/}
                printf '%s\0' "$relative_path" >> "$PATH_FILE"
            done < <(find -H "$container_root" \( -type f -o -type l \) -perm /111 -print0)
        done < <(find "$DOCKER_ROOT/overlay2" -mindepth 2 -maxdepth 2 -type d -name merged -print0)
    fi
fi

# Include the exact executable paths of already-running processes, including
# services installed outside standard package directories.
for proc_exe in /proc/[0-9]*/exe; do
    [[ -L $proc_exe ]] || continue
    process_path=$(readlink "$proc_exe" 2>/dev/null || true)
    [[ $process_path == /* && -x $process_path ]] || continue
    printf '%s\0' "$process_path" >> "$PATH_FILE"
done

# Preserve every configured login shell, not only the installer's shell.
while IFS=: read -r _ _ _ _ _ _ login_shell; do
    [[ -x $login_shell ]] && printf '%s\0' "$login_shell" >> "$PATH_FILE"
done < /etc/passwd

sort -z -u -o "$PATH_FILE" "$PATH_FILE"

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

batch_updates=0
while IFS= read -r -d '' path; do
    [[ -x $path ]] || continue
    build_key "$path"
    printf 'map update pinned %s key hex' "$MAP_PIN" >> "$BATCH_FILE"
    printf ' %s' "${key_bytes[@]}" >> "$BATCH_FILE"
    printf ' value hex 01 any\n' >> "$BATCH_FILE"
    ((batch_updates += 1))
done < "$PATH_FILE"

(( batch_updates > 0 )) || { echo "refusing to attach with an empty executable inventory" >&2; exit 1; }
bpftool batch file "$BATCH_FILE"
map_entries=$(bpftool -j map dump pinned "$MAP_PIN" | python3 -c 'import json, sys; print(len(json.load(sys.stdin)))')
[[ $map_entries =~ ^[0-9]+$ ]] && (( map_entries >= batch_updates )) || {
    echo "whitelist map verification failed: expected at least $batch_updates entries, found $map_entries" >&2
    exit 1
}

lookup_path() {
    local path=$1
    build_key "$path"
    bpftool map lookup pinned "$MAP_PIN" key hex "${key_bytes[@]}" >/dev/null
}

# These commands form the minimum remote recovery and administration path.
for tool in bash sh sudo systemctl rm bpftool sshd; do
    tool_path=$(command -v "$tool") || { echo "required recovery command is missing: $tool" >&2; exit 1; }
    lookup_path "$tool_path" || { echo "required command is not whitelisted: $tool_path" >&2; exit 1; }
done

while IFS=: read -r _ _ _ _ _ _ login_shell; do
    if [[ -x $login_shell ]]; then
        lookup_path "$login_shell" || { echo "login shell is not whitelisted: $login_shell" >&2; exit 1; }
    fi
done < /etc/passwd
for tool in agetty login; do
    if tool_path=$(command -v "$tool"); then
        lookup_path "$tool_path" || { echo "console login command is not whitelisted: $tool_path" >&2; exit 1; }
    fi
done

# Include web and container control paths when those services are installed.
for tool in nginx docker containerd runc; do
    if tool_path=$(command -v "$tool"); then
        lookup_path "$tool_path" || { echo "service management command is not whitelisted: $tool_path" >&2; exit 1; }
    fi
done

# Attachment happens only after population and exact critical-key checks pass.
if [[ -e $LINK_PIN ]]; then
    bpftool prog show pinned "$PROGRAM_PIN"
    exit 0
fi

"$ATTACHER" "$PROGRAM_PIN" "$LINK_PIN"
bpftool prog show pinned "$PROGRAM_PIN"
[[ -e $LINK_PIN ]] || { echo "LSM link pin was not created" >&2; exit 1; }
echo "Guardian attached in audit-only mode; enforcement is disabled."
