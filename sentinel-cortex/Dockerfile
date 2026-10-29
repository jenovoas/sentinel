# Runtime stage matches Fenix's Debian 13 glibc baseline.
FROM docker.io/library/debian:trixie-slim

# Install CA certificates for HTTPS and system deps
RUN apt-get update && apt-get install -y ca-certificates curl libssl3t64 libelf1 zlib1g libzstd1 && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled binary from context
COPY sentinel-cortex.bin /usr/local/bin/sentinel-cortex
RUN chmod +x /usr/local/bin/sentinel-cortex

# Run as non-root user
RUN useradd -m -u 1000 sentinel
USER sentinel

CMD ["sentinel-cortex"]
