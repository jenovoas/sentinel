# 🎨 Frontend Modernization Plan - Sentinel

**Version**: 1.0  
**Date**: December 14, 2025  
**Approach**: Gradual, Low-Risk, User-Validated

---

## 🎯 Strategic Vision

**Integrate the best of both recommendations**:
1. ✅ **Your plan**: shadcn/ui → AI playground → validate → multi-tenant (if needed)
2. ✅ **My analysis**: Phased approach, low-risk changes, preserve what works

**Result**: Modernize frontend WITHOUT breaking existing functionality

---

## 📊 Current State Analysis

### What We Have (Solid Foundation)
```
✅ Next.js 14 with App Router
✅ React 18 + TypeScript
✅ Tailwind CSS (configured)
✅ Chart.js for visualizations
✅ Working analytics dashboard
✅ Responsive design
✅ Dark mode support
```

### What We'll Add
```
🆕 shadcn/ui component library
🆕 AI playground interface
🆕 Embedded Grafana dashboards
🆕 Consistent design system
```

### What We'll Defer
```
⏸️ Multi-tenant routing (validate first)
⏸️ Organization management (if needed)
⏸️ Custom domains (future)
```

---

## 🚀 Implementation Roadmap

### Phase 1: shadcn/ui Foundation (Week 1)

**Goal**: Integrate shadcn/ui without breaking existing pages

#### Step 1.1: Installation (Day 1)
```bash
cd /home/jnovoas/sentinel/frontend

# Initialize shadcn/ui
npx shadcn-ui@latest init

# Select options:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes
# - Tailwind config: Yes
```

#### Step 1.2: Add Core Components (Day 1)
```bash
# Essential components
npx shadcn-ui@latest add card
npx shadcn-ui@latest add button
npx shadcn-ui@latest add table
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add dialog

# AI playground components
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add select
npx shadcn-ui@latest add slider
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add separator
```

#### Step 1.3: Migrate Analytics Page (Days 2-3)

**Before** (custom components):
```typescript
const StatCard = ({ label, value, stats, color }) => (
  <div className="rounded-2xl border border-white/5...">
    {/* custom markup */}
  </div>
);
```

**After** (shadcn/ui):
```typescript
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

const StatCard = ({ label, value, stats }) => (
  <Card className="bg-white/5 backdrop-blur-xl border-white/5">
    <CardHeader>
      <CardTitle className="text-sm text-gray-400">{label}</CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-3xl font-semibold text-cyan-400">{value}</p>
      <div className="mt-3 space-y-1">
        {stats.map((s, i) => (
          <div key={i} className="flex justify-between text-xs">
            <span className="text-gray-400">{s.label}</span>
            <span className="text-gray-300">{s.value}</span>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
);
```

**Benefits**:
- Accessible (keyboard navigation, ARIA labels)
- Consistent styling
- Less custom CSS
- Easier to maintain

#### Step 1.4: Migrate Dashboard Page (Days 4-5)

**Add Tabs for different views**:
```typescript
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function DashboardPage() {
  return (
    <Tabs defaultValue="overview">
      <TabsList>
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="metrics">Metrics</TabsTrigger>
        <TabsTrigger value="logs">Logs</TabsTrigger>
      </TabsList>
      
      <TabsContent value="overview">
        {/* Your custom Sentinel overview */}
      </TabsContent>
      
      <TabsContent value="metrics">
        {/* Embedded Grafana or detailed charts */}
      </TabsContent>
      
      <TabsContent value="logs">
        {/* System logs */}
      </TabsContent>
    </Tabs>
  );
}
```

---

### Phase 2: AI Playground (Week 2)

**Goal**: Create dedicated AI interface to showcase capabilities

#### Step 2.1: Create Route (Day 1)
```bash
mkdir -p /home/jnovoas/sentinel/frontend/src/app/ai
touch /home/jnovoas/sentinel/frontend/src/app/ai/page.tsx
```

#### Step 2.2: Build UI Components (Days 2-4)

**File**: `frontend/src/app/ai/page.tsx`
```typescript
"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function AIPlayground() {
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState("phi3:mini");
  const [maxTokens, setMaxTokens] = useState(100);
  const [temperature, setTemperature] = useState(0.3);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/ai/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          max_tokens: maxTokens,
          temperature,
        }),
      });
      const data = await res.json();
      setResponse(data.response);
      
      // Add to history
      setHistory([
        { prompt, response: data.response, timestamp: new Date() },
        ...history,
      ]);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts = [
    "Explain what is a CPU anomaly in 2 sentences",
    "Analyze this metric spike: CPU at 95% for 10 minutes",
    "What are common causes of memory leaks?",
    "How to optimize database queries?",
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-semibold text-white">AI Playground</h1>
          <p className="text-gray-400 mt-2">
            Interact with Sentinel's local AI (Ollama + phi3:mini)
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left: Input & Controls */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Query Input</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Enter your prompt here..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={6}
                  className="resize-none"
                />

                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Model</label>
                    <Select value={model} onValueChange={setModel}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="phi3:mini">phi3:mini (1.3B)</SelectItem>
                        <SelectItem value="llama3.2:1b">llama3.2:1b</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">
                      Max Tokens: {maxTokens}
                    </label>
                    <Slider
                      value={[maxTokens]}
                      onValueChange={([v]) => setMaxTokens(v)}
                      min={10}
                      max={500}
                      step={10}
                    />
                  </div>

                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">
                      Temperature: {temperature}
                    </label>
                    <Slider
                      value={[temperature * 100]}
                      onValueChange={([v]) => setTemperature(v / 100)}
                      min={0}
                      max={100}
                      step={10}
                    />
                  </div>
                </div>

                <Button
                  onClick={handleQuery}
                  disabled={!prompt || loading}
                  className="w-full"
                >
                  {loading ? "Generating..." : "Generate Response"}
                </Button>
              </CardContent>
            </Card>

            {/* Response */}
            {response && (
              <Card>
                <CardHeader>
                  <CardTitle>AI Response</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap">
                    {response}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right: Examples & History */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Example Prompts</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {examplePrompts.map((example, i) => (
                  <Button
                    key={i}
                    variant="outline"
                    className="w-full justify-start text-left h-auto py-3"
                    onClick={() => setPrompt(example)}
                  >
                    {example}
                  </Button>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Query History</CardTitle>
              </CardHeader>
              <CardContent>
                {history.length === 0 ? (
                  <p className="text-sm text-gray-400">No queries yet</p>
                ) : (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {history.map((item, i) => (
                      <div key={i} className="bg-slate-900/50 rounded-lg p-3">
                        <p className="text-xs text-gray-400 mb-1">
                          {item.timestamp.toLocaleTimeString()}
                        </p>
                        <p className="text-sm font-medium text-cyan-400 mb-2">
                          {item.prompt.slice(0, 50)}...
                        </p>
                        <p className="text-xs text-gray-300">
                          {item.response.slice(0, 100)}...
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}
```

#### Step 2.3: Add to Navigation (Day 5)
```typescript
// Update layout.tsx or navigation component
<nav>
  <Link href="/dashboard">Dashboard</Link>
  <Link href="/analytics">Analytics</Link>
  <Link href="/ai">AI Playground</Link>  {/* NEW */}
  <Link href="/db">Database</Link>
</nav>
```

---

### Phase 3: Grafana Integration (Week 3)

**Goal**: Embed Grafana dashboards for detailed metrics

#### Step 3.1: Create Embedded Component
```typescript
// components/grafana/EmbeddedDashboard.tsx
export function EmbeddedDashboard({ 
  dashboardId, 
  title 
}: { 
  dashboardId: string; 
  title: string;
}) {
  return (
    <div className="w-full h-[600px] rounded-lg overflow-hidden border border-white/10">
      <iframe
        src={`http://localhost:3001/d/${dashboardId}?orgId=1&kiosk&theme=dark`}
        className="w-full h-full border-0"
        title={title}
      />
    </div>
  );
}
```

#### Step 3.2: Integrate in Dashboard
```typescript
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmbeddedDashboard } from "@/components/grafana/EmbeddedDashboard";

export default function DashboardPage() {
  return (
    <Tabs defaultValue="overview">
      <TabsList>
        <TabsTrigger value="overview">Sentinel Overview</TabsTrigger>
        <TabsTrigger value="grafana">Detailed Metrics</TabsTrigger>
      </TabsList>
      
      <TabsContent value="overview">
        {/* Your custom cards and charts */}
      </TabsContent>
      
      <TabsContent value="grafana">
        <EmbeddedDashboard 
          dashboardId="host-metrics" 
          title="Host Metrics Dashboard"
        />
      </TabsContent>
    </Tabs>
  );
}
```

---

### Phase 4: Validation & Feedback (Week 4)

**Goal**: Validate with real users before architectural changes

#### Validation Checklist
- [ ] Deploy to staging environment
- [ ] Invite 5-10 users to test
- [ ] Gather feedback on:
  - AI playground usability
  - shadcn/ui components
  - Dashboard organization
  - Missing features
- [ ] Identify pain points
- [ ] Document feature requests
- [ ] **Decide**: Do we need multi-tenant?

#### Decision Matrix
```
IF users need:
  ✅ Multiple organizations per user → Multi-tenant needed
  ✅ Custom domains per org → Multi-tenant needed
  ✅ Org-level permissions → Multi-tenant needed

IF users are happy with:
  ✅ Single organization → Keep simple
  ✅ Current URL structure → Keep simple
  ✅ Existing features → Keep simple
```

---

## 📋 Quick Start Commands

### Week 1: Setup shadcn/ui
```bash
cd /home/jnovoas/sentinel/frontend
npx shadcn-ui@latest init
npx shadcn-ui@latest add card button table tabs dialog textarea select slider badge separator
```

### Week 2: Create AI Playground
```bash
mkdir -p src/app/ai
# Copy AI playground code
# Add to navigation
```

### Week 3: Embed Grafana
```bash
mkdir -p src/components/grafana
# Create EmbeddedDashboard component
# Update dashboard page with Tabs
```

---

## ✅ Success Criteria

### Phase 1 Complete When:
- [ ] All pages use shadcn/ui components
- [ ] Design is consistent across pages
- [ ] No visual regressions
- [ ] Dark mode works everywhere

### Phase 2 Complete When:
- [ ] AI playground is functional
- [ ] Users can query all AI endpoints
- [ ] Query history works
- [ ] Example prompts are helpful

### Phase 3 Complete When:
- [ ] Grafana dashboards embed correctly
- [ ] Tabs navigation is intuitive
- [ ] No authentication issues

### Phase 4 Complete When:
- [ ] 10+ users have tested
- [ ] Feedback is documented
- [ ] Decision made on multi-tenant
- [ ] Roadmap updated

---

## 🎯 Final Recommendation

**Start This Week**:
1. Install shadcn/ui (30 minutes)
2. Migrate one page (analytics) to shadcn (2-3 hours)
3. Test and validate (1 hour)

**Next Week**:
1. Build AI playground (1 day)
2. Test with internal users (2 days)
3. Iterate based on feedback (2 days)

**Week 3**:
1. Embed Grafana (1 day)
2. Polish all pages (2 days)
3. Prepare for user testing (2 days)

**Week 4**:
1. User testing (3 days)
2. Gather feedback (1 day)
3. Decide on multi-tenant (1 day)

---

**Total Time**: 4 weeks to validated, production-ready frontend  
**Risk Level**: Low (all changes are additive)  
**ROI**: High (better UX, faster development, user validation)

¿Empezamos con shadcn/ui esta semana?
