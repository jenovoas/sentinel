# ADR-001: Canonical Cortex Path

**Status**: Accepted
**Date**: 2026-01-28
**Authors**: Architecture Team

## Context (ISO/IEC/IEEE 42010)

The project contains multiple historical Cortex locations:
- `sentinel-cortex/` (buildable Rust crate with Cargo.toml)
- `src/sentinel-cortex/` (legacy mirror without Cargo.toml)

This duplication creates ambiguity for build, integration, and operational procedures. The system requires a single canonical path to align architecture, deployment, and service management.

## Decision

- The canonical path for the Cortex implementation is now **`core/cortex/`**.
- `core/cortex/` is implemented as a symlink to `sentinel-cortex/` to avoid duplication and preserve existing artifacts.
- `src/sentinel-cortex/` is treated as **legacy reference** and is not used for builds or runtime.

## ITIL Service Impact

- **Service Design**: Canonical path removes ambiguity for build pipelines and service definitions.
- **Service Transition**: No data migration required; symlink provides immediate compatibility.
- **Service Operation**: Operational tooling should reference `core/cortex/` for clarity.
- **Continual Improvement**: Legacy path can be audited and documented without deletion.

## Consequences

- All new Rust Cortex work must target `core/cortex/` (via symlink).
- Build and deployment scripts should reference `core/cortex/` for clarity.
- Legacy `src/sentinel-cortex/` remains untouched and available for historical review.

## Alternatives Considered

1) Keep `sentinel-cortex/` as canonical without alias.
2) Move all files into `core/cortex/` and remove old paths. (Rejected due to preservation constraints.)

## Related Documents

- `docs/EBPF_CORTEX_STATUS.md`
- `AI_PRIME_DIRECTIVES.md`
- `docs/ARCHITECTURE.md`
