# Sentinel Frontend - Developer Documentation

**Last Updated**: December 15, 2025  
**Version**: 2.0.0  
**Tech Stack**: Next.js 14, React, TypeScript, shadcn/ui, Tailwind CSS

---

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Component Documentation](#component-documentation)
3. [API Integration](#api-integration)
4. [State Management](#state-management)
5. [Styling Guidelines](#styling-guidelines)
6. [Common Patterns](#common-patterns)
7. [Debugging Tips](#debugging-tips)
8. [TODO List](#todo-list)

---

## 🏗️ Project Structure

```
frontend/src/
├── app/                          # Next.js 14 App Router pages
│   ├── dashboard/               # Executive Dashboard (main entry)
│   │   └── page.tsx            # Business-level insights, SLOs
│   ├── ai/playground/          # AI Playground
│   │   └── page.tsx            # Ollama query interface
│   ├── security/watchdog/      # Security Dashboard
│   │   └── page.tsx            # Auditd events, exploit detection
│   ├── metrics/                # Embedded Grafana
│   │   └── page.tsx            # Technical metrics dashboards
│   ├── analytics/              # Legacy analytics (to be deprecated)
│   │   └── page.tsx            # Historical metrics view
│   ├── api/v1/                 # Next.js API routes (proxy to backend)
│   │   └── ai/
│   │       ├── query/route.ts  # AI query proxy
│   │       └── health/route.ts # AI health check proxy
│   └── page.tsx                # Home (redirects to /dashboard)
├── components/ui/              # shadcn/ui components
│   ├── card.tsx               # Card component with variants
│   ├── button.tsx             # Button component
│   └── badge.tsx              # Badge component
└── lib/
    └── utils.ts               # Utility functions (cn for class merging)
```

---

## 📄 Component Documentation

### 1. Executive Dashboard (`/dashboard`)

**Purpose**: Business-level overview for non-technical stakeholders  
**Route**: `/dashboard`  
**File**: `src/app/dashboard/page.tsx`

#### Key Features:
- **System Status Hero**: Dynamic health indicator (Healthy/Warning/Critical)
- **SLO Cards**: 4 key metrics with targets and status
- **AI Insights**: Automatic anomaly analysis
- **Security Alerts**: Last 24h security events
- **Quick Actions**: Navigation to other dashboards
- **Recent Activity**: Timeline of system events

#### Data Flow:
```typescript
// 1. Component mounts → useEffect triggers
useEffect(() => {
  const fetchData = async () => {
    // 2. Fetch from 3 backend endpoints
    const stats = await fetch("/api/v1/analytics/statistics?hours=24");
    const anomalies = await fetch("/api/v1/analytics/anomalies?hours=24&limit=10");
    const aiHealth = await fetch("/api/v1/ai/health");
    
    // 3. Transform data for UI
    setSloData(...);
    setAiInsights(...);
    setSecurityAlerts(...);
  };
  
  fetchData();
  
  // 4. Auto-refresh every 30 seconds
  const interval = setInterval(fetchData, 30000);
  return () => clearInterval(interval);
}, []);
```

#### State Management:
```typescript
// SLO data with current values and targets
const [sloData, setSloData] = useState<SLOData>({
  availability: { value: 99.95, target: 99.9 },
  errorRate: { value: 0.3, target: 1.0 },
  latency: { value: 45, target: 100 },
  aiResponse: { value: 1.2, target: 3.0 },
});

// AI-generated insights from anomalies
const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);

// Security alerts from auditd/anomalies
const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([]);

// Overall system health status
const [systemStatus, setSystemStatus] = useState<"healthy" | "warning" | "critical">("healthy");
```

#### API Endpoints Used:
- `GET /api/v1/analytics/statistics?hours=24` - System metrics aggregates
- `GET /api/v1/analytics/anomalies?hours=24&limit=10` - Detected anomalies
- `GET /api/v1/ai/health` - AI service status

#### Status Determination Logic:
```typescript
// System status based on CPU/Memory thresholds
if (statsData.cpu?.max > 95 || statsData.memory?.max > 95) {
  setSystemStatus("critical");  // Red alert
} else if (statsData.cpu?.max > 90 || statsData.memory?.max > 90) {
  setSystemStatus("warning");   // Yellow warning
} else {
  setSystemStatus("healthy");   // Green, all good
}
```

#### TODO:
- [ ] Connect latency SLO to real API metrics (currently hardcoded to 45ms)
- [ ] Add WebSocket for real-time updates instead of polling
- [ ] Implement SLO history charts
- [ ] Add export to PDF functionality

---

### 2. AI Playground (`/ai/playground`)

**Purpose**: Interactive interface for querying local AI (Ollama)  
**Route**: `/ai/playground`  
**File**: `src/app/ai/playground/page.tsx`

#### Key Features:
- **Query Interface**: Large textarea with Ctrl+Enter shortcut
- **Model Selector**: Choose between phi3:mini, llama3.2:1b
- **Parameter Controls**: Adjust max_tokens (10-500) and temperature (0-1)
- **Example Prompts**: 6 pre-made prompts in Spanish (optimized for speed)
- **Query History**: Persistent in-memory history with timestamps
- **Copy to Clipboard**: Easy sharing of AI responses

#### Data Flow:
```typescript
// 1. User enters prompt and clicks "Generate Response"
const handleQuery = async () => {
  setLoading(true);
  
  // 2. Send to Next.js API proxy (not directly to backend)
  const res = await fetch("/api/v1/ai/query", {
    method: "POST",
    body: JSON.stringify({ prompt, max_tokens, temperature })
  });
  
  // 3. API proxy forwards to backend at http://backend:8000/api/v1/ai/query
  // 4. Backend calls Ollama at http://ollama:11434/api/generate
  // 5. Response flows back through proxy to frontend
  
  const data = await res.json();
  
  if (data.response) {
    setResponse(data.response);
    // 6. Add to history for future reference
    setHistory([{ prompt, response, timestamp, model }, ...history]);
  }
};
```

#### Why Use API Proxy?
```typescript
// ❌ DON'T: Call backend directly from browser
fetch("http://backend:8000/api/v1/ai/query")  // CORS issues, backend not exposed

// ✅ DO: Use Next.js API route as proxy
fetch("/api/v1/ai/query")  // Proxies to backend internally
```

#### Timeout Configuration:
- **Frontend**: No timeout (waits for backend)
- **Backend**: 60 seconds (configured in `backend/app/routers/ai.py`)
- **Ollama**: Depends on model and hardware

#### Performance Expectations:
```
GTX 1050 (3GB VRAM) with phi3:mini:
- Simple prompts (Spanish, <10 words): 2-5s
- Medium prompts (Spanish, 10-20 words): 5-10s
- Complex prompts (English, >20 words): 15-40s

First query of the day: +5-10s (model loading)
```

#### Example Prompts (Optimized):
```typescript
const examplePrompts = [
  "¿Qué es una anomalía de CPU?",              // ~3s response
  "Explica qué es Prometheus en 10 palabras",  // ~2s response
  "¿Cómo optimizar una base de datos?",        // ~5s response
  "¿Qué causa un memory leak?",                // ~4s response
  "Explica qué es latencia",                   // ~2s response
  "¿Cómo funciona Redis?",                     // ~3s response
];
```

#### Error Handling:
```typescript
// Backend errors are passed through with detail
if (data.error) {
  setResponse(`Error: ${data.error}`);  // e.g., "Backend returned 504"
} else if (data.detail) {
  setResponse(`Error: ${data.detail}`);  // e.g., "AI service timeout"
} else {
  setResponse("Error: No response from AI");
}
```

#### TODO:
- [ ] Add streaming responses (currently waits for full response)
- [ ] Implement query persistence to localStorage
- [ ] Add "Stop Generation" button
- [ ] Support for image inputs (multimodal)
- [ ] Add prompt templates library

---

### 3. Security Dashboard (`/security/watchdog`)

**Purpose**: Kernel-level security monitoring (Sentinel's key differentiator)  
**Route**: `/security/watchdog`  
**File**: `src/app/security/watchdog/page.tsx`

#### Key Features:
- **Security Status Hero**: Threat counter and overall security posture
- **Stats Grid**: Events today, exploits blocked, syscalls monitored, compliance %
- **Auditd Events Table**: Real-time kernel syscall events
- **Exploit Detection**: Privilege escalation, suspicious executions, unauthorized access
- **Compliance Checklist**: SOC 2 readiness indicators
- **AI Security Insights**: Automatic threat assessment

#### Monitored Syscalls:
```bash
# Configured in host-metrics/auditd_rules.conf
execve   # Process execution (detect malicious binaries)
open     # File access (detect sensitive file reads)
ptrace   # Debugging/injection (detect code injection)
chmod    # Permission changes (detect privilege escalation)
```

#### Data Flow (Currently Mock):
```typescript
// TODO: Replace with real auditd data
useEffect(() => {
  // CURRENT: Mock data for demonstration
  const mockEvents: AuditEvent[] = [
    {
      id: "1",
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
      type: "execve",
      severity: "low",
      description: "Process execution: /usr/bin/python3",
      user: "www-data",
      process: "python3",
    },
    // ...
  ];
  
  setEvents(mockEvents);
  
  // FUTURE: Fetch from backend
  // const res = await fetch("/api/v1/security/events?hours=24");
  // const data = await res.json();
  // setEvents(data.events);
}, []);
```

#### Hydration Error Fix:
```typescript
// Problem: Server renders time as "3:26:00 AM", client as "12:26:01 a. m."
// Solution: Only render timestamps after component mounts

const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);  // Set to true after client-side mount
}, []);

// In JSX:
{mounted ? event.timestamp.toLocaleTimeString() : "--:--:--"}
```

#### Severity Color Mapping:
```typescript
const getSeverityColor = (severity: "low" | "medium" | "high" | "critical") => {
  switch (severity) {
    case "critical": return "bg-rose-500/20 text-rose-400";    // Red
    case "high":     return "bg-orange-500/20 text-orange-400"; // Orange
    case "medium":   return "bg-amber-500/20 text-amber-400";  // Yellow
    case "low":      return "bg-slate-500/20 text-slate-400";  // Gray
  }
};
```

#### TODO:
- [ ] **CRITICAL**: Connect to real auditd events from backend
- [ ] Add WebSocket for real-time event streaming
- [ ] Implement event filtering (by type, severity, user)
- [ ] Add event search functionality
- [ ] Create event detail modal
- [ ] Add export to CSV
- [ ] Implement event acknowledgment/resolution

---

### 4. Metrics Page (`/metrics`)

**Purpose**: Embedded Grafana dashboards for technical metrics  
**Route**: `/metrics`  
**File**: `src/app/metrics/page.tsx`

#### Key Features:
- **Tab Navigation**: 5 metric categories (Overview, Host, Database, Network, AI)
- **Embedded Grafana**: Iframe with kiosk mode (no Grafana UI)
- **Quick Stats**: Monitoring stack status (Prometheus, Grafana, Loki)
- **Fallback Links**: Direct links if iframe doesn't load

#### Grafana URL Structure:
```typescript
const grafanaUrls: Record<MetricTab, string> = {
  // Format: http://localhost:3001/d/{dashboard-id}/{dashboard-name}?orgId=1&refresh=5s&kiosk
  overview: "http://localhost:3001/d/sentinel-overview/sentinel-overview?orgId=1&refresh=5s&kiosk",
  host: "http://localhost:3001/d/sentinel-host/host-metrics?orgId=1&refresh=5s&kiosk",
  // ...
};
```

#### URL Parameters Explained:
- `orgId=1` - Grafana organization ID (default)
- `refresh=5s` - Auto-refresh every 5 seconds
- `kiosk` - Hide Grafana UI (menu, header, etc.)

#### Iframe Configuration:
```typescript
<iframe
  src={grafanaUrls[activeTab]}
  className="w-full h-[800px]"  // Fixed height for consistent layout
  frameBorder="0"                // No border
  title={`Grafana ${activeTab} dashboard`}  // Accessibility
/>
```

#### TODO:
- [ ] **CRITICAL**: Create Grafana dashboards (sentinel-overview, sentinel-host, etc.)
- [ ] Configure Grafana for iframe embedding (allow_embedding = true)
- [ ] Add authentication handling (currently assumes logged in)
- [ ] Implement dashboard refresh button
- [ ] Add fullscreen mode
- [ ] Create dashboard templates for quick setup

---

## 🔌 API Integration

### Backend Endpoints

All API calls go through Next.js API routes (proxy pattern):

```
Frontend → Next.js API Route → Backend → Database/Services
```

#### Why Use Proxy Pattern?

1. **CORS**: Backend runs in Docker, not accessible from browser
2. **Security**: Hide backend URL from client
3. **Flexibility**: Can add caching, rate limiting, etc.
4. **SSR**: Can make server-side requests

### API Routes Documentation

#### 1. AI Query Proxy (`/api/v1/ai/query/route.ts`)

```typescript
/**
 * Proxies AI queries from frontend to backend
 * 
 * Frontend: POST /api/v1/ai/query
 * Backend:  POST http://backend:8000/api/v1/ai/query
 * Ollama:   POST http://ollama:11434/api/generate
 * 
 * Request Body:
 * {
 *   prompt: string,        // User's question
 *   max_tokens: number,    // 10-500
 *   temperature: number    // 0.0-1.0
 * }
 * 
 * Response:
 * {
 *   response: string,      // AI's answer
 *   model: string,         // e.g., "phi3:mini"
 *   enabled: boolean       // AI service status
 * }
 * 
 * Errors:
 * - 504: Timeout (query took >60s)
 * - 503: Ollama unavailable
 * - 500: Other backend error
 */
```

#### 2. AI Health Proxy (`/api/v1/ai/health/route.ts`)

```typescript
/**
 * Checks AI service health
 * 
 * Frontend: GET /api/v1/ai/health
 * Backend:  GET http://backend:8000/api/v1/ai/health
 * 
 * Response:
 * {
 *   status: "healthy" | "unhealthy",
 *   enabled: boolean,
 *   url: string,              // Ollama URL
 *   model: string,            // Current model
 *   models_available: string[] // All available models
 * }
 */
```

### Direct Backend Endpoints (No Proxy)

These are called directly because they're on the same Docker network:

```typescript
// Analytics Statistics
GET /api/v1/analytics/statistics?hours=24
Response: {
  cpu: { avg: number, max: number, min: number },
  memory: { avg: number, max: number, min: number },
  anomalies_count: number,
  // ...
}

// Anomalies
GET /api/v1/analytics/anomalies?hours=24&limit=10
Response: {
  count: number,
  anomalies: [{
    id: string,
    detected_at: string,
    type: "cpu_spike" | "memory_leak" | ...,
    severity: "low" | "medium" | "high" | "critical",
    title: string,
    description: string,
    is_resolved: boolean
  }]
}
```

---

## 🎨 Styling Guidelines

### Color System

```typescript
// Status Colors
const statusColors = {
  healthy:  "emerald-400",  // Green - all good
  warning:  "amber-400",    // Yellow - attention needed
  critical: "rose-400",     // Red - urgent action required
};

// Feature Colors
const featureColors = {
  ai:       "purple-400",   // AI/Insights
  security: "rose-400",     // Security/Alerts
  metrics:  "cyan-400",     // Metrics/Analytics
  database: "blue-400",     // Database
  network:  "emerald-400",  // Network
};

// Background Gradients
const backgrounds = {
  dashboard: "from-slate-950 via-slate-900 to-slate-950",
  ai:        "from-slate-950 via-slate-900 to-slate-950",
  security:  "from-slate-950 via-slate-900 to-slate-950",
  metrics:   "from-slate-950 via-slate-900 to-slate-950",
};
```

### Component Patterns

```typescript
// Card with backdrop blur (glassmorphism)
<Card className="bg-white/5 backdrop-blur-xl border-white/10">

// Status badge
<Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
  Active
</Badge>

// Hover effect for clickable cards
<Card className="hover:bg-white/10 transition-colors cursor-pointer">
```

### Responsive Design

```typescript
// Grid layouts
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

// Text sizing
<h1 className="text-4xl md:text-5xl">

// Spacing
<div className="px-6 py-10">  // Mobile: 24px padding, Desktop: 40px
```

---

## 🔧 Common Patterns

### 1. Data Fetching with Auto-Refresh

```typescript
useEffect(() => {
  const fetchData = async () => {
    try {
      const res = await fetch("/api/endpoint");
      const data = await res.json();
      setState(data);
    } catch (error) {
      console.error("Error:", error);
    }
  };
  
  fetchData();  // Initial fetch
  
  const interval = setInterval(fetchData, 30000);  // Refresh every 30s
  return () => clearInterval(interval);  // Cleanup on unmount
}, []);
```

### 2. Hydration Error Prevention

```typescript
// For timestamps and other client-specific data
const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);
}, []);

// In JSX:
{mounted ? new Date().toLocaleTimeString() : "--:--:--"}
```

### 3. Status Color Mapping

```typescript
const getStatusColor = (status: Status) => {
  switch (status) {
    case "good":     return "text-emerald-400 bg-emerald-500/10";
    case "warning":  return "text-amber-400 bg-amber-500/10";
    case "critical": return "text-rose-400 bg-rose-500/10";
  }
};
```

### 4. Conditional Rendering

```typescript
// Loading state
{loading && <Spinner />}

// Empty state
{items.length === 0 ? (
  <p>No items found</p>
) : (
  items.map(item => <Item key={item.id} {...item} />)
)}

// Error state
{error && <ErrorMessage error={error} />}
```

---

## 🐛 Debugging Tips

### Common Issues

#### 1. "Module not found" errors

```bash
# Solution: Rebuild Docker image
docker-compose build frontend
docker-compose up -d frontend
```

#### 2. Hydration errors

```
Error: Text content does not match server-rendered HTML
```

Solution: Use `mounted` state pattern (see Common Patterns)

#### 3. API calls failing

```typescript
// Check if backend is running
docker-compose ps backend

// Check backend logs
docker-compose logs backend | tail -50

// Test endpoint directly
curl http://localhost:8000/api/v1/analytics/statistics?hours=24
```

#### 4. Styles not applying

```bash
# Clear Next.js cache
rm -rf frontend/.next
docker-compose restart frontend
```

### Debugging Tools

```typescript
// Add to component for debugging
useEffect(() => {
  console.log("Component mounted");
  console.log("State:", { sloData, aiInsights, securityAlerts });
}, [sloData, aiInsights, securityAlerts]);

// Network debugging
fetch("/api/endpoint")
  .then(res => {
    console.log("Status:", res.status);
    console.log("Headers:", res.headers);
    return res.json();
  })
  .then(data => console.log("Data:", data))
  .catch(err => console.error("Error:", err));
```

---

## 📝 TODO List

### High Priority

- [ ] **Connect Security Dashboard to real auditd events**
  - Create backend endpoint: `GET /api/v1/security/events`
  - Parse `/var/log/audit/audit.log`
  - Stream events via WebSocket

- [ ] **Create Grafana dashboards**
  - sentinel-overview: System health overview
  - sentinel-host: CPU, Memory, Disk, GPU
  - sentinel-db: PostgreSQL metrics
  - sentinel-network: Network traffic
  - sentinel-ai: Ollama performance

- [ ] **Add global navigation menu**
  - Sidebar or top nav
  - Active route highlighting
  - Breadcrumbs

### Medium Priority

- [ ] Add loading skeletons for better UX
- [ ] Implement error boundaries
- [ ] Add dark mode toggle (currently always dark)
- [ ] Create user settings page
- [ ] Add notification system
- [ ] Implement data export (CSV, JSON)

### Low Priority

- [ ] Add unit tests (Jest + React Testing Library)
- [ ] Add E2E tests (Playwright)
- [ ] Optimize bundle size
- [ ] Add PWA support
- [ ] Implement i18n (English/Spanish)

---

## 🤝 Contributing

### Code Style

- Use TypeScript for all new files
- Follow existing naming conventions
- Add comments for complex logic
- Update this documentation when adding features

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

### Commit Message Format

```
feat: add new feature
fix: fix bug
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

---

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

---

**Questions?** Check existing code examples or ask the team in Slack.
