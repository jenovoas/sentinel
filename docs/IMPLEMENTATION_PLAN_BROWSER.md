# Secure Browser Implementation Plan

**Goal**: Implement a privacy-focused browser that sanitizes content and routes traffic securely (supporting Tor).

## User Review Required
> [!IMPORTANT]
> **Tor Requirement**: The backend expects a SOCKS5 proxy at `127.0.0.1:9050`. If Tor is not running, it gracefully falls back to direct connection (with a log warning) OR fails if strict mode is enabled. For this POC, we default to direct connection if Tor is unreachable, but the architecture is Tor-ready.

## Proposed Changes

### Backend (FastAPI)
#### [NEW] `backend/poc/browser_service.py`
- (Already implemented) Core logic for fetching and sanitizing.

#### [MODIFY] `backend/poc/main.py`
- Add `POST /browser/browse` endpoint.
- Accepts `url` and `use_tor` (boolean).
- Returns sanitized HTML content.

### Frontend (Next.js)
#### [MODIFY] `frontend/poc/src/app/page.tsx`
- Add "Secure Browser" section to the dashboard.
- Features:
    - URL Input Bar
    - "Tor Mode" Toggle
    - "Reader View" container (iframe or div with shadow DOM) to render sanitized HTML.
    - Status indicator (Secure/Insecure).

## Verification Plan

### Automated Tests
- **Unit Test**: Run `python backend/poc/browser_service.py` (Existing).
- **Integration Test**: 
    1. Start Backend: `cd backend/poc && uvicorn main:app --reload`
    2. Curl Request:
       ```bash
       curl -X POST "http://localhost:8000/browser/browse" \
            -H "Content-Type: application/json" \
            -d '{"url": "https://example.com"}'
       ```
    3. Verify JSON response contains sanitized HTML.

### Manual Verification
1. Open Sentinel Vault Frontend.
2. Navigate to "Secure Browser" section.
3. Enter `https://example.com`.
4. Verify the page content loads cleanly (no ads, plain text/images).
5. Toggle "Tor Mode" and retry (expect success if Tor runs, or error handler/fallback).
6. Verify no scripts executed in the browser console from the target site.
