---
title: Búsqueda de dataset real para TruthSync
date: 2026-11-12
tags:
  - truthsync
  - benchmark
  - dataset
---

# Búsqueda de dataset real para TruthSync

## Estado

El benchmark de 1.000.000 de claims ejecutado el 2026-11-11 es sintético y no cierra el requisito P2.1 de medir con al menos 1.000.000 de claims reales. No se repitió ese benchmark.

La búsqueda focal de archivos de datos (`.jsonl`, `.csv`, `.parquet`, `.tsv` y `.ndjson`) en `truthsync-core`, `backend`, `docs`, `data`, `datasets` y `quantum/experiments` no encontró un corpus candidato versionado en esas ubicaciones.

## Fuentes evaluadas

- [Fact-Check Insights — guía oficial](https://www.factcheckinsights.org/guide): compila ClaimReview/MediaReview publicados por organizaciones verificadas; incluye el campo `claimReviewed` y declara licencia CC BY. La descarga requiere solicitar acceso. [Reporters’ Lab — descripción y volumen publicado](https://reporterslab.org/2024/06/20/what-exactly-is-the-fact-check-insights-dataset/) informa más de 240.000 claims revisados en junio de 2024, no un millón. La guía consultada no publica un conteo actual que demuestre que hoy alcance el umbral.
- [MultiClaim, artículo de ACL Anthology](https://aclanthology.org/2023.emnlp-main.1027/): reporta 205.751 fact-checks profesionales y 28.092 publicaciones de redes sociales. Es real y multilingüe, pero queda por debajo del umbral de 1.000.000.
- [MuMiN, sitio oficial](https://mumin-dataset.github.io/) y [artículo](https://arxiv.org/abs/2202.11684): el conjunto grande relaciona 21.565.018 publicaciones con 12.914 claims revisados. El artículo especifica que el paquete distribuye IDs de publicaciones/usuarios y palabras clave, no el texto de los claims ni de los tweets, por términos de Twitter y copyright. Por ello, los 21 millones no se cuentan como claims ni sirven como corpus textual listo para este benchmark.

## Decisión y desbloqueo

No se encontró una fuente accesible y documentada que demuestre contener 1.000.000 o más de textos de claims reales aptos para esta medición. No se duplicarán registros, se contarán publicaciones como claims ni se sustituirá el corpus por datos sintéticos. P2.1 queda abierto hasta que se proporcione un dataset con procedencia, volumen deduplicable y condiciones de uso verificables, o se defina otro umbral/fuente aceptable.

No se modificó el código de TruthSync y no se ejecutó el benchmark. Este informe registra únicamente la búsqueda y sus límites.
