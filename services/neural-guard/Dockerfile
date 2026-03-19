# Fase de construcción
FROM rust:1-slim as builder
WORKDIR /usr/src/app
COPY . .
RUN cargo install --path .

# Fase final
FROM debian:stable-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/neural-guard /usr/local/bin/neural-guard
CMD ["neural-guard"]
