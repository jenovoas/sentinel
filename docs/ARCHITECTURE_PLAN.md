# Architecture Consolidation Plan

## Goal
To update `docs/ARCHITECTURE.md` to reflect the current state of the Sentinel system, specifically integrating the "TruthSync" dual-container architecture and the "Document Vault" security architecture. This will provide a single source of truth for the system's design.

## User Review Required
> [!NOTE]
> This plan focuses on documentation updates. No code changes are currently proposed, but discrepancies found during documentation might lead to future code tasks.

## Proposed Changes

### Documentation

#### [MODIFY] [docs/ARCHITECTURE.md](file:///home/jnovoas/sentinel/docs/ARCHITECTURE.md)
- **TruthSync Integration**:
  - Add "TruthSync" to the High-Level Architecture diagram (or a new dedicated section).
  - Describe the "Dual-Container" concept (Core vs. Edge) in the Components section.
  - List new services: `truth-core`, `truthsync-edge`.
- **Document Vault Integration**:
  - Add "Document Vault" to the Component Details.
  - Describe the encryption flow (AES-256-GCM, Zero-Knowledge) in the Security Features section.
- **Service Inventory**:
  - Update the Service Inventory table to include TruthSync and Document Vault services if they are distinct containers/services.

#### [MODIFY] [docs/TASK.md](file:///home/jnovoas/sentinel/docs/TASK.md)
- Ensure the roadmap reflects the ongoing architectural work (already updated).

## Verification Plan
### Manual Verification
- **Visual Review**: Open `docs/ARCHITECTURE.md` and verify that:
    - The diagram includes TruthSync.
    - The text descriptions effectively summarize `TRUTHSYNC_ARCHITECTURE.md` and `DOCUMENT_VAULT.md`.
    - The version number and date are updated.
