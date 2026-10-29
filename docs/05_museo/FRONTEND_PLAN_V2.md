# 🎯 Sentinel Frontend - Implementation Plan v2.0

**Vision**: Control Tower sobre Grafana con IA y Seguridad como diferenciadores

**Date**: December 14, 2025  
**Status**: Ready to implement

---

## 🎨 Strategic Positioning

### What Sentinel IS
- **Executive Control Tower** - Business-level insights, not just metrics
- **AI-Powered Analysis** - Automatic explanations and recommendations
- **Security Platform** - Auditd watchdog, exploit detection, compliance
- **Incident Manager** - Timeline, runbooks, post-mortems

### What Sentinel is NOT
- ❌ Another Grafana (we embed it for details)
- ❌ Metrics visualization tool (Grafana does this)
- ❌ Log viewer (Loki + Grafana does this)

### Competitive Advantage
```
Grafana/Prometheus = Metrics Engine (commodity)
Sentinel = Business Intelligence + AI + Security (differentiation)
```

---

## 🏗️ Frontend Architecture

### Route Structure
```
app/
├── dashboard/              # Executive Overview (Main Page)
│   └── page.tsx           # SLOs, status, AI insights, security alerts
│
├── ai/                    # AI Playground (Killer Feature #1)
│   ├── playground/        # Query interface
│   ├── insights/          # AI-generated insights
│   └── analyze/           # Anomaly analyzer
│
├── security/              # Security Dashboard (Killer Feature #2)
│   ├── watchdog/          # Auditd events
│   ├── exploits/          # Exploit detection
│   ├── timeline/          # Security timeline
│   └── compliance/        # Compliance reports
│
├── incidents/             # Incident Management
│   ├── active/            # Current incidents
│   ├── history/           # Past incidents
│   └── runbooks/          # Automated runbooks
│
├── metrics/               # Embedded Grafana (Technical Details)
│   ├── host/              # Host metrics
│   ├── services/          # Services metrics
│   └── custom/            # Custom dashboards
│
└── settings/              # Configuration
    ├── profile/
    ├── notifications/
    └── integrations/
```

---

## 📊 Page Designs

### 1. Executive Dashboard (Main Page)

**Purpose**: Non-technical overview for stakeholders

**Components**:
```typescript
// app/dashboard/page.tsx

<Dashboard>
  {/* Hero Section */}
  <SystemStatus>
    🟢 All Systems Operational
    Uptime: 99.95% (Target: 99.9%)
  </SystemStatus>

  {/* SLO Cards */}
  <SLOGrid>
    <SLOCard title="Availability" value="99.95%" target="99.9%" status="good" />
    <SLOCard title="Error Rate" value="0.3%" target="<1%" status="good" />
    <SLOCard title="Latency P95" value="45ms" target="<100ms" status="good" />
    <SLOCard title="AI Response" value="1.2s" target="<3s" status="good" />
  </SLOGrid>

  {/* AI Insights */}
  <AIInsightsCard>
    💡 AI detected 3 optimization opportunities
    - CPU usage trending up 15% this week
    - Memory leak suspected in backend service
    - GPU utilization could be optimized
  </AIInsightsCard>

  {/* Security Alerts */}
  <SecurityAlertsCard>
    🔒 2 security events in last 24h
    - Failed login attempts: 5 (normal)
    - Auditd events: 2 (low severity)
  </SecurityAlertsCard>

  {/* Quick Actions */}
  <QuickActions>
    <Button href="/ai/playground">Ask AI</Button>
    <Button href="/metrics/host">View Metrics</Button>
    <Button href="/security/watchdog">Security Dashboard</Button>
  </QuickActions>

  {/* Recent Activity */}
  <ActivityTimeline>
    - 10:30 AM: AI analyzed CPU spike (resolved)
    - 09:15 AM: Backup completed successfully
    - 08:00 AM: Daily SLO report generated
  </ActivityTimeline>
</Dashboard>
```

**Key Features**:
- ✅ Non-technical language
- ✅ Green/Yellow/Red status indicators
- ✅ AI-generated insights
- ✅ Security summary
- ✅ Quick access to details (Grafana)

---

### 2. AI Playground

**Purpose**: Showcase AI capabilities, analyze anomalies

**Components**:
```typescript
// app/ai/playground/page.tsx

<AIPlayground>
  {/* Query Interface */}
  <QuerySection>
    <Textarea placeholder="Ask about your system..." />
    <ModelSelector models={["phi3:mini", "llama3.2:1b"]} />
    <ParameterControls>
      <Slider label="Max Tokens" value={100} />
      <Slider label="Temperature" value={0.3} />
    </ParameterControls>
    <Button>Generate Response</Button>
  </QuerySection>

  {/* Example Prompts */}
  <ExamplePrompts>
    - "Why is CPU usage high right now?"
    - "Analyze the memory spike at 2 PM"
    - "What caused the latency increase?"
    - "Recommend optimizations for database"
  </ExamplePrompts>

  {/* Response */}
  <ResponseCard>
    <AIResponse>
      Based on metrics, the CPU spike was caused by...
      Recommendation: Consider scaling horizontally...
    </AIResponse>
    <Actions>
      <Button>Copy</Button>
      <Button>Save to Runbook</Button>
      <Button>Create Incident</Button>
    </Actions>
  </ResponseCard>

  {/* Query History */}
  <HistoryTable>
    {queries.map(q => (
      <HistoryRow 
        timestamp={q.timestamp}
        prompt={q.prompt}
        response={q.response}
      />
    ))}
  </HistoryTable>
</AIPlayground>
```

**Key Features**:
- ✅ Clean, focused interface
- ✅ Example prompts for quick start
- ✅ Actions on responses (save, create incident)
- ✅ Query history

---

### 3. Security Dashboard

**Purpose**: Real-time security monitoring with auditd

**Components**:
```typescript
// app/security/watchdog/page.tsx

<SecurityDashboard>
  {/* Security Status */}
  <SecurityStatus>
    🔒 Security Status: SECURE
    Last scan: 2 minutes ago
    Threats detected: 0
  </SecurityStatus>

  {/* Auditd Events */}
  <AuditdEventsTable>
    <EventRow 
      severity="low"
      type="execve"
      description="Process execution: /usr/bin/python3"
      timestamp="10:45:23"
      action="Logged"
    />
    <EventRow 
      severity="medium"
      type="ptrace"
      description="Debug attempt on process 1234"
      timestamp="10:30:15"
      action="Blocked"
    />
  </AuditdEventsTable>

  {/* Exploit Detection */}
  <ExploitTimeline>
    - No exploits detected in last 7 days ✅
    - 15 suspicious events logged (all benign)
    - 0 privilege escalation attempts
  </ExploitTimeline>

  {/* Compliance */}
  <ComplianceCard>
    SOC 2 Compliance: 95%
    - Audit logging: ✅
    - Encryption: ✅
    - Access control: ✅
    - Backup: ⚠️ (needs review)
  </ComplianceCard>

  {/* AI Analysis */}
  <AISecurityInsights>
    💡 AI Analysis:
    "Security posture is strong. No anomalous patterns 
    detected in the last 24 hours. Recommend reviewing 
    backup configuration for SOC 2 compliance."
  </AISecurityInsights>
</SecurityDashboard>
```

**Key Features**:
- ✅ Real-time auditd events
- ✅ Exploit detection timeline
- ✅ Compliance status
- ✅ AI-powered security insights

---

### 4. Metrics (Embedded Grafana)

**Purpose**: Technical deep-dive when needed

**Components**:
```typescript
// app/metrics/host/page.tsx

<MetricsPage>
  <Tabs>
    <TabsList>
      <TabsTrigger value="overview">Overview</TabsTrigger>
      <TabsTrigger value="grafana">Detailed Metrics</TabsTrigger>
    </TabsList>

    <TabsContent value="overview">
      {/* Your custom high-level view */}
      <StatsGrid>
        <StatCard label="CPU" value="45%" />
        <StatCard label="Memory" value="62%" />
        <StatCard label="GPU" value="15%" />
      </StatsGrid>
    </TabsContent>

    <TabsContent value="grafana">
      {/* Embedded Grafana */}
      <EmbeddedDashboard 
        dashboardId="host-metrics"
        height="800px"
      />
    </TabsContent>
  </Tabs>
</MetricsPage>
```

**Key Features**:
- ✅ Simple overview (yours)
- ✅ Detailed metrics (Grafana)
- ✅ Seamless transition
- ✅ No duplication of effort

---

## 🎯 Implementation Phases

### Phase 1: Executive Dashboard (Week 1)
- [ ] Create dashboard route
- [ ] Build SLO cards with shadcn/ui
- [ ] Add system status indicator
- [ ] Integrate AI insights (from `/api/v1/ai/query`)
- [ ] Add security alerts summary
- [ ] Create quick actions section

### Phase 2: AI Playground (Week 2)
- [ ] Create AI playground route
- [ ] Build query interface
- [ ] Add model selector
- [ ] Implement parameter controls
- [ ] Add example prompts
- [ ] Create query history
- [ ] Add actions (save, create incident)

### Phase 3: Security Dashboard (Week 3)
- [ ] Create security routes
- [ ] Build auditd events table
- [ ] Add exploit detection timeline
- [ ] Create compliance card
- [ ] Integrate AI security insights
- [ ] Add filtering and search

### Phase 4: Embedded Grafana (Week 4)
- [ ] Create metrics routes
- [ ] Build EmbeddedDashboard component
- [ ] Add Tabs for overview vs detail
- [ ] Configure Grafana for embedding
- [ ] Test authentication pass-through

### Phase 5: Polish & Deploy (Week 5)
- [ ] Add navigation
- [ ] Implement dark mode
- [ ] Add loading states
- [ ] Error handling
- [ ] Performance optimization
- [ ] Deploy to staging
- [ ] User testing

---

## 🎨 Design System

### Colors (Dark Mode)
```css
Background: slate-950 → slate-900 gradient
Cards: white/5 with backdrop-blur
Borders: white/10

Status Colors:
- Good: emerald-400
- Warning: amber-400
- Critical: rose-400
- Info: cyan-400

AI: purple-400
Security: rose-400
Metrics: cyan-400
```

### Typography
```css
Headings: font-semibold, tracking-tight
Body: text-gray-300
Labels: text-gray-400, text-sm
```

### Components (shadcn/ui)
- Card, CardHeader, CardTitle, CardContent
- Button (variants: default, outline, ghost)
- Tabs, TabsList, TabsTrigger, TabsContent
- Table, TableHeader, TableRow, TableCell
- Badge (for status indicators)
- Dialog (for modals)

---

## 📊 Data Flow

### Dashboard
```
Frontend → /api/v1/analytics/statistics → Backend
        → /api/v1/ai/insights → Ollama
        → /api/v1/security/summary → Auditd
```

### AI Playground
```
Frontend → /api/v1/ai/query → Ollama → phi3:mini
        → /api/v1/ai/analyze-anomaly → AI Analysis
```

### Security Dashboard
```
Frontend → /api/v1/security/events → Auditd logs
        → /api/v1/security/exploits → Pattern matching
        → /api/v1/ai/security-insights → AI Analysis
```

---

## 🚀 Quick Start

### This Week
```bash
# 1. Create dashboard route
mkdir -p src/app/dashboard
# Copy dashboard template

# 2. Add more shadcn components
npx shadcn-ui@latest add tabs badge table dialog

# 3. Build SLO cards
# Use Card component from shadcn/ui

# 4. Test
npm run dev
```

---

## 💡 Key Principles

1. **Don't Compete with Grafana** - Embed it, don't replace it
2. **Focus on Business Value** - SLOs, not just metrics
3. **AI is the Differentiator** - Use it everywhere
4. **Security is Premium** - Auditd watchdog is unique
5. **Keep it Simple** - Non-technical language
6. **Defer Multi-Tenant** - Validate first, scale later

---

## 🎯 Success Metrics

### Week 5 Goals
- [ ] Dashboard loads in <2s
- [ ] AI responds in <3s
- [ ] Security events update real-time
- [ ] 5 users tested and gave feedback
- [ ] Decision made on multi-tenant

---

**Next Step**: Create Executive Dashboard with shadcn/ui

Ready to start?
