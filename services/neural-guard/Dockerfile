# Fase final
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates libssl3 libelf1 zlib1g libzstd1 && rm -rf /var/lib/apt/lists/*
COPY neural-guard.bin /usr/local/bin/neural-guard
RUN chmod +x /usr/local/bin/neural-guard
RUN useradd -m -u 1000 sentinel
USER sentinel
CMD ["neural-guard"]
