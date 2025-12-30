# Dockerfile for TruthSync Production (Optimized Rust Edge)
FROM rust:1.75-bookworm as builder

WORKDIR /app
COPY . .

# Build release binary
RUN cargo build --release --manifest-path truthsync-poc/Cargo.toml

# Minimal runtime image
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies (OpenSSL might be needed by some crates)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the binary from the builder stage
COPY --from=builder /app/truthsync-poc/target/release/truthsync_core /usr/local/bin/truthsync-edge

# Expose the Axum server port
EXPOSE 8001

# Run the server
CMD ["truthsync-edge"]
