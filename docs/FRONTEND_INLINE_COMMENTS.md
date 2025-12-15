/**
 * SENTINEL FRONTEND - INLINE CODE COMMENTS GUIDE
 * 
 * This file contains detailed inline comments for all major components.
 * Copy these comments into the actual component files as needed.
 * 
 * Last Updated: December 15, 2025
 */

// ============================================================================
// 1. EXECUTIVE DASHBOARD (/dashboard/page.tsx)
// ============================================================================

/**
 * Executive Dashboard - Business-Level System Overview
 * 
 * PURPOSE:
 * - Provides non-technical stakeholders with high-level system health
 * - Shows SLOs (Service Level Objectives) with targets
 * - Displays AI-generated insights from anomaly detection
 * - Presents security alerts from auditd/anomalies
 * 
 * DATA SOURCES:
 * - /api/v1/analytics/statistics - CPU, memory, anomaly counts
 * - /api/v1/analytics/anomalies - Detected system anomalies
 * - /api/v1/ai/health - AI service status
 * 
 * AUTO-REFRESH: Every 30 seconds
 * 
 * NAVIGATION:
 * - Quick Actions → /ai/playground, /metrics, /security/watchdog, /analytics
 */

// State interfaces for type safety
interface SLOData {
  availability: { value: number; target: number };  // System uptime %
  errorRate: { value: number; target: number };     // Failed requests %
  latency: { value: number; target: number };       // P95 response time (ms)
  aiResponse: { value: number; target: number };    // AI inference time (s)
}

interface AIInsight {
  type: "optimization" | "warning" | "info";  // Insight category
  message: string;                             // Human-readable insight
}

interface SecurityAlert {
  severity: "low" | "medium" | "high";  // Alert severity level
  message: string;                       // Alert description
  count: number;                         // Number of occurrences
}

// Main data fetching logic
useEffect(() => {
  const fetchData = async () => {
    try {
      // 1. Fetch system statistics (CPU, memory, anomaly counts)
      const statsRes = await fetch("/api/v1/analytics/statistics?hours=24");
      const statsData = await statsRes.json();
      
      // 2. Update SLO data based on real metrics
      if (statsData) {
        setSloData({
          // Availability: 99.95% if CPU < 90%, else 99.5%
          availability: {
            value: statsData.cpu?.avg < 90 ? 99.95 : 99.5,
            target: 99.9
          },
          // Error rate: 1.5% if >10 anomalies, else 0.3%
          errorRate: {
            value: statsData.anomalies_count > 10 ? 1.5 : 0.3,
            target: 1.0
          },
          // TODO: Get latency from actual API metrics
          latency: {
            value: 45,  // Hardcoded for now
            target: 100
          },
          // TODO: Get AI response time from AI health
          aiResponse: {
            value: 1.2,  // Hardcoded for now
            target: 3.0
          },
        });
        
        // 3. Determine overall system status based on thresholds
        if (statsData.cpu?.max > 95 || statsData.memory?.max > 95) {
          setSystemStatus("critical");  // Red alert - immediate action needed
        } else if (statsData.cpu?.max > 90 || statsData.memory?.max > 90) {
          setSystemStatus("warning");   // Yellow warning - attention needed
        } else {
          setSystemStatus("healthy");   // Green - all systems operational
        }
      }
      
      // 4. Fetch anomalies and convert to insights
      const anomaliesRes = await fetch("/api/v1/analytics/anomalies?hours=24&limit=10");
      const anomaliesData = await anomaliesRes.json();
      
      if (anomaliesData?.anomalies) {
        // Convert unresolved anomalies to AI insights (max 3)
        const insights: AIInsight[] = anomaliesData.anomalies
          .filter((a: any) => !a.is_resolved)  // Only show active issues
          .slice(0, 3)                          // Limit to 3 for UI space
          .map((a: any) => ({
            type: a.severity === "critical" ? "warning" : "optimization",
            message: a.title || a.description,
          }));
        
        if (insights.length > 0) {
          setAiInsights(insights);
        }
        
        // Convert anomalies to security alerts (max 5)
        const alerts: SecurityAlert[] = anomaliesData.anomalies
          .filter((a: any) => !a.is_resolved)
          .slice(0, 5)
          .map((a: any) => ({
            severity: a.severity === "critical" ? "high" : 
                     a.severity === "warning" ? "medium" : "low",
            message: a.title,
            count: 1,
          }));
        
        if (alerts.length > 0) {
          setSecurityAlerts(alerts);
        }
      }
      
      // 5. Fetch AI service health
      const aiHealthRes = await fetch("/api/v1/ai/health");
      const aiHealthData = await aiHealthRes.json();
      
      if (aiHealthData) {
        setSloData(prev => ({
          ...prev,
          aiResponse: {
            value: aiHealthData.enabled ? 1.2 : 0,  // 0 if AI disabled
            target: 3.0,
          },
        }));
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      // TODO: Show error toast to user
    }
  };
  
  fetchData();  // Initial fetch on mount
  
  // Auto-refresh every 30 seconds
  const interval = setInterval(fetchData, 30000);
  
  // Cleanup: Clear interval when component unmounts
  return () => clearInterval(interval);
}, []);  // Empty deps = run once on mount

// Helper: Determine SLO status based on value vs target
const getSLOStatus = (value: number, target: number, inverse = false) => {
  // inverse=true for metrics where lower is better (error rate, latency)
  const ratio = inverse ? target / value : value / target;
  
  if (ratio >= 1.0) return "good";      // Meeting or exceeding target
  if (ratio >= 0.9) return "warning";   // Within 10% of target
  return "critical";                     // Below 90% of target
};

// ============================================================================
// 2. AI PLAYGROUND (/ai/playground/page.tsx)
// ============================================================================

/**
 * AI Playground - Interactive Ollama Query Interface
 * 
 * PURPOSE:
 * - Allows users to query local AI (Ollama) for insights
 * - Provides parameter controls for fine-tuning responses
 * - Maintains query history for reference
 * 
 * DATA FLOW:
 * Frontend → Next.js API Proxy → Backend → Ollama → Response
 * 
 * PERFORMANCE:
 * - GTX 1050 (3GB): 2-40s depending on prompt complexity
 * - First query: +5-10s (model loading)
 * - Spanish prompts: Faster than English
 * 
 * TIMEOUT: 60 seconds (configured in backend)
 */

// Main query handler
const handleQuery = async () => {
  if (!prompt.trim()) return;  // Don't send empty prompts
  
  setLoading(true);  // Show loading spinner
  setResponse("");   // Clear previous response
  
  try {
    // Send query to Next.js API proxy (NOT directly to backend)
    // Why? Backend runs in Docker, not accessible from browser
    const res = await fetch("/api/v1/ai/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,           // User's question
        max_tokens,       // Max response length (10-500)
        temperature,      // Creativity level (0-1)
      }),
    });
    
    const data = await res.json();
    
    // Handle successful response
    if (data.response) {
      setResponse(data.response);
      
      // Add to history for future reference
      setHistory([
        {
          prompt,
          response: data.response,
          timestamp: new Date(),
          model: data.model || model,
        },
        ...history,  // Prepend to show newest first
      ]);
    } 
    // Handle backend errors (timeout, unavailable, etc.)
    else if (data.error) {
      setResponse(`Error: ${data.error}`);
    } else if (data.detail) {
      setResponse(`Error: ${data.detail}`);
    } else {
      setResponse("Error: No response from AI");
    }
  } catch (error) {
    console.error("AI query error:", error);
    setResponse("Error: Failed to connect to AI service. Please try again.");
  } finally {
    setLoading(false);  // Hide loading spinner
  }
};

// Keyboard shortcut: Ctrl+Enter to submit
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.ctrlKey && e.key === "Enter") {
    handleQuery();
  }
};

// Example prompts (optimized for speed)
const examplePrompts = [
  "¿Qué es una anomalía de CPU?",              // ~3s
  "Explica qué es Prometheus en 10 palabras",  // ~2s
  "¿Cómo optimizar una base de datos?",        // ~5s
  "¿Qué causa un memory leak?",                // ~4s
  "Explica qué es latencia",                   // ~2s
  "¿Cómo funciona Redis?",                     // ~3s
];

// ============================================================================
// 3. SECURITY DASHBOARD (/security/watchdog/page.tsx)
// ============================================================================

/**
 * Security Dashboard - Kernel-Level Security Monitoring
 * 
 * PURPOSE:
 * - Displays auditd events (kernel syscall monitoring)
 * - Shows exploit detection (privilege escalation, code injection)
 * - Provides compliance checklist (SOC 2 readiness)
 * 
 * KEY DIFFERENTIATOR:
 * - Most tools only monitor application layer
 * - Sentinel monitors at kernel level (execve, open, ptrace, chmod)
 * - Catches exploits before they reach application
 * 
 * DATA SOURCE (TODO):
 * - Currently: Mock data
 * - Future: GET /api/v1/security/events (from auditd logs)
 * 
 * REAL-TIME:
 * - TODO: WebSocket for live event streaming
 */

// Hydration error fix: Only render timestamps after client mount
const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);  // Set to true after component mounts on client
}, []);

// In JSX: Conditional rendering based on mounted state
{mounted ? event.timestamp.toLocaleTimeString() : "--:--:--"}

// Why? Server renders time as "3:26:00 AM", client as "12:26:01 a. m."
// This causes hydration mismatch. Solution: Don't render time on server.

// Severity color mapping for visual hierarchy
const getSeverityColor = (severity: "low" | "medium" | "high" | "critical") => {
  switch (severity) {
    case "critical":
      return "bg-rose-500/20 text-rose-400 border-rose-500/30";    // Red
    case "high":
      return "bg-orange-500/20 text-orange-400 border-orange-500/30"; // Orange
    case "medium":
      return "bg-amber-500/20 text-amber-400 border-amber-500/30";  // Yellow
    case "low":
      return "bg-slate-500/20 text-slate-400 border-slate-500/30";  // Gray
  }
};

// TODO: Replace mock data with real auditd events
useEffect(() => {
  // CURRENT: Mock data for demonstration
  const mockEvents: AuditEvent[] = [
    {
      id: "1",
      timestamp: new Date(Date.now() - 1000 * 60 * 5),  // 5 minutes ago
      type: "execve",                                     // Process execution
      severity: "low",
      description: "Process execution: /usr/bin/python3",
      action: "Logged",
      user: "www-data",
      process: "python3",
    },
    // ...more events
  ];
  
  setEvents(mockEvents);
  
  // FUTURE: Fetch from backend
  /*
  const fetchEvents = async () => {
    const res = await fetch("/api/v1/security/events?hours=24");
    const data = await res.json();
    setEvents(data.events);
  };
  
  fetchEvents();
  const interval = setInterval(fetchEvents, 5000);  // Refresh every 5s
  return () => clearInterval(interval);
  */
}, []);

// ============================================================================
// 4. METRICS PAGE (/metrics/page.tsx)
// ============================================================================

/**
 * Metrics Page - Embedded Grafana Dashboards
 * 
 * PURPOSE:
 * - Embeds Grafana dashboards for technical metrics
 * - Provides tab navigation for different metric categories
 * - Shows monitoring stack status (Prometheus, Grafana, Loki)
 * 
 * GRAFANA CONFIGURATION REQUIRED:
 * 1. Create dashboards in Grafana:
 *    - sentinel-overview (system health)
 *    - sentinel-host (CPU, memory, disk, GPU)
 *    - sentinel-db (PostgreSQL metrics)
 *    - sentinel-network (network traffic)
 *    - sentinel-ai (Ollama performance)
 * 
 * 2. Enable iframe embedding in Grafana:
 *    grafana.ini: allow_embedding = true
 * 
 * 3. Ensure user is authenticated (or enable anonymous access)
 */

// Grafana URL structure
const grafanaUrls: Record<MetricTab, string> = {
  // Format: http://localhost:3001/d/{dashboard-id}/{dashboard-name}?params
  overview: "http://localhost:3001/d/sentinel-overview/sentinel-overview?orgId=1&refresh=5s&kiosk",
  //                                    ^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^  ^^^^^^  ^^^^^^^^^^  ^^^^^
  //                                    Dashboard ID     Dashboard Name    Org ID  Auto-refresh Kiosk mode
  
  // orgId=1: Default Grafana organization
  // refresh=5s: Auto-refresh every 5 seconds
  // kiosk: Hide Grafana UI (menu, header, etc.) for clean embedding
};

// Iframe configuration
<iframe
  src={grafanaUrls[activeTab]}
  className="w-full h-[800px]"  // Fixed height for consistent layout
  frameBorder="0"                // No border around iframe
  title={`Grafana ${activeTab} dashboard`}  // Accessibility label
/>

// Fallback if iframe doesn't load (CORS, auth, etc.)
<p className="text-sm text-gray-400">
  Dashboard not loading?{" "}
  <a
    href={grafanaUrls[activeTab].replace("&kiosk", "")}  // Remove kiosk mode
    target="_blank"
    rel="noopener noreferrer"
    className="text-cyan-400 hover:text-cyan-300 underline"
  >
    Open in new tab
  </a>
</p>

// ============================================================================
// 5. API PROXY ROUTES
// ============================================================================

/**
 * AI Query Proxy (/api/v1/ai/query/route.ts)
 * 
 * PURPOSE:
 * - Proxies AI queries from frontend to backend
 * - Hides backend URL from client (security)
 * - Enables server-side requests (SSR)
 * 
 * FLOW:
 * Browser → Next.js API Route → Backend (Docker) → Ollama → Response
 * 
 * WHY PROXY?
 * - Backend runs in Docker network, not accessible from browser
 * - CORS issues if calling backend directly
 * - Can add caching, rate limiting, etc. in future
 */

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward request to backend (Docker service name)
    const backendUrl = "http://backend:8000";  // NOT localhost!
    console.log(`[AI Proxy] Forwarding to ${backendUrl}/api/v1/ai/query`);
    console.log(`[AI Proxy] Body:`, body);
    
    const response = await fetch(`${backendUrl}/api/v1/ai/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    
    console.log(`[AI Proxy] Response status: ${response.status}`);
    
    // Handle non-200 responses
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[AI Proxy] Backend error: ${errorText}`);
      return NextResponse.json(
        { error: `Backend returned ${response.status}` },
        { status: response.status }
      );
    }
    
    // Forward successful response to client
    const data = await response.json();
    console.log(`[AI Proxy] Success, response length: ${data.response?.length || 0}`);
    return NextResponse.json(data);
    
  } catch (error) {
    console.error("[AI Proxy] Error:", error);
    return NextResponse.json(
      { error: "Failed to connect to AI service", details: String(error) },
      { status: 500 }
    );
  }
}

// ============================================================================
// 6. COMMON UTILITY FUNCTIONS
// ============================================================================

/**
 * cn() - Class Name Merger
 * Location: src/lib/utils.ts
 * 
 * PURPOSE:
 * - Merges Tailwind CSS classes intelligently
 * - Handles conflicts (last class wins)
 * - Used by all shadcn/ui components
 * 
 * EXAMPLE:
 * cn("px-4 py-2", "px-6")  // Result: "py-2 px-6" (px-6 overrides px-4)
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage in components:
<div className={cn(
  "base-classes",
  condition && "conditional-classes",
  props.className  // Allow parent to override
)} />

// ============================================================================
// END OF INLINE COMMENTS GUIDE
// ============================================================================

/**
 * NEXT STEPS FOR DEVELOPERS:
 * 
 * 1. Copy relevant comments into actual component files
 * 2. Add TODO comments for incomplete features
 * 3. Update comments when modifying code
 * 4. Add JSDoc comments for exported functions
 * 5. Document complex algorithms with inline comments
 * 
 * REMEMBER:
 * - Comments should explain WHY, not WHAT
 * - Keep comments up-to-date with code changes
 * - Use TODO, FIXME, NOTE, HACK as needed
 * - Add links to relevant documentation
 */
