# Fase final (Binario pre-compilado en Host para máxima fidelidad técnica)
FROM alpine:3.22
RUN apk add --no-cache ca-certificates libgcc libstdc++ libssl3 libelf zlib zstd-libs
# Copiamos el binario verificado que compilamos en el host
COPY services/neural-guard/neural-guard.bin /usr/local/bin/neural-guard
RUN chmod +x /usr/local/bin/neural-guard
RUN adduser -D -u 1000 sentinel
USER sentinel
CMD ["neural-guard"]
