# 🎨 Frontend Polish Plan: "Interview Ready"

**Goal**: Elevate the frontend code from "Functional" to "Senior Professional".
**Focus**: Code abstractions, performance patterns, and visual polish.

## 1. Code Quality & Abstractions (The "Senior" Signals)

### A. Icon Strategy
- **Current**: Hardcoded SVGs inside `CognitiveNavBar.tsx`. Clutters lines 51-157.
- **Plan**:
    - [ ] Install `lucide-react` (Industry standard).
    - [ ] Replace hardcoded SVGs with Lucide icons (e.g., `<Activity />`, `<Shield />`).
    - **Why**: Shows knowledge of maintainability.

### B. Styling Architecture
- **Current**: Complex logical strings for color variants (lines 164-195).
- **Plan**:
    - [ ] Install `class-variance-authority` (CVA) and `clsx`.
    - [ ] Create `components/ui/badge.variants.ts` and `nav-item.variants.ts`.
    - **Why**: Demonstrates scalable design system thinking.

### C. Data Access Layer
- **Current**: `useEffect` + `fetch` inside UI components (`IncidentManagementCard.tsx`).
- **Plan**:
    - [ ] Create simple custom hooks: `hooks/useIncidents.ts`.
    - [ ] (Bonus) Use `swr` for cache/revalidation.
    - **Why**: Separation of Concerns (UI vs Data).

## 2. Visual Polish (The "Wow" Factor)

### A. Loading States
- **Current**: Text says "Loading incident data...".
- **Plan**:
    - [ ] Implement `Skeleton` component (`shadcn/ui` style).
    - [ ] Show a pulsing gray structure matching the card layout while loading.

### B. Micro-Interactions
- **Current**: CSS transitions.
- **Plan**:
    - [ ] Add `framer-motion` for entrance animations (`fadeInUp` for cards).

## 3. Action Items (Immediate)
1.  Refactor `CognitiveNavBar` to use `lucide-react`.
2.  Extract `useIncidents` hook.
3.  Add `Skeleton` loader to `IncidentManagementCard`.

> **Recruiter Takeaway**: "This candidate writes clean, modular, and maintainable code."
