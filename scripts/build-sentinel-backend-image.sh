#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: %s <image-tag>\n' "$0" >&2
  exit 2
fi

root=$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)

docker run --rm \
  -v "$root:/src" \
  -w /src \
  rust:bookworm \
  bash -c 'apt-get update -qq && apt-get install -y -qq --no-install-recommends python3.11 python3.11-dev build-essential clang libbpf-dev libelf-dev libzstd-dev zlib1g-dev libssl-dev pkg-config >/dev/null && PYO3_PYTHON=/usr/bin/python3.11 cargo build --locked --release --package me60os --features extension-module --lib && install -m 0644 target/release/libme60os_core.so backend/me60os_core.so'

docker build --tag "$1" -f "$root/backend/Dockerfile" "$root"
