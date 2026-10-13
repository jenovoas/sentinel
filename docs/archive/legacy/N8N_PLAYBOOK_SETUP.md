# 🛡️ N8N Fail-Safe Playbook Setup Guide

## Quick Start

This guide shows you how to set up the 3 core fail-safe playbooks in N8N.

---

## Prerequisites

1. **N8N running**: `http://localhost:5678`
2. **Webhook token**: Set in environment variable `N8N_WEBHOOK_TOKEN`
3. **Sentinel backend**: Running and accessible from N8N

---

## Playbook 1: Backup Recovery

### Workflow Overview

```
Webhook → Wait for ACK → Retry Backup → Verify → Notify → Create Ticket
```

### N8N Workflow JSON

Create a new workflow in N8N and import this:

```json
{
  "name": "Fail-Safe: Backup Recovery",
  "nodes": [
    {
      "parameters": {
        "path": "failsafe/backup-recovery",
        "options": {}
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "amount": 15,
        "unit": "minutes"
      },
      "name": "Wait 15min",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "url": "http://backend:8000/api/v1/backup/trigger",
        "method": "POST",
        "options": {}
      },
      "name": "Retry Backup",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "url": "http://backend:8000/api/v1/backup/status",
        "options": {}
      },
      "name": "Verify Backup",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [850, 300]
    },
    {
      "parameters": {
        "channel": "#alerts",
        "text": "🛡️ Fail-Safe: Backup recovery executed\n\nStatus: {{ $json.status }}\nTime: {{ $now }}\nContext: {{ $node['Webhook'].json.context }}",
        "otherOptions": {}
      },
      "name": "Notify Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 1,
      "position": [1050, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Wait 15min", "type": "main", "index": 0}]]
    },
    "Wait 15min": {
      "main": [[{"node": "Retry Backup", "type": "main", "index": 0}]]
    },
    "Retry Backup": {
      "main": [[{"node": "Verify Backup", "type": "main", "index": 0}]]
    },
    "Verify Backup": {
      "main": [[{"node": "Notify Slack", "type": "main", "index": 0}]]
    }
  }
}
```

### Test the Playbook

```bash
# Trigger from Sentinel
curl -X POST http://localhost:8000/api/v1/failsafe/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "playbook": "backup_recovery",
    "severity": "high",
    "context": {
      "backup_file": "sentinel_backup_20250115.sql.gz",
      "error": "Connection timeout"
    },
    "triggered_by": "backup_failed",
    "wait_time_minutes": 15
  }'
```

---

## Playbook 2: Intrusion Lockdown

### Workflow Overview

```
Webhook → Wait for Response → Block IP → Lock User → Revoke Sessions → Notify
```

### Key Actions

1. **Block IP** at firewall (iptables or CloudFlare API)
2. **Lock user account** in database
3. **Revoke active sessions** (Redis)
4. **Create security incident** (Jira/Linear)
5. **Notify security team** (Slack + Email + SMS)

### N8N Workflow (Simplified)

```json
{
  "name": "Fail-Safe: Intrusion Lockdown",
  "nodes": [
    {
      "parameters": {
        "path": "failsafe/intrusion-lockdown"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "amount": 10,
        "unit": "minutes"
      },
      "name": "Wait 10min",
      "type": "n8n-nodes-base.wait",
      "position": [450, 300]
    },
    {
      "parameters": {
        "command": "iptables -A INPUT -s {{ $json.context.ip_address }} -j DROP"
      },
      "name": "Block IP",
      "type": "n8n-nodes-base.executeCommand",
      "position": [650, 300]
    },
    {
      "parameters": {
        "url": "http://backend:8000/api/v1/users/{{ $json.context.user_id }}/lock",
        "method": "POST"
      },
      "name": "Lock User",
      "type": "n8n-nodes-base.httpRequest",
      "position": [850, 300]
    },
    {
      "parameters": {
        "channel": "#security",
        "text": "🚨 SECURITY ALERT: Intrusion Lockdown Executed\n\nIP Blocked: {{ $json.context.ip_address }}\nUser Locked: {{ $json.context.user_id }}\nReason: {{ $json.context.reason }}\nTime: {{ $now }}"
      },
      "name": "Notify Security",
      "type": "n8n-nodes-base.slack",
      "position": [1050, 300]
    }
  ]
}
```

### Test the Playbook

```bash
curl -X POST http://localhost:8000/api/v1/failsafe/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "playbook": "intrusion_lockdown",
    "severity": "critical",
    "context": {
      "ip_address": "192.168.1.100",
      "user_id": "user_123",
      "reason": "10+ failed login attempts",
      "failed_attempts": 15
    },
    "triggered_by": "security_alert",
    "wait_time_minutes": 10
  }'
```

---

## Playbook 3: Health Failsafe

### Workflow Overview

```
Webhook → Verify Failure → Restart Service → Monitor → Success? → Notify/Escalate
```

### Key Actions

1. **Verify failure** (secondary health check)
2. **Restart service** (Docker/systemd)
3. **Monitor recovery** (30s intervals, 5 attempts)
4. **Switch to standby** (if HA enabled)
5. **Escalate** (if recovery fails)

### N8N Workflow (Simplified)

```json
{
  "name": "Fail-Safe: Health Failsafe",
  "nodes": [
    {
      "parameters": {
        "path": "failsafe/health-failsafe"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "amount": 5,
        "unit": "minutes"
      },
      "name": "Wait 5min",
      "type": "n8n-nodes-base.wait",
      "position": [450, 300]
    },
    {
      "parameters": {
        "command": "docker restart {{ $json.context.service_name }}"
      },
      "name": "Restart Service",
      "type": "n8n-nodes-base.executeCommand",
      "position": [650, 300]
    },
    {
      "parameters": {
        "amount": 30,
        "unit": "seconds"
      },
      "name": "Wait for Startup",
      "type": "n8n-nodes-base.wait",
      "position": [850, 300]
    },
    {
      "parameters": {
        "url": "http://backend:8000/health"
      },
      "name": "Check Health",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1050, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.status }}",
              "value2": "healthy"
            }
          ]
        }
      },
      "name": "Is Healthy?",
      "type": "n8n-nodes-base.if",
      "position": [1250, 300]
    },
    {
      "parameters": {
        "channel": "#ops",
        "text": "✅ Service recovered: {{ $json.context.service_name }}"
      },
      "name": "Notify Success",
      "type": "n8n-nodes-base.slack",
      "position": [1450, 250]
    },
    {
      "parameters": {
        "channel": "#ops",
        "text": "❌ ESCALATION: Service failed to recover\n\nService: {{ $json.context.service_name }}\nAttempts: 3\nStatus: Still down\n\n@oncall please investigate immediately"
      },
      "name": "Escalate",
      "type": "n8n-nodes-base.slack",
      "position": [1450, 350]
    }
  ]
}
```

---

## Environment Variables

Add to your `.env` file:

```bash
# N8N Configuration
N8N_BASE_URL=http://n8n:5678
N8N_WEBHOOK_TOKEN=your-secure-token-here

# Notification Channels
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_API_KEY=your-pagerduty-key
```

---

## Security Best Practices

### 1. Webhook Authentication

Always use bearer tokens:

```javascript
// In N8N webhook node
if (headers.authorization !== 'Bearer YOUR_TOKEN') {
  return { error: 'Unauthorized' };
}
```

### 2. Rate Limiting

Prevent playbook spam:

```javascript
// Check last execution time
const lastRun = await getLastExecutionTime(playbook);
if (Date.now() - lastRun < 300000) { // 5 minutes
  return { error: 'Rate limited' };
}
```

### 3. Audit Logging

Log every execution:

```javascript
await logExecution({
  playbook: 'backup_recovery',
  triggered_by: 'sentinel',
  context: webhookData,
  timestamp: new Date(),
  outcome: 'success'
});
```

---

## Monitoring Playbook Executions

### View in Dashboard

Go to: `http://localhost:3000/dashboard`

The **Fail-Safe Security** card shows:
- Active playbooks
- Success rate
- Last auto-remediation
- Recent executions

### API Endpoints

```bash
# Get status
curl http://localhost:8000/api/v1/failsafe/status

# List playbooks
curl http://localhost:8000/api/v1/failsafe/playbooks

# Health check
curl http://localhost:8000/api/v1/failsafe/health
```

---

## Troubleshooting

### Playbook Not Triggering

1. Check N8N is running: `docker ps | grep n8n`
2. Verify webhook URL: `echo $N8N_BASE_URL`
3. Check logs: `docker logs n8n`
4. Test webhook manually:
   ```bash
   curl -X POST http://localhost:5678/webhook/failsafe/backup-recovery \
     -H "Authorization: Bearer $N8N_WEBHOOK_TOKEN" \
     -d '{"test": true}'
   ```

### Playbook Failing

1. Check N8N execution logs (UI)
2. Verify service connectivity
3. Check permissions (Docker, iptables, etc.)
4. Review error messages in Slack

---

## Next Steps

1. ✅ Set up 3 core playbooks
2. ⏳ Test each playbook manually
3. ⏳ Configure notification channels
4. ⏳ Set up monitoring alerts
5. ⏳ Create remaining 3 playbooks
6. ⏳ Document custom playbooks

---

## Support

- **N8N Docs**: https://docs.n8n.io
- **Sentinel Docs**: `/docs/FAILSAFE_SECURITY_LAYER.md`
- **Issues**: Create ticket in Jira/Linear

**You're now protected by the Fail-Safe Security Layer!** 🛡️
