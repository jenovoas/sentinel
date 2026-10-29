#!/usr/bin/env bash
set -euo pipefail

readonly REPO_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
readonly OUTPUT=${1:-/tmp/sentinel-ebpf-bundle.tar.gz}
readonly STAGE=$(mktemp -d "${TMPDIR:-/tmp}/sentinel-ebpf-bundle.XXXXXX")
trap 'rm -rf -- "$STAGE"' EXIT

case $(uname -m) in
    x86_64|aarch64) ;;
    *) echo "unsupported bundle architecture: $(uname -m)" >&2; exit 1 ;;
esac

make -C "$REPO_DIR/ebpf" \
    OBJECT="$STAGE/guardian_cognitive.o" \
    CLANG="${CLANG:-clang}" \
    LLVM_STRIP="${LLVM_STRIP:-llvm-strip}"
"${CLANG:-clang}" -g -O2 -Wall -I/usr/include \
    -o "$STAGE/attacher" "$REPO_DIR/ebpf/attacher.c" -lbpf

install -m 0755 "$REPO_DIR/scripts/bootstrap-sentinel-ebpf.sh" "$STAGE/bootstrap-sentinel-ebpf.sh"
install -m 0755 "$REPO_DIR/scripts/sentinel-guardian-mode.sh" "$STAGE/sentinel-guardian-mode.sh"
install -m 0755 "$REPO_DIR/scripts/sentinel-guardian-rollback.sh" "$STAGE/sentinel-guardian-rollback.sh"
install -m 0644 "$REPO_DIR/systemd/sentinel-ebpf.service" "$STAGE/sentinel-ebpf.service"
install -m 0644 /dev/null "$STAGE/bundle-arch"
printf '%s\n' "$(uname -m)" > "$STAGE/bundle-arch"
install -m 0755 "$REPO_DIR/scripts/install-sentinel-ebpf.sh" "$STAGE/install-sentinel-ebpf.sh"

mkdir -p "$(dirname -- "$OUTPUT")"
tar -C "$STAGE" -czf "$OUTPUT" .
sha256sum "$OUTPUT"
