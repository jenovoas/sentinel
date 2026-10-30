#!/usr/bin/env bash
set -euo pipefail

readonly REPO_DIR=$(git -C "$(dirname -- "${BASH_SOURCE[0]}")/.." rev-parse --show-toplevel)
readonly OUTPUT=${1:-/tmp/sentinel-security-gateway.tar.gz}
readonly STAGE=$(mktemp -d "${TMPDIR:-/tmp}/sentinel-security-gateway.XXXXXX")
trap 'rm -rf -- "$STAGE"' EXIT

cargo build --locked --release \
    --manifest-path "$REPO_DIR/sentinel-cortex/Cargo.toml" \
    --bin sentinel-security-gateway

install -m 0755 "$REPO_DIR/target/release/sentinel-security-gateway" "$STAGE/sentinel-security-gateway"
install -m 0644 "$REPO_DIR/systemd/sentinel-security-gateway.service" "$STAGE/sentinel-security-gateway.service"
mkdir -p "$(dirname -- "$OUTPUT")"
tar -C "$STAGE" -czf "$OUTPUT" .
sha256sum "$OUTPUT"
