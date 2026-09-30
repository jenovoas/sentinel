# Fase final (Binario pre-compilado en Host para máxima fidelidad técnica)
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates libssl3 libelf1 zlib1g libzstd1 && rm -rf /var/lib/apt/lists/*
# Copiamos el binario verificado que compilamos en el host
COPY services/neural-guard/neural-guard.bin /usr/local/bin/neural-guard
RUN chmod +x /usr/local/bin/neural-guard
RUN useradd -m -u 1000 sentinel
USER sentinel
CMD ["neural-guard"]
