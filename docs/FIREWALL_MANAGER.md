# 🛡️ Sentinel Firewall Manager - Neural Orchestration Layer

## Overview

**Concept**: Neural Guard orchestrates existing firewalls (CloudFlare, iptables, Fail2ban) instead of building from scratch.

**Key Principle**: "Decide policies, don't filter packets"

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Neural Guard (Rust)                            │
│  - Analyzes threats                             │
│  - Decides severity                             │
│  - Orchestrates firewalls                       │
└─────────────────┬───────────────────────────────┘
                  │
                  │ FirewallManager API
                  │
        ┌─────────┼─────────┬─────────┐
        ▼         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │CloudFl.│ │iptables│ │Fail2ban│ │  N8N   │
    │  (L7)  │ │  (L3)  │ │ (Auto) │ │(Custom)│
    └────────┘ └────────┘ └────────┘ └────────┘
```

---

## Firewall Manager API

```rust
// src/firewall/manager.rs

use async_trait::async_trait;

#[async_trait]
pub trait FirewallProvider {
    async fn block_ip(&self, ip: &str) -> Result<()>;
    async fn unblock_ip(&self, ip: &str) -> Result<()>;
    async fn create_rate_limit(&self, rule: RateLimitRule) -> Result<()>;
    async fn remove_rate_limit(&self, rule_id: &str) -> Result<()>;
    async fn block_asn(&self, asn: u32) -> Result<()>;
    async fn get_blocked_ips(&self) -> Result<Vec<String>>;
}

pub struct FirewallManager {
    cloudflare: Option<CloudFlareProvider>,
    iptables: IptablesProvider,
    fail2ban: Fail2banProvider,
    n8n_client: N8NClient,
}

impl FirewallManager {
    /// Orchestrate firewall response based on threat severity
    pub async fn respond_to_threat(&self, threat: &Threat) -> Result<Response> {
        match threat.severity {
            Severity::Critical => {
                // Block at ALL layers
                self.block_everywhere(&threat).await?;
                
                // Trigger N8N playbook for incident response
                self.n8n_client.trigger("critical_threat_response", json!({
                    "ip": threat.ip,
                    "reason": threat.reason,
                    "evidence": threat.evidence,
                })).await?;
                
                Ok(Response::Blocked {
                    layers: vec!["cloudflare", "iptables", "fail2ban"],
                    duration: Duration::from_secs(86400), // 24 hours
                })
            }
            
            Severity::High => {
                // Block at host level
                self.iptables.block_ip(&threat.ip).await?;
                self.fail2ban.add_to_jail(&threat.ip).await?;
                
                // Notify security team
                self.n8n_client.trigger("security_alert", json!({
                    "ip": threat.ip,
                    "severity": "high",
                })).await?;
                
                Ok(Response::Blocked {
                    layers: vec!["iptables", "fail2ban"],
                    duration: Duration::from_secs(3600), // 1 hour
                })
            }
            
            Severity::Medium => {
                // Rate limit only
                if let Some(cf) = &self.cloudflare {
                    cf.create_rate_limit(RateLimitRule {
                        ip: threat.ip.clone(),
                        requests_per_minute: 100,
                        action: RateLimitAction::Challenge,
                    }).await?;
                }
                
                Ok(Response::RateLimited {
                    threshold: 100,
                    duration: Duration::from_secs(600), // 10 minutes
                })
            }
            
            Severity::Low => {
                // Monitor only, no action
                Ok(Response::Monitored)
            }
        }
    }
    
    /// Block IP at all firewall layers
    async fn block_everywhere(&self, threat: &Threat) -> Result<()> {
        // Edge (CloudFlare)
        if let Some(cf) = &self.cloudflare {
            cf.block_ip(&threat.ip).await?;
        }
        
        // Host (iptables)
        self.iptables.block_ip(&threat.ip).await?;
        
        // Auto-ban (Fail2ban)
        self.fail2ban.add_to_jail(&threat.ip).await?;
        
        // Log to database
        self.log_block_action(threat).await?;
        
        Ok(())
    }
    
    /// Auto-unblock after duration
    pub async fn schedule_unblock(&self, ip: String, after: Duration) -> Result<()> {
        tokio::spawn(async move {
            tokio::time::sleep(after).await;
            
            // Unblock at all layers
            if let Some(cf) = &self.cloudflare {
                let _ = cf.unblock_ip(&ip).await;
            }
            let _ = self.iptables.unblock_ip(&ip).await;
            let _ = self.fail2ban.remove_from_jail(&ip).await;
            
            tracing::info!("Auto-unblocked IP: {}", ip);
        });
        
        Ok(())
    }
}
```

---

## CloudFlare Provider

```rust
// src/firewall/cloudflare.rs

pub struct CloudFlareProvider {
    api_token: String,
    zone_id: String,
    client: reqwest::Client,
}

#[async_trait]
impl FirewallProvider for CloudFlareProvider {
    async fn block_ip(&self, ip: &str) -> Result<()> {
        let rule = json!({
            "mode": "block",
            "configuration": {
                "target": "ip",
                "value": ip
            },
            "notes": format!("Blocked by Sentinel at {}", Utc::now())
        });
        
        let response = self.client
            .post(&format!(
                "https://api.cloudflare.com/client/v4/zones/{}/firewall/access_rules/rules",
                self.zone_id
            ))
            .bearer_auth(&self.api_token)
            .json(&rule)
            .send()
            .await?;
        
        if !response.status().is_success() {
            return Err(anyhow!("CloudFlare API error: {}", response.status()));
        }
        
        tracing::info!("CloudFlare: Blocked IP {}", ip);
        Ok(())
    }
    
    async fn create_rate_limit(&self, rule: RateLimitRule) -> Result<()> {
        let cf_rule = json!({
            "match": {
                "request": {
                    "url": "*"
                }
            },
            "threshold": rule.requests_per_minute,
            "period": 60,
            "action": {
                "mode": match rule.action {
                    RateLimitAction::Block => "block",
                    RateLimitAction::Challenge => "challenge",
                    RateLimitAction::JsChallenge => "js_challenge",
                }
            }
        });
        
        self.client
            .post(&format!(
                "https://api.cloudflare.com/client/v4/zones/{}/rate_limits",
                self.zone_id
            ))
            .bearer_auth(&self.api_token)
            .json(&cf_rule)
            .send()
            .await?;
        
        Ok(())
    }
    
    async fn block_asn(&self, asn: u32) -> Result<()> {
        let rule = json!({
            "mode": "block",
            "configuration": {
                "target": "asn",
                "value": asn.to_string()
            }
        });
        
        self.client
            .post(&format!(
                "https://api.cloudflare.com/client/v4/zones/{}/firewall/access_rules/rules",
                self.zone_id
            ))
            .bearer_auth(&self.api_token)
            .json(&rule)
            .send()
            .await?;
        
        tracing::info!("CloudFlare: Blocked ASN {}", asn);
        Ok(())
    }
}
```

---

## iptables Provider

```rust
// src/firewall/iptables.rs

pub struct IptablesProvider {
    chain: String,
}

#[async_trait]
impl FirewallProvider for IptablesProvider {
    async fn block_ip(&self, ip: &str) -> Result<()> {
        // Add to INPUT chain
        Command::new("iptables")
            .args(&[
                "-A", &self.chain,
                "-s", ip,
                "-j", "DROP"
            ])
            .output()
            .await?;
        
        // Persist rules
        Command::new("iptables-save")
            .arg("/etc/iptables/rules.v4")
            .output()
            .await?;
        
        tracing::info!("iptables: Blocked IP {}", ip);
        Ok(())
    }
    
    async fn unblock_ip(&self, ip: &str) -> Result<()> {
        Command::new("iptables")
            .args(&[
                "-D", &self.chain,
                "-s", ip,
                "-j", "DROP"
            ])
            .output()
            .await?;
        
        Command::new("iptables-save")
            .arg("/etc/iptables/rules.v4")
            .output()
            .await?;
        
        tracing::info!("iptables: Unblocked IP {}", ip);
        Ok(())
    }
    
    async fn get_blocked_ips(&self) -> Result<Vec<String>> {
        let output = Command::new("iptables")
            .args(&["-L", &self.chain, "-n"])
            .output()
            .await?;
        
        let stdout = String::from_utf8(output.stdout)?;
        let ips: Vec<String> = stdout
            .lines()
            .filter_map(|line| {
                if line.contains("DROP") {
                    line.split_whitespace().nth(3).map(String::from)
                } else {
                    None
                }
            })
            .collect();
        
        Ok(ips)
    }
}
```

---

## Fail2ban Provider

```rust
// src/firewall/fail2ban.rs

pub struct Fail2banProvider {
    jail_name: String,
}

impl Fail2banProvider {
    pub async fn add_to_jail(&self, ip: &str) -> Result<()> {
        Command::new("fail2ban-client")
            .args(&["set", &self.jail_name, "banip", ip])
            .output()
            .await?;
        
        tracing::info!("Fail2ban: Banned IP {} in jail {}", ip, self.jail_name);
        Ok(())
    }
    
    pub async fn remove_from_jail(&self, ip: &str) -> Result<()> {
        Command::new("fail2ban-client")
            .args(&["set", &self.jail_name, "unbanip", ip])
            .output()
            .await?;
        
        Ok(())
    }
    
    pub async fn get_banned_ips(&self) -> Result<Vec<String>> {
        let output = Command::new("fail2ban-client")
            .args(&["status", &self.jail_name])
            .output()
            .await?;
        
        let stdout = String::from_utf8(output.stdout)?;
        
        // Parse banned IPs from output
        let ips: Vec<String> = stdout
            .lines()
            .find(|line| line.contains("Banned IP list"))
            .and_then(|line| line.split(':').nth(1))
            .map(|ips_str| {
                ips_str
                    .split_whitespace()
                    .map(String::from)
                    .collect()
            })
            .unwrap_or_default();
        
        Ok(ips)
    }
}
```

---

## Integration with Neural Guard

```rust
// src/intelligence/threat_responder.rs

pub struct ThreatResponder {
    firewall: FirewallManager,
    honeypots: HoneypotOrchestrator,
}

impl ThreatResponder {
    /// Respond to detected threat
    pub async fn respond(&self, threat: DetectedThreat) -> Result<()> {
        // 1. Immediate firewall action
        let response = self.firewall.respond_to_threat(&threat).await?;
        
        // 2. Deploy honeypot if needed
        if threat.confidence > 0.8 {
            self.honeypots.deploy_targeted(&threat).await?;
        }
        
        // 3. Log response
        self.log_response(&threat, &response).await?;
        
        // 4. Learn from outcome
        self.learn_from_response(&threat, &response).await?;
        
        Ok(())
    }
}
```

---

## Configuration

```toml
# config/firewall.toml

[cloudflare]
enabled = true
api_token = "${CLOUDFLARE_API_TOKEN}"
zone_id = "${CLOUDFLARE_ZONE_ID}"

[iptables]
enabled = true
chain = "SENTINEL_INPUT"
persist_rules = true

[fail2ban]
enabled = true
jail_name = "sentinel"
ban_time = 3600  # 1 hour
max_retry = 5

[policies]
# Auto-unblock after duration
auto_unblock = true
critical_duration = 86400  # 24 hours
high_duration = 3600       # 1 hour
medium_duration = 600      # 10 minutes

# Whitelist (never block)
whitelist = [
    "127.0.0.1",
    "10.0.0.0/8",
]
```

---

## Costs

| Provider | Tier | Cost/Month |
|----------|------|------------|
| CloudFlare | Free | $0 |
| CloudFlare | Pro | $20 |
| iptables | - | $0 |
| Fail2ban | - | $0 |
| **Total** | | **$0-20** |

---

## Benefits

1. **Reuses proven components** (CloudFlare, iptables, Fail2ban)
2. **Minimal engineering effort** (orchestration vs. building)
3. **Low cost** ($0-20/month)
4. **High impact** (DDoS protection, WAF, auto-banning)
5. **Neural integration** (dynamic policies, not static rules)

---

## Roadmap

**Week 2.5: Firewall Integration** (3 days)

**Day 14**: CloudFlare Integration
- [ ] API client
- [ ] Block IP endpoint
- [ ] Rate limiting
- [ ] Testing

**Day 15**: iptables Integration
- [ ] Rust wrapper
- [ ] Block/unblock IP
- [ ] Persist rules
- [ ] Testing

**Day 16**: Fail2ban + Integration
- [ ] Fail2ban client
- [ ] FirewallManager
- [ ] Neural Guard integration
- [ ] End-to-end testing

---

## Summary

**Firewall Manager = Neural orchestration layer**

- ✅ Decides policies (Neural Guard)
- ✅ Doesn't filter packets (existing firewalls)
- ✅ Low cost ($0-20/month)
- ✅ High value (complete protection)
- ✅ Cognitive integration (learns & adapts)

**This completes the security stack.** 🛡️
