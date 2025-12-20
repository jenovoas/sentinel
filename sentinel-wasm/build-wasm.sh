#!/bin/bash

# Simple WASM build script (without wasm-pack)
# Builds Rust to WASM manually

echo "🦀 Building Sentinel WASM Module..."

cd "$(dirname "$0")"

# Build for wasm32 target
echo "📦 Compiling to wasm32-unknown-unknown..."
cargo build --target wasm32-unknown-unknown --release

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📊 WASM file location:"
    ls -lh target/wasm32-unknown-unknown/release/*.wasm
    echo ""
    echo "📝 To use in Next.js, you'll need wasm-bindgen-cli:"
    echo "   cargo install wasm-bindgen-cli"
    echo "   wasm-bindgen target/wasm32-unknown-unknown/release/sentinel_wasm.wasm --out-dir pkg --target bundler"
else
    echo "❌ Build failed"
    exit 1
fi
