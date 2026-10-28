#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

readonly BPF_DIR=/sys/fs/bpf/guardian_alpha
readonly PROGRAM_PIN="$BPF_DIR/guardian_prog"
readonly LINK_PIN="$BPF_DIR/guardian_link"
readonly MAP_PIN="$BPF_DIR/whitelist_map"
readonly SCRIPT_DIR=/usr/local/lib/sentinel/ebpf
readonly OBJECT="$SCRIPT_DIR/guardian_cognitive.o"
readonly ATTACHER="$SCRIPT_DIR/attacher"
readonly BATCH_FILE="/run/sentinel-ebpf-allowlist.${BASHPID}.batch"

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

if [[ ! -e $PROGRAM_PIN ]]; then
    bpftool prog load "$OBJECT" "$PROGRAM_PIN" type lsm pinmaps "$BPF_DIR"
fi
[[ -e $MAP_PIN ]] || { echo "whitelist map was not pinned" >&2; exit 1; }
: > "$BATCH_FILE"
trap 'rm -f "$BATCH_FILE"' EXIT

whitelist_path() {
    local path=$1 padding byte i
    local -a key_bytes
    [[ -x $path ]] || return 0
    padding=$((256 - ${#path}))
    (( padding >= 0 )) || { echo "whitelist path exceeds map key size: $path" >&2; return 1; }
    key_bytes=()
    for ((i = 0; i < ${#path}; i++)); do
        printf -v byte '%02x' "'${path:i:1}"
        key_bytes+=("$byte")
    done
    for ((i = 0; i < padding; i++)); do key_bytes+=(00); done
    [[ ${#key_bytes[@]} -eq 256 ]] || { echo "invalid whitelist key size for $path" >&2; return 1; }
    printf 'map update pinned %s key hex' "$MAP_PIN" >> "$BATCH_FILE"
    printf ' %s' "${key_bytes[@]}" >> "$BATCH_FILE"
    printf ' value hex 01 any\n' >> "$BATCH_FILE"
}

# Minimal operational allowlist is populated before attaching the fail-closed LSM.
for path in \
    /bin/bash /usr/bin/bash /bin/sh /usr/bin/sh /usr/bin/dash \
    /bin/zsh /usr/bin/zsh /bin/fish /usr/bin/fish \
    /usr/bin/sudo /usr/bin/systemctl /usr/sbin/sshd \
    /usr/sbin/unix_chkpwd /usr/lib/openssh/sshd-session \
    /usr/lib/openssh/sshd-auth /usr/lib/openssh/sftp-server \
    /usr/bin/ssh /usr/bin/scp /usr/bin/curl /usr/bin/wget \
    /usr/bin/cp /usr/bin/mv /usr/bin/rm /usr/bin/mkdir /usr/bin/install /usr/bin/chmod /usr/bin/chown \
    /usr/bin/ls /usr/bin/cat /usr/bin/grep /usr/bin/sed /usr/bin/awk /usr/bin/head /usr/bin/tail \
    /usr/bin/env /usr/bin/od /usr/bin/readlink /usr/bin/sha256sum /usr/bin/echo /bin/echo \
    /usr/bin/true /bin/true /usr/bin/id /usr/bin/whoami \
    /usr/bin/apt /usr/bin/apt-get /usr/bin/dpkg /usr/bin/dpkg-query \
    /usr/sbin/bpftool /usr/bin/bpftool /usr/local/bin/sentinel-cortex \
    /usr/local/libexec/sentinel-ebpf-bootstrap \
    /home/jnovoas/.local/bin/sentinel-cortex /home/jnovoas/.local/bin/mycnetd \
    /usr/local/sbin/mycnet-batmesh \
    /usr/bin/firewall-cmd /usr/sbin/firewalld /usr/bin/firewalld \
    /usr/bin/redis-server /usr/sbin/redis-server /usr/sbin/watchdog /usr/bin/watchdog \
    /usr/sbin/ss /usr/sbin/ip /usr/bin/ip \
    /usr/sbin/batctl /usr/bin/batctl /usr/sbin/modprobe /usr/bin/modprobe \
    /usr/bin/bridge /usr/sbin/bridge /usr/bin/wg /usr/bin/journalctl \
    /usr/bin/mountpoint /bin/mountpoint /usr/bin/mount /bin/mount \
    /usr/bin/timeout /usr/bin/sleep /usr/bin/find /bin/find; do
    whitelist_path "$path"
done

# This LSM is fail-closed for every execve, not just Sentinel agents. Seed the
# map with the executable inventory of the fresh host before attaching it, so
# baseline tools and installed services remain runnable. Include symlink names
# as well as regular files because bprm->filename can retain the invoked path.
for root in /bin /sbin /usr/bin /usr/sbin /lib /usr/lib /usr/local /home/jnovoas/.local/bin /home/jnovoas/.cargo/bin; do
    [[ -d $root ]] || continue
    while IFS= read -r -d '' candidate; do
        whitelist_path "$candidate"
    done < <(find -H "$root" \( -type f -o -type l \) -perm /111 -print0 2>/dev/null)
done

# Keep each configured login shell executable available after the LSM attaches.
while IFS=: read -r account _ _ _ _ _ login_shell; do
    if [[ $account == jnovoas || $account == root ]]; then
        whitelist_path "$login_shell"
    fi
done < /etc/passwd

# Submit the inventory in one bpftool process. A process per binary made fresh
# hosts exceed systemd's bootstrap timeout before the LSM could attach.
bpftool batch file "$BATCH_FILE"

# Never detach or delete an existing BPF program from a running host.
if [[ -e $LINK_PIN ]]; then
    bpftool prog show pinned "$PROGRAM_PIN"
    exit 0
fi

"$ATTACHER" "$PROGRAM_PIN" "$LINK_PIN"
bpftool prog show pinned "$PROGRAM_PIN"
[[ -e $LINK_PIN ]] || { echo "LSM link pin was not created" >&2; exit 1; }
