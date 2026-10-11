# AI & Interactive Experience Integration Plan (Consolidated)

## 1. Executive Summary
This document outlines the strategy to transform Sentinel Cortex from a static tool into a **Living Cognitive Organism**. 
We unify the **Semantic Shell (SemSH)**, the **Trinity 3D Experience**, and the **TruthSync Psychology Pipeline** into a cohesive "Cognitive Interface" that the user doesn't just use, but *interacts* with.

## 2. Core Components

### A. The "SemSH" Cognitive Loop (Phase 2)
*   **Goal:** Replace stiff CLI commands with "Intentions".
*   **Architecture:** `User Intent` -> `Llama 3.2` -> `Safety Check` -> `Execution`.
*   **Integration:**
    *   **Frontend:** A global "Command Palette" (`Ctrl+K`) or a floating chat widget (`/cortex`) that accepts natural language.
    *   **Backend:** `/api/v1/cortex/intent` endpoint.
    *   **Safety:** Every automated command is dry-run first and requires explicit user confirmation if it exceeds risk threshold (Risk Level > 3).

### B. Trinity 3D Experience (Emotional UX)
*   **Goal:** A "Screensaver/Meditative" mode that visualizes the system's "Heartbeat" coherently.
*   **Visuals:**
    *   **Physics:** Merkabah (Geometry).
    *   **Biology:** Neural Hierarchy.
    *   **Technology:** Flower of Life (Nodes network).
*   **Tech Stack:** Three.js + React Three Fiber.
*   **Data Source:** Real-time WebSockets from `/monitoring/live` (mapped to visual intensity).
*   **Implementation Location:** `/trinity` page (Landing Page hero alternative or Screensaver).

### C. TruthSync Psychology Pipeline (Behavioral Analysis)
*   **Goal:** Automated truth verification using behavioral patterns extracted from academic literature.
*   **Pipeline:** `Text Extraction` -> `GPT-4 Pattern Recog` -> `n8n Workflows`.
*   **Integration:**
    *   **Frontend:** "/truth" dashboard for analyzing text/audio input.
    *   **Backend:** Connects to n8n Webhooks.

## 3. Implementation Roadmap (AI & Interactive)

### Phase 1: Cognitive Chat (`/cortex`)
*   **Status:** ✅ **DONE (MVP)**
*   **Next Steps:**
    *   Give Cortex "Eyes": Allow it to read current page context (e.g., "Analyze these logs on screen").
    *   Give Cortex "Hands": Allow it to propose `sctl` commands to fix issues found in logs.

### Phase 2: Trinity Visualizer (`/trinity`)
*   **Status:** 🚧 **CONCEPT**
*   **Action Plan:**
    1.  Install `three`, `@react-three/fiber`, `@react-three/drei`.
    2.  Create `TrinityScene.tsx` component.
    3.  Map `System Load` -> `Rotation Speed`.
    4.  Map `Threat Level` -> `Color Shift` (Blue -> Red).

### Phase 3: Semantic Command Palette
*   **Status:** 🚧 **PENDING**
*   **Action Plan:**
    1.  Implement `cmdk` based global search.
    2.  Integrate "Ask Cortex" directly in the command bar.
    3.  Build the "Confirmation/Diff" UI for AI actions.

## 4. Technical Requirements
*   **Models:** Ensure efficient local inference (Llama-3-8B-Quantized) for `SemSH`.
*   **Performance:** Trinity 3D must disable itself on low-power devices.
*   **Privacy:** Psychology pipeline data must remain strictly local (except when explicitly using GPT-4 API).

## 5. Success Metrics
*   **Engagement:** Users spend >2 mins in "Trinity" mode.
*   **Utility:** 50% of admin tasks performed via "Natural Language" instead of CLI.
*   **Accuracy:** >90% success rate in translating intent to valid bash commands.
