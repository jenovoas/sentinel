FROM rust:1.75 as builder

WORKDIR /app
COPY . .

# Build release binary
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install CA certificates for HTTPS
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy binary from builder
COPY --from=builder /app/target/release/neural-guard /usr/local/bin/neural-guard

# Run as non-root user
RUN useradd -m -u 1000 neural-guard
USER neural-guard

CMD ["neural-guard"]
