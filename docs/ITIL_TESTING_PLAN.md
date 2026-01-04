# ITIL Incident Management - Testing Plan

**Date**: 2025-12-16  
**Status**: Ready to Execute  
**Duration**: ~30 minutes

---

## Test Environment

```yaml
Backend: http://localhost:8000
Frontend: http://localhost:3000
Database: PostgreSQL (local)
Status: ✅ Migration applied
```

---

## Test Suite

### 1. Database Verification (5 min)

**Objetivo**: Verificar que las tablas se crearon correctamente

**Steps**:
```bash
# Verificar tablas incidents
cd backend
python3 -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
incident_tables = [t for t in tables if 'incident' in t]
print('Incident tables:', incident_tables)
"
```

**Expected Output**:
```
Incident tables: ['incidents', 'incident_audit_logs', 'incident_attachments']
```

---

### 2. Backend API Tests (10 min)

#### 2.1 Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

**Expected**: Server starts on http://localhost:8000

---

#### 2.2 Test Stats Endpoint
```bash
curl http://localhost:8000/api/v1/incidents/stats
```

**Expected Response**:
```json
{
  "total_incidents": 0,
  "open_incidents": 0,
  "critical_incidents": 0,
  "p1_count": 0,
  "p2_count": 0,
  "p3_count": 0,
  "p4_count": 0,
  "new_count": 0,
  "assigned_count": 0,
  "in_progress_count": 0,
  "resolved_count": 0,
  "closed_count": 0,
  "category_breakdown": {},
  "avg_resolution_time_hours": null,
  "sla_compliance_rate": null
}
```

---

#### 2.3 Test Create Incident (Manual)

**Note**: Requires authentication. Skip for now or test with valid token.

---

### 3. Frontend Integration Test (10 min)

#### 3.1 Start Frontend
```bash
cd frontend
npm run dev
```

**Expected**: Server starts on http://localhost:3000

---

#### 3.2 Visual Verification

1. Open browser: `http://localhost:3000/dashboard`
2. Scroll to "Incident Management" card
3. Verify:
   - ✅ Card appears in grid
   - ✅ "All Clear!" message (no incidents)
   - ✅ Stats show 0/0/0/0
   - ✅ Green/emerald color scheme
   - ✅ Buttons visible ("View All" + "Create")

**Screenshot**: Take screenshot for documentation

---

### 4. E2E Workflow Test (5 min)

**Objetivo**: Crear incident via API y verificar en dashboard

#### 4.1 Create Test Incident (Python)

```python
import requests
import uuid

# Create test user and tenant (mock)
incident_data = {
    "title": "Test Incident - Database Timeout",
    "description": "Users unable to access application due to database connection timeouts",
    "category": "software",
    "impact": "high",
    "urgency": "high",
    "affected_service": "user-api",
    "affected_users": 150,
    "source": "manual"
}

# Note: Requires auth token
# response = requests.post(
#     "http://localhost:8000/api/v1/incidents",
#     json=incident_data,
#     headers={"Authorization": "Bearer <token>"}
# )
```

**Expected**: Incident created with P1 priority (high impact + high urgency)

---

#### 4.2 Verify in Dashboard

1. Refresh dashboard
2. Verify:
   - ✅ Stats updated (1 total, 1 open, 1 critical)
   - ✅ Incident appears in "Recent Incidents"
   - ✅ P1 badge is RED (calm design)
   - ✅ Status badge shows "new"

---

### 5. Calm Design Verification (5 min)

**Objetivo**: Verificar principios de diseño calmado

#### Test Cases:

**5.1 Empty State (No Incidents)**
- ✅ "All Clear!" message prominent
- ✅ Emerald/green color scheme
- ✅ Positive tone (" All Clear!")

**5.2 P3/P4 Incidents (Low Priority)**
- ✅ Blue/gray badges (NOT red)
- ✅ Calm, informative tone
- ✅ No urgency indicators

**5.3 P2 Incidents (High Priority)**
- ✅ Amber/yellow badges
- ✅ "Attention" tone (not panic)
- ✅ Visible but not alarming

**5.4 P1 Incidents (Critical)**
- ✅ RED badge (ONLY for P1)
- ✅ "🔴 Critical" indicator
- ✅ Prominent but not hysterical

**5.5 Layout**
- ✅ Generous spacing (breathing room)
- ✅ Smooth transitions (300ms)
- ✅ Icon + text redundancy

---

## Test Results Template

```markdown
## Test Execution Results

**Date**: YYYY-MM-DD  
**Tester**: [Name]  
**Duration**: [XX] minutes

### Database Verification
- [ ] Tables created: incidents, incident_audit_logs, incident_attachments
- [ ] Indexes created correctly
- [ ] Foreign keys valid

### Backend API
- [ ] Server starts without errors
- [ ] /api/v1/incidents/stats returns valid JSON
- [ ] Stats show zero incidents initially
- [ ] No console errors

### Frontend Integration
- [ ] Dashboard loads successfully
- [ ] Incident Management card visible
- [ ] "All Clear!" state displays correctly
- [ ] Colors match calm design (green/emerald)
- [ ] Buttons functional

### Calm Design
- [ ] Empty state is positive
- [ ] P1 uses red (critical only)
- [ ] P2 uses amber (attention)
- [ ] P3/P4 use blue/gray (calm)
- [ ] Spacing is generous
- [ ] Transitions are smooth

### Issues Found
- None / [List issues]

### Overall Status
- [ ] ✅ PASS - Ready for demo
- [ ] ⚠ PARTIAL - Minor issues
- [ ] ❌ FAIL - Major issues

### Notes
[Additional observations]
```

---

## Success Criteria

- ✅ All database tables exist
- ✅ Backend API responds correctly
- ✅ Frontend card displays
- ✅ Calm design principles applied
- ✅ No console errors
- ✅ Mobile responsive (bonus)

---

## Known Limitations (Expected)

1. **Authentication**: Endpoints require JWT token (normal)
2. **Empty Data**: No incidents initially (expected)
3. **Mock Data**: May need to create test user/tenant first

---

## Next Steps After Testing

1. ✅ Document test results
2. ⏳ Create demo video (5 min)
3. ⏳ Prepare pitch deck CORFO
4. ⏳ Schedule pilot with ex-empleador

---

**Ready to execute**: YES ✅  
**Estimated time**: 30 minutes  
**Risk**: Low (non-destructive tests)
