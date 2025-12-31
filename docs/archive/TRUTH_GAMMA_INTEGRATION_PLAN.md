# Truth Algorithm + Guardian Gamma Integration Plan

## 🎯 Architecture

```
Guardian Gamma Decision → Truth Algorithm → Certification → Display in UI
```

## 📋 Integration Points

### 1. Backend (FastAPI)
- Add Truth Algorithm to `guardian_gamma/service.py`
- Create `/api/gamma/certify/{decision_id}` endpoint
- Store truth_score in Decision model

### 2. Frontend (Next.js)
- Display Truth Score badge
- Show verification sources
- Add certification details modal

### 3. Database
- Add `truth_score` field to decisions table
- Add `certification` JSON field for details

## 🔧 Implementation Steps

### Step 1: Backend Integration
```python
# guardian_gamma/service.py
from truth_algorithm.certification_generator import CertificationGenerator

class GuardianGammaService:
    def __init__(self):
        self.certifier = CertificationGenerator(provider=SearchProvider.PERPLEXITY)
    
    async def certify_decision(self, decision_id: str):
        decision = await self.get_decision(decision_id)
        certificate = self.certifier.certify(decision.context)
        decision.truth_score = certificate.truth_score
        decision.certification = certificate.to_dict()
        await self.save_decision(decision)
```

### Step 2: API Endpoint
```python
@app.post("/api/gamma/certify/{decision_id}")
async def certify_decision(decision_id: str):
    service = GuardianGammaService()
    await service.certify_decision(decision_id)
    return {"status": "certified"}
```

### Step 3: Frontend Display
```tsx
// components/TruthBadge.tsx
export function TruthBadge({ score }: { score: number }) {
  const color = score >= 0.8 ? 'green' : score >= 0.6 ? 'yellow' : 'red';
  return (
    <Badge color={color}>
      Truth Score: {(score * 100).toFixed(0)}%
    </Badge>
  );
}
```

## ✅ Benefits

1. **Auto-verification** of HITL decisions
2. **Transparency** with source citations
3. **Audit trail** with certificates
4. **Patent strength** - self-validating system

---

**Ready to implement?** ✅
