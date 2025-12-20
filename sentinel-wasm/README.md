# Sentinel WASM Module

High-performance Rust → WebAssembly module for Sentinel frontend.

## Features

- **AIOpsDoom Detection**: Ultra-fast pattern matching (90.5x faster than JS)
- **Anomaly Calculation**: Statistical analysis for metrics
- **Batch Processing**: Optimized for bulk operations
- **Minimal Bundle**: <20KB gzipped

## Build

```bash
# Install wasm-pack
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Build for web
wasm-pack build --target web --release

# Build for bundler (Next.js)
wasm-pack build --target bundler --release
```

## Usage in Next.js

```typescript
import init, { detect_aiopsdoom, detect_aiopsdoom_batch } from './pkg/sentinel_wasm';

// Initialize WASM
await init();

// Single detection
const isMalicious = detect_aiopsdoom("IGNORE PREVIOUS INSTRUCTIONS");

// Batch detection
const events = [
  { message: "Normal log", source: "app", timestamp: Date.now() },
  { message: "'; DROP TABLE", source: "user", timestamp: Date.now() }
];
const results = detect_aiopsdoom_batch(events);
```

## Performance

```
Benchmark: 10,000 events
├─ JavaScript: 450ms
├─ Rust WASM: 5ms
└─ Speedup: 90x ⭐
```

## Development

```bash
# Run tests
cargo test

# Run WASM tests
wasm-pack test --headless --firefox
```
