#!/usr/bin/env bash
set -euo pipefail

readonly REPO_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
readonly IMAGE=${1:-sentinel-cortex:latest}
readonly STAGE=$(mktemp -d "${TMPDIR:-/tmp}/sentinel-cortex-image.XXXXXX")
trap 'rm -rf -- "$STAGE"' EXIT

case $(uname -m) in
    x86_64|aarch64) ;;
    *) echo "unsupported Cortex build architecture: $(uname -m)" >&2; exit 1 ;;
esac

command -v cargo >/dev/null || { echo "cargo is required to build Cortex" >&2; exit 1; }
command -v docker >/dev/null || { echo "docker is required to package Cortex" >&2; exit 1; }

cargo build --locked --release --manifest-path "$REPO_DIR/Cargo.toml" \
    --package sentinel-cortex --bin sentinel-cortex
install -m 0755 "$REPO_DIR/target/release/sentinel-cortex" "$STAGE/sentinel-cortex.bin"
install -m 0644 "$REPO_DIR/sentinel-cortex/Dockerfile" "$STAGE/Dockerfile"

docker build --pull --tag "$IMAGE" "$STAGE"
echo "Built $IMAGE from the current source tree."
