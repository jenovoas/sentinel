# 🚀 N8N Quick Start - Investor Demo

## Goal
Get N8N running with 3 fail-safe playbooks in **2-3 hours**.

---

## Step 1: Start N8N (5 minutes)

```bash
# Create network if doesn't exist
docker network create sentinel-network 2>/dev/null || true

# Start N8N
docker-compose -f docker-compose.n8n.yml up -d

# Check logs
docker logs -f sentinel-n8n
```

**Access**: http://localhost:5678
- User: `admin`
- Password: `sentinel_n8n_2024`

---

## Step 2: Import Workflows (10 minutes)

### Option A: Manual Import (Recommended for demo)
1. Open N8N: http://localhost:5678
2. Click "Workflows" → "Import from File"
3. Import these files:
   - `n8n/workflows/backup-recovery.json`
   - `n8n/workflows/intrusion-lockdown.json` (create next)
   - `n8n/workflows/health-failsafe.json` (create next)

### Option B: Auto-import (if available)
```bash
# Copy workflows to N8N data directory
docker cp n8n/workflows/. sentinel-n8n:/home/node/.n8n/workflows/
docker restart sentinel-n8n
```

---

## Step 3: Configure Webhooks (15 minutes)

### Get Webhook URLs

For each workflow, click on the "Webhook" node to get the URL:

**Backup Recovery**:
```
http://localhost:5678/webhook/failsafe/backup-recovery
```

**Intrusion Lockdown**:
```
http://localhost:5678/webhook/failsafe/intrusion-lockdown
```

**Health Failsafe**:
```
http://localhost:5678/webhook/failsafe/health-failsafe
```

### Update Backend Config

Add to `.env`:
```bash
N8N_BASE_URL=http://localhost:5678
N8N_WEBHOOK_TOKEN=your_webhook_token_here
```

---

## Step 4: Test Playbooks (30 minutes)

### Test 1: Backup Recovery

```bash
# Trigger backup failure
curl -X POST http://localhost:5678/webhook/failsafe/backup-recovery \
  -H "Content-Type: application/json" \
  -d '{
    "backup_file": "sentinel_backup_2024-12-15.sql",
    "error": "Connection timeout",
    "retry_count": 0
  }'
```

**Expected**: 
- N8N retries backup
- Verifies success
- Sends Slack notification

### Test 2: Intrusion Lockdown

```bash
# Trigger intrusion detection
curl -X POST http://localhost:5678/webhook/failsafe/intrusion-lockdown \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.168.1.100",
    "user": "attacker@evil.com",
    "attack_type": "brute_force",
    "failed_attempts": 50
  }'
```

**Expected**:
- Blocks IP
- Locks user account
- Revokes sessions
- Alerts security team

### Test 3: Health Failsafe

```bash
# Trigger health check failure
curl -X POST http://localhost:5678/webhook/failsafe/health-failsafe \
  -H "Content-Type: application/json" \
  -d '{
    "service": "backend",
    "status": "unhealthy",
    "cpu_usage": 95,
    "memory_usage": 90
  }'
```

**Expected**:
- Restarts service
- Monitors recovery
- Escalates if needed

---

## Step 5: Demo Script (1 hour)

### Setup Demo Environment

```bash
# Terminal 1: N8N logs
docker logs -f sentinel-n8n

# Terminal 2: Backend logs
docker logs -f sentinel-backend

# Terminal 3: Test commands
cd /home/jnovoas/sentinel
```

### Demo Flow (5 minutes)

**1. Show Dashboard** (30 seconds)
- Open http://localhost:3000/dashboard
- Point to "Fail-Safe Security" card
- Show "6 Active Playbooks"

**2. Trigger Backup Failure** (1 minute)
```bash
# Simulate backup failure
curl -X POST http://localhost:5678/webhook/failsafe/backup-recovery \
  -H "Content-Type: application/json" \
  -d '{"backup_file": "demo.sql", "error": "Timeout", "retry_count": 0}'
```

- Show N8N execution in real-time
- Point to retry logic
- Show success notification

**3. Trigger Intrusion** (1 minute)
```bash
# Simulate brute force attack
curl -X POST http://localhost:5678/webhook/failsafe/intrusion-lockdown \
  -H "Content-Type: application/json" \
  -d '{"ip": "1.2.3.4", "attack_type": "brute_force", "failed_attempts": 100}'
```

- Show automatic IP blocking
- Show user lockout
- Show security alert

**4. Show Intelligence** (2 minutes)
- Open N8N workflow editor
- Show visual workflow
- Explain decision logic
- Show execution history

**5. Pitch Points** (30 seconds)
> "This is just Phase 1. Phase 2 adds:
> - Neural Guard (Rust) for pattern detection
> - 9 data sources auto-ingestion
> - Cognitive learning
> - Neural honeypots
> 
> We're building the world's first self-learning security system."

---

## Troubleshooting

### N8N won't start
```bash
# Check logs
docker logs sentinel-n8n

# Restart
docker-compose -f docker-compose.n8n.yml restart

# Reset
docker-compose -f docker-compose.n8n.yml down -v
docker-compose -f docker-compose.n8n.yml up -d
```

### Webhooks not working
```bash
# Check N8N is accessible
curl http://localhost:5678/healthz

# Check webhook URL
# Make sure it matches the workflow configuration
```

### Slack notifications not sending
- Configure Slack credentials in N8N
- Or replace with HTTP Request to your notification service

---

## Next Steps

After demo:
1. ✅ Polish dashboard (4-6 hours)
2. ✅ Add CloudFlare firewall (1 day)
3. ✅ Record demo video (2 hours)
4. ✅ Practice pitch (1 hour)

**Total to investor-ready**: 2-3 days 🚀
