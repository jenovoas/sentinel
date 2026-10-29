#!/usr/bin/env bash
set -euo pipefail

readonly BUNDLE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
readonly BPF_DIR=/sys/fs/bpf/guardian_alpha
readonly LINK_PIN="$BPF_DIR/guardian_link"
readonly MODE_PIN="$BPF_DIR/guardian_mode_map"
readonly EBPF_DEST=/usr/local/lib/sentinel/ebpf
readonly LIBEXEC_DEST=/usr/local/libexec
readonly UNIT_DEST=/etc/systemd/system/sentinel-ebpf.service

if [[ $EUID -ne 0 ]]; then
    echo "run as root" >&2
    exit 1
fi
[[ -d /run/systemd/system ]] || { echo "systemd is not running" >&2; exit 1; }

for file in \
    guardian_cognitive.o attacher bootstrap-sentinel-ebpf.sh \
    sentinel-guardian-mode.sh sentinel-guardian-rollback.sh sentinel-ebpf.service bundle-arch; do
    [[ -f $BUNDLE_DIR/$file ]] || { echo "incomplete Sentinel eBPF bundle: $file is missing" >&2; exit 1; }
done
[[ -x $BUNDLE_DIR/attacher ]] || { echo "bundle attacher is not executable" >&2; exit 1; }
[[ $(<"$BUNDLE_DIR/bundle-arch") == "$(uname -m)" ]] || {
    echo "bundle architecture does not match this host" >&2
    exit 1
}

# Never replace files beneath a legacy fail-closed link that cannot be switched
# to audit mode. The caller must recover it out of band first.
if [[ -e $LINK_PIN ]]; then
    [[ -e $MODE_PIN ]] || { echo "legacy Guardian link has no mode map; refusing installation" >&2; exit 1; }
    bpftool map update pinned "$MODE_PIN" key hex 00 00 00 00 value hex 00 00 00 00 any || {
        echo "could not put the attached Guardian into audit mode; refusing installation" >&2
        exit 1
    }
fi

install -d -m 0755 "$EBPF_DEST" "$LIBEXEC_DEST"
install -m 0644 "$BUNDLE_DIR/guardian_cognitive.o" "$EBPF_DEST/guardian_cognitive.o"
install -m 0755 "$BUNDLE_DIR/attacher" "$EBPF_DEST/attacher"
install -m 0755 "$BUNDLE_DIR/bootstrap-sentinel-ebpf.sh" "$LIBEXEC_DEST/sentinel-ebpf-bootstrap"
install -m 0755 "$BUNDLE_DIR/sentinel-guardian-mode.sh" "$LIBEXEC_DEST/sentinel-guardian-mode"
install -m 0755 "$BUNDLE_DIR/sentinel-guardian-rollback.sh" "$LIBEXEC_DEST/sentinel-guardian-rollback"
install -m 0644 "$BUNDLE_DIR/sentinel-ebpf.service" "$UNIT_DEST"
systemctl daemon-reload

echo "Sentinel eBPF files installed in audit-by-default mode."
echo "The service was not unmasked, enabled, or started. Review recovery access, then start it explicitly."
