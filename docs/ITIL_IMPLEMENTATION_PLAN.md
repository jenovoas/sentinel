# Implementation Plan: ITIL Incident Management Module

## Goal

Implement a production-ready ITIL v4 compliant Incident Management module integrated with Sentinel's existing dashboard, following cognitive UX design principles and enterprise compliance requirements (CMF, Ley 21.663, ISO 20000).

---

## User Review Required

> [!IMPORTANT]
> **Integration Approach**: This module will integrate with existing Sentinel architecture (FastAPI backend + Next.js frontend) without breaking changes to current functionality.

> [!WARNING]
> **Database Migration**: New tables will be created for incidents, categories, priorities, and audit trails. This requires an Alembic migration.

> [!CAUTION]
> **External Dependencies**: Integration with SIEM/ticketing systems (Splunk/QRadar/Jira) will use adapter pattern but requires API credentials configuration.

---

## Proposed Changes

### Backend Components

#### [NEW] [incident.py](file:///home/jnovoas/sentinel/backend/app/models/incident.py)

**Purpose**: SQLAlchemy models for ITIL Incident Management

**Key Models**:
- `Incident`: Core incident entity with ITIL lifecycle states
- `IncidentCategory`: ITIL categories (Hardware, Software, Security, etc.)
- `IncidentPriority`: P1-P4 priority levels
- `IncidentStatus`: ITIL states (New, Assigned, In Progress, Resolved, Closed)
- `IncidentAuditLog`: Audit trail for compliance (who/what/when/why)
- `IncidentAttachment`: Evidence/documentation attachments

**ITIL Compliance**:
- Maps to ITIL v4 Incident Management practice
- Includes SLA tracking fields (detection_time, response_time, resolution_time)
- Audit trail for regulatory compliance

---

#### [NEW] [incident_schemas.py](file:///home/jnovoas/sentinel/backend/app/schemas/incident_schemas.py)

**Purpose**: Pydantic schemas for API request/response validation

**Key Schemas**:
- `IncidentCreate`: Create new incident
- `IncidentUpdate`: Update incident fields
- `IncidentResponse`: Full incident details with relationships
- `IncidentList`: Paginated list response
- `IncidentStats`: Dashboard statistics

---

#### [NEW] [incident_service.py](file:///home/jnovoas/sentinel/backend/app/services/incident_service.py)

**Purpose**: Business logic for ITIL incident lifecycle

**Key Functions**:
1. **Detection & Logging** (ITIL Practice: Incident Logging)
   - `create_incident_from_event()`: Auto-create from SIEM/monitoring
   - `create_manual_incident()`: Manual incident creation
   - `correlate_incidents()`: Deduplication logic

2. **Categorization & Prioritization** (ITIL Practice: Categorization)
   - `categorize_incident()`: Auto-categorize based on rules
   - `calculate_priority()`: Impact × Urgency matrix
   - `assign_sla()`: Assign SLA based on priority

3. **Diagnosis** (ITIL Practice: Investigation)
   - `run_diagnosis_playbook()`: Execute diagnostic checks
   - `enrich_incident()`: Add context from monitoring/logs

4. **Escalation** (ITIL Practice: Escalation)
   - `assign_incident()`: Assign to team/owner
   - `escalate_incident()`: Auto-escalate if SLA breach
   - `notify_stakeholders()`: Send notifications

5. **Resolution** (ITIL Practice: Resolution)
   - `execute_resolution_playbook()`: Auto-remediation
   - `mark_resolved()`: Validate resolution
   - `request_user_confirmation()`: User acceptance

6. **Closure** (ITIL Practice: Closure)
   - `close_incident()`: Final closure with validation
   - `generate_post_mortem()`: Auto-generate RCA
   - `archive_incident()`: Archive for reporting

---

#### [NEW] [incidents.py](file:///home/jnovoas/sentinel/backend/app/routers/incidents.py)

**Purpose**: FastAPI router for incident endpoints

**Endpoints**:
```
GET    /api/v1/incidents              # List incidents (paginated, filtered)
POST   /api/v1/incidents              # Create manual incident
GET    /api/v1/incidents/{id}         # Get incident details
PATCH  /api/v1/incidents/{id}         # Update incident
DELETE /api/v1/incidents/{id}         # Delete incident (soft delete)

GET    /api/v1/incidents/stats        # Dashboard statistics
GET    /api/v1/incidents/{id}/timeline # Incident timeline (audit log)
POST   /api/v1/incidents/{id}/assign  # Assign incident
POST   /api/v1/incidents/{id}/escalate # Escalate incident
POST   /api/v1/incidents/{id}/resolve # Mark as resolved
POST   /api/v1/incidents/{id}/close   # Close incident

POST   /api/v1/incidents/from-siem    # Create from SIEM event (webhook)
```

**Authentication**: All endpoints require JWT authentication
**Authorization**: Role-based access (Admin, SOC, SRE, Viewer)

---

#### [MODIFY] [main.py](file:///home/jnovoas/sentinel/backend/app/main.py#L189)

**Changes**: Add incident router to FastAPI app

```python
# Add after line 189
from app.routers import incidents
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])
```

**Complexity**: Low (1 line change)

---

#### [MODIFY] [__init__.py](file:///home/jnovoas/sentinel/backend/app/models/__init__.py#L6)

**Changes**: Export new incident models

```python
# Add after line 6
from .incident import (
    Incident, IncidentCategory, IncidentPriority, 
    IncidentStatus, IncidentAuditLog, IncidentAttachment
)

# Update __all__ list
__all__ = [
    # ... existing exports ...
    "Incident", "IncidentCategory", "IncidentPriority",
    "IncidentStatus", "IncidentAuditLog", "IncidentAttachment"
]
```

---

#### [NEW] [YYYYMMDD_add_incident_tables.py](file:///home/jnovoas/sentinel/backend/alembic/versions/)

**Purpose**: Alembic migration for incident tables

**Tables Created**:
- `incident_categories`
- `incident_priorities`
- `incident_statuses`
- `incidents`
- `incident_audit_logs`
- `incident_attachments`

**Indexes**:
- `idx_incidents_status` (for filtering)
- `idx_incidents_priority` (for sorting)
- `idx_incidents_created_at` (for timeline)
- `idx_incidents_tenant_id` (for multi-tenancy)

---

### Frontend Components

#### [NEW] [IncidentDashboard.tsx](file:///home/jnovoas/sentinel/frontend/src/components/IncidentDashboard.tsx)

**Purpose**: Main incident management dashboard component

**Features**:
1. **Statistics Cards** (Cognitive: Visual Hierarchy)
   - Total incidents
   - Open incidents
   - P1/P2 critical incidents
   - Average resolution time
   - Color-coded by severity (Red=P1, Amber=P2, Green=P3/P4)

2. **Incident List** (Cognitive: Affordance + Color Psychology)
   - Sortable/filterable table
   - Priority badges (color-coded)
   - Status indicators (icon + text redundancy)
   - Quick actions (assign, escalate, resolve)
   - Hover effects for interactivity

3. **Filters** (Cognitive: Cognitive Load Reduction)
   - Status filter (New, Assigned, In Progress, Resolved, Closed)
   - Priority filter (P1, P2, P3, P4)
   - Category filter (Hardware, Software, Security, etc.)
   - Date range picker
   - Search by ID/description

4. **Create Incident Button** (Cognitive: Affordance)
   - Prominent CTA with icon
   - Opens modal form
   - Guided wizard for ITIL fields

**UX Principles Applied**:
- Visual hierarchy (stats → filters → list)
- Color psychology (Red=urgent, Green=resolved)
- Breathing room (generous padding/spacing)
- Smooth transitions (300ms animations)
- Icon + text redundancy (dual coding theory)

---

#### [NEW] [IncidentDetail.tsx](file:///home/jnovoas/sentinel/frontend/src/components/IncidentDetail.tsx)

**Purpose**: Detailed incident view with timeline

**Sections**:
1. **Header** (Cognitive: Visual Hierarchy)
   - Incident ID (prominent)
   - Priority badge (color-coded)
   - Status badge
   - Created/Updated timestamps

2. **Details Panel**
   - Category, priority, status
   - Assigned to (user/team)
   - SLA countdown (visual progress bar)
   - Description (rich text)

3. **Timeline** (Cognitive: Temporal Dynamics)
   - Chronological audit log
   - Who did what when
   - Color-coded by action type
   - Smooth scroll animations

4. **Actions Panel**
   - Assign button
   - Escalate button
   - Resolve button
   - Close button
   - Add comment
   - Attach file

**UX Principles Applied**:
- Gestalt law of proximity (related info grouped)
- Feedback loop (immediate visual confirmation)
- Consistency (matches existing Sentinel UI)

---

#### [NEW] [IncidentForm.tsx](file:///home/jnovoas/sentinel/frontend/src/components/IncidentForm.tsx)

**Purpose**: Create/edit incident form with validation

**Fields** (ITIL-compliant):
- Title (required)
- Description (required, rich text)
- Category (dropdown, required)
- Impact (High/Medium/Low)
- Urgency (High/Medium/Low)
- Priority (auto-calculated from Impact × Urgency)
- Affected service (optional)
- Affected users (optional)

**Validation**:
- Client-side validation (Zod schema)
- Server-side validation (Pydantic)
- Error messages (clear, actionable)

**UX Principles Applied**:
- Progressive disclosure (show advanced fields on demand)
- Inline validation (immediate feedback)
- Tooltips for help (cognitive load reduction)

---

#### [MODIFY] [page.tsx](file:///home/jnovoas/sentinel/frontend/src/app/dashboard/page.tsx)

**Changes**: Add Incident Management section to dashboard

**New Section** (after existing sections):
```tsx
{/* Incident Management Section */}
<section className="mb-8">
  <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
    <AlertTriangle className="text-amber-500" />
    Incident Management
  </h2>
  <IncidentDashboard />
</section>
```

**Complexity**: Low (add new section, no breaking changes)

---

#### [NEW] [useIncidents.ts](file:///home/jnovoas/sentinel/frontend/src/hooks/useIncidents.ts)

**Purpose**: React hook for incident data fetching

**Features**:
- Fetch incidents (with pagination/filtering)
- Create incident
- Update incident
- Delete incident
- Real-time updates (optional WebSocket)
- Optimistic UI updates
- Error handling

**Technology**: React Query (TanStack Query) for caching

---

### Configuration Files

#### [NEW] [itil_policies.yaml](file:///home/jnovoas/sentinel/backend/app/config/itil_policies.yaml)

**Purpose**: Configurable ITIL policies (no hardcoding)

**Sections**:
1. **Categorization Rules**
   ```yaml
   categorization:
     keywords:
       hardware: ["server", "disk", "cpu", "memory", "network"]
       software: ["application", "bug", "crash", "error"]
       security: ["intrusion", "malware", "breach", "unauthorized"]
   ```

2. **Prioritization Matrix**
   ```yaml
   prioritization:
     matrix:
       high_impact_high_urgency: P1
       high_impact_medium_urgency: P2
       medium_impact_high_urgency: P2
       # ... etc
   ```

3. **SLA Definitions**
   ```yaml
   sla:
     P1:
       response_time_minutes: 15
       resolution_time_hours: 4
     P2:
       response_time_minutes: 30
       resolution_time_hours: 8
   ```

4. **Escalation Rules**
   ```yaml
   escalation:
     P1:
       team: "SOC-L3"
       notification: ["pagerduty", "sms", "email"]
     P2:
       team: "SOC-L2"
       notification: ["slack", "email"]
   ```

5. **Auto-Assignment Rules**
   ```yaml
   assignment:
     security:
       team: "SOC"
       on_call_rotation: true
     performance:
       team: "SRE"
   ```

---

## Verification Plan

### Automated Tests

#### 1. Backend Unit Tests

**File**: `backend/tests/test_incident_service.py`

**Tests**:
- `test_create_incident()`: Verify incident creation
- `test_categorize_incident()`: Verify auto-categorization
- `test_calculate_priority()`: Verify priority matrix
- `test_assign_incident()`: Verify assignment logic
- `test_escalate_incident()`: Verify escalation rules
- `test_close_incident()`: Verify closure validation

**Run Command**:
```bash
cd backend
pytest tests/test_incident_service.py -v
```

---

#### 2. Backend Integration Tests

**File**: `backend/tests/test_incident_api.py`

**Tests**:
- `test_create_incident_endpoint()`: POST /api/v1/incidents
- `test_list_incidents_endpoint()`: GET /api/v1/incidents
- `test_update_incident_endpoint()`: PATCH /api/v1/incidents/{id}
- `test_incident_timeline_endpoint()`: GET /api/v1/incidents/{id}/timeline
- `test_unauthorized_access()`: Verify authentication

**Run Command**:
```bash
cd backend
pytest tests/test_incident_api.py -v
```

---

#### 3. Database Migration Test

**Verification**:
```bash
cd backend
# Generate migration
alembic revision --autogenerate -m "Add incident management tables"

# Apply migration
alembic upgrade head

# Verify tables created
psql -U sentinel -d sentinel -c "\dt incident*"
```

**Expected Output**: 6 tables created (categories, priorities, statuses, incidents, audit_logs, attachments)

---

### Manual Testing

#### 1. Frontend Dashboard Test

**Steps**:
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:3000/dashboard`
4. Verify "Incident Management" section appears
5. Click "Create Incident" button
6. Fill form and submit
7. Verify incident appears in list
8. Click incident to view details
9. Verify timeline shows creation event

**Expected Result**: Incident created, visible in list, detail view works

---

#### 2. ITIL Workflow Test

**Steps**:
1. Create incident with High Impact + High Urgency
2. Verify priority auto-calculated to P1
3. Verify SLA countdown starts
4. Click "Assign" → assign to SOC team
5. Verify status changes to "Assigned"
6. Click "Escalate" → escalate to L3
7. Verify notification sent (check logs)
8. Click "Resolve" → mark as resolved
9. Verify status changes to "Resolved"
10. Click "Close" → close incident
11. Verify post-mortem generated

**Expected Result**: Full ITIL lifecycle works end-to-end

---

#### 3. UX/Cognitive Design Test

**Steps**:
1. Open dashboard
2. Observe visual hierarchy (stats → filters → list)
3. Hover over incident row → verify smooth transition
4. Check color coding (P1=red, P2=amber, P3/P4=green)
5. Verify icon + text redundancy
6. Check tooltips on hover
7. Test mobile responsive (resize browser)

**Expected Result**: Cognitive UX principles applied correctly

---

#### 4. SIEM Integration Test (Optional)

**Steps**:
1. Configure SIEM adapter (Splunk/QRadar)
2. Send test event to webhook: `POST /api/v1/incidents/from-siem`
3. Verify incident auto-created
4. Verify auto-categorization works
5. Verify priority calculated correctly

**Expected Result**: SIEM events create incidents automatically

---

### Performance Testing

**Load Test** (optional):
```bash
# Install k6
brew install k6

# Run load test
k6 run scripts/load_test_incidents.js
```

**Expected**: Handle 100 concurrent users, <200ms P95 latency

---

## Dependencies

### Backend
- No new dependencies (uses existing FastAPI, SQLAlchemy, Pydantic)

### Frontend
- `@tanstack/react-query`: Data fetching/caching
- `lucide-react`: Icons (already installed)
- `date-fns`: Date formatting (already installed)

---

## Rollout Plan

### Phase 1: Backend (Week 1)
1. Create models (`incident.py`)
2. Create schemas (`incident_schemas.py`)
3. Create service (`incident_service.py`)
4. Create router (`incidents.py`)
5. Create migration
6. Write tests
7. Deploy to staging

### Phase 2: Frontend (Week 1)
1. Create components (`IncidentDashboard.tsx`, `IncidentDetail.tsx`, `IncidentForm.tsx`)
2. Create hook (`useIncidents.ts`)
3. Integrate with dashboard
4. Test UX/cognitive design
5. Deploy to staging

### Phase 3: Integration (Week 2)
1. Configure ITIL policies (`itil_policies.yaml`)
2. Test SIEM integration
3. Test full ITIL workflow
4. Performance testing
5. Security audit
6. Deploy to production

---

## Success Criteria

- ✅ All automated tests pass
- ✅ ITIL v4 compliance verified
- ✅ Cognitive UX principles applied
- ✅ No breaking changes to existing functionality
- ✅ Performance: <200ms P95 latency
- ✅ Security: Authentication/authorization working
- ✅ Audit trail complete (who/what/when/why)
- ✅ Mobile responsive
- ✅ Accessible (WCAG AA)

---

**Estimated Effort**: 2 weeks (1 developer)  
**Risk Level**: Low (follows existing patterns, no breaking changes)  
**Business Impact**: High (enables sales to banks/enterprises)
