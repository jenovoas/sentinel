# Dockerfile for TruthSync Production
# Using Debian stable minimal as per Sentinel architecture
FROM rust:1.75-bookworm as rust-builder

WORKDIR /app

# Copy Rust source
COPY Cargo.toml ./
COPY src/ ./src/
COPY benches/ ./benches/

# Build release binary
RUN cargo build --release

# Python runtime stage - Debian stable minimal
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust library
COPY --from=rust-builder /app/target/release/libtruthsync_core.so /usr/local/lib/
COPY --from=rust-builder /app/target/release/truthsync_core /usr/local/bin/

# Copy Python code
COPY *.py ./

# Install Python dependencies
RUN pip install --no-cache-dir \
    prometheus-client \
    asyncio

# Set library path
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Expose metrics port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import truthsync_buffer; print('OK')" || exit 1

# Run application
CMD ["python", "truthsync_server.py"]
