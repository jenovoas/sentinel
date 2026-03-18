# Runtime stage - usar imagen slim sin apt-get issues en Rocky Linux
FROM docker.io/library/debian:bookworm-slim

# Install CA certificates for HTTPS
RUN apt-get update && apt-get install -y ca-certificates libssl3 && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled binary from host target/release
COPY target/release/sentinel-cortex /usr/local/bin/sentinel-cortex

# Run as non-root user
RUN useradd -m -u 1000 sentinel
USER sentinel

CMD ["sentinel-cortex"]
