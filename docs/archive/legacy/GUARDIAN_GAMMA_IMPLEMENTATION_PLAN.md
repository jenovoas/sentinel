# Guardian Gamma Implementation Plan

**Goal**: Implement Human-in-the-Loop (HITL) interface for critical security decisions  
**Time estimate**: 2-3 hours  
**Status**: Planning

---

## What Guardian Gamma Does

**Purpose**: Allow human to validate critical decisions from Guardian Alpha and Beta

**When it triggers**:
- Guardian Alpha blocks a binary (potential false positive)
- Guardian Beta detects anomaly in telemetry (needs human judgment)
- System encounters unknown threat pattern

**How it works**:
1. Guardian Alpha/Beta makes decision
2. If confidence < threshold, escalate to Gamma
3. Human reviews context and evidence
4. Human approves/denies/modifies decision
5. System learns from human feedback

---

## Architecture

### Components

**1. Decision Queue**
- Store pending decisions
- Priority-based ordering
- Timeout handling

**2. Web Interface**
- Dashboard showing pending decisions
- Context display (logs, evidence)
- Approve/Deny/Modify buttons
- Feedback mechanism

**3. API Endpoints**
- POST /gamma/decision - Create decision request
- GET /gamma/pending - List pending decisions
- POST /gamma/approve/:id - Approve decision
- POST /gamma/deny/:id - Deny decision
- POST /gamma/feedback/:id - Provide feedback

**4. Integration Layer**
- Connect to Guardian Alpha (eBPF events)
- Connect to Guardian Beta (telemetry events)
- Notification system (email, Slack, etc)

---

## Implementation Steps

### Phase 1: Backend (1 hour)
- [ ] Create `guardian_gamma_service.py`
- [ ] Decision queue (PostgreSQL table)
- [ ] API endpoints
- [ ] Integration with Alpha/Beta

### Phase 2: Frontend (1 hour)
- [ ] Gamma dashboard page
- [ ] Decision card component
- [ ] Approve/Deny UI
- [ ] Real-time updates (WebSocket)

### Phase 3: Integration (30 min)
- [ ] Connect Alpha to Gamma
- [ ] Connect Beta to Gamma
- [ ] Test end-to-end flow

### Phase 4: Testing (30 min)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

---

## Database Schema

```sql
CREATE TABLE gamma_decisions (
    id SERIAL PRIMARY KEY,
    guardian_source VARCHAR(10) NOT NULL, -- 'alpha' or 'beta'
    decision_type VARCHAR(50) NOT NULL,
    context JSONB NOT NULL,
    evidence JSONB,
    confidence FLOAT,
    status VARCHAR(20) DEFAULT 'pending', -- pending/approved/denied
    human_decision VARCHAR(20),
    human_feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    decided_at TIMESTAMP,
    timeout_at TIMESTAMP
);
```

---

## API Design

### Create Decision
```python
POST /gamma/decision
{
    "guardian": "alpha",
    "type": "binary_block",
    "context": {
        "binary_path": "/usr/bin/suspicious",
        "signature": "unknown",
        "hash": "abc123..."
    },
    "confidence": 0.65,
    "timeout_minutes": 30
}
```

### Get Pending
```python
GET /gamma/pending
Response: [
    {
        "id": 1,
        "guardian": "alpha",
        "type": "binary_block",
        "context": {...},
        "created_at": "2025-12-21T20:00:00Z"
    }
]
```

### Approve/Deny
```python
POST /gamma/approve/1
{
    "feedback": "Known internal tool, safe to allow"
}
```

---

## Frontend Design

### Dashboard Layout
```
┌─────────────────────────────────────────┐
│  Guardian Gamma - Pending Decisions     │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Guardian Alpha - Binary Block     │ │
│  │ Binary: /usr/bin/suspicious       │ │
│  │ Confidence: 65%                   │ │
│  │ Created: 2 minutes ago            │ │
│  │                                   │ │
│  │ [View Details] [Approve] [Deny]  │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Guardian Beta - Anomaly Detected  │ │
│  │ Metric: CPU spike                 │ │
│  │ Confidence: 72%                   │ │
│  │ Created: 5 minutes ago            │ │
│  │                                   │ │
│  │ [View Details] [Approve] [Deny]  │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

---

## Integration Points

### Guardian Alpha → Gamma
```python
# In eBPF LSM (when confidence < threshold)
if confidence < 0.8:
    decision_id = gamma_service.create_decision(
        guardian="alpha",
        type="binary_block",
        context={"binary": binary_path, "hash": hash},
        confidence=confidence
    )
    # Wait for human decision or timeout
    result = gamma_service.wait_for_decision(decision_id, timeout=30)
    return result  # allow or deny
```

### Guardian Beta → Gamma
```python
# In Dual-Lane (when anomaly detected)
if anomaly_score > threshold and confidence < 0.8:
    decision_id = gamma_service.create_decision(
        guardian="beta",
        type="anomaly_detected",
        context={"metric": metric, "value": value},
        confidence=confidence
    )
    # Continue processing, human reviews async
```

---

## Testing Plan

### Unit Tests
- [ ] Decision creation
- [ ] Decision approval/denial
- [ ] Timeout handling
- [ ] Feedback storage

### Integration Tests
- [ ] Alpha → Gamma flow
- [ ] Beta → Gamma flow
- [ ] Frontend → Backend

### Manual Tests
- [ ] Create decision from Alpha
- [ ] Review in dashboard
- [ ] Approve decision
- [ ] Verify Alpha receives approval

---

## Success Criteria

- [ ] Backend API working (all endpoints)
- [ ] Frontend dashboard functional
- [ ] Guardian Alpha integration working
- [ ] Guardian Beta integration working
- [ ] Tests passing
- [ ] Documentation complete

---

## Next Steps

1. Create backend service
2. Create database migration
3. Implement API endpoints
4. Create frontend components
5. Integrate with Alpha/Beta
6. Test end-to-end

**Ready to start?**
