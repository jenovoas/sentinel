/**
 * Navigation Component - Global Sidebar Menu
 * 
 * PURPOSE:
 * - Provides consistent navigation across all pages
 * - Shows active route highlighting
 * - Collapsible for more screen space
 * - Responsive design for mobile
 * 
 * USAGE:
 * Import and add to layout.tsx or each page
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface NavItem {
    label: string;
    href: string;
    icon: string;
    badge?: string;
    description: string;
}

export function Navigation() {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Navigation items with routes
    const navItems: NavItem[] = [
        {
            label: "Dashboard",
            href: "/dashboard",
            icon: "📊",
            description: "Executive overview",
        },
        {
            label: "AI Playground",
            href: "/ai/playground",
            icon: "🤖",
            badge: "AI",
            description: "Query Ollama",
        },
        {
            label: "Security",
            href: "/security/watchdog",
            icon: "🔒",
            badge: "New",
            description: "Auditd watchdog",
        },
        {
            label: "Metrics",
            href: "/metrics",
            icon: "📈",
            description: "Grafana dashboards",
        },
        {
            label: "Analytics",
            href: "/analytics",
            icon: "📉",
            description: "Historical data",
        },
    ];

    // Check if current route is active
    const isActive = (href: string) => {
        if (href === "/dashboard") {
            return pathname === "/" || pathname === "/dashboard";
        }
        return pathname?.startsWith(href);
    };

    return (
        <>
            {/* Sidebar */}
            <aside
                className={`
          fixed left-0 top-0 h-full bg-slate-950/95 backdrop-blur-xl border-r border-white/10
          transition-all duration-300 z-50
          ${isCollapsed ? "w-20" : "w-64"}
        `}
            >
                {/* Header */}
                <div className="p-6 border-b border-white/10">
                    <div className="flex items-center justify-between">
                        {!isCollapsed && (
                            <div>
                                <h1 className="text-xl font-bold text-white">Sentinel</h1>
                                <p className="text-xs text-gray-400">Control Tower</p>
                            </div>
                        )}
                        <button
                            onClick={() => setIsCollapsed(!isCollapsed)}
                            className="text-gray-400 hover:text-white transition-colors"
                            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                        >
                            {isCollapsed ? "→" : "←"}
                        </button>
                    </div>
                </div>

                {/* Navigation Items */}
                <nav className="p-4 space-y-2">
                    {navItems.map((item) => (
                        <Link key={item.href} href={item.href}>
                            <div
                                className={`
                  flex items-center gap-3 px-3 py-2 rounded-lg transition-all
                  ${isActive(item.href)
                                        ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                                        : "text-gray-400 hover:bg-white/5 hover:text-white"
                                    }
                `}
                            >
                                <span className="text-2xl">{item.icon}</span>
                                {!isCollapsed && (
                                    <>
                                        <div className="flex-1">
                                            <p className="font-medium">{item.label}</p>
                                            <p className="text-xs opacity-70">{item.description}</p>
                                        </div>
                                        {item.badge && (
                                            <Badge
                                                variant="outline"
                                                className="bg-purple-500/10 text-purple-400 border-purple-500/20 text-xs"
                                            >
                                                {item.badge}
                                            </Badge>
                                        )}
                                    </>
                                )}
                            </div>
                        </Link>
                    ))}
                </nav>

                {/* Footer */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10">
                    {!isCollapsed ? (
                        <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs text-gray-400">
                                <span>Status</span>
                                <span className="flex items-center gap-1">
                                    <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                                    Online
                                </span>
                            </div>
                            <div className="flex items-center justify-between text-xs text-gray-400">
                                <span>Version</span>
                                <span>2.0.0</span>
                            </div>
                        </div>
                    ) : (
                        <div className="flex justify-center">
                            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                        </div>
                    )}
                </div>
            </aside>

            {/* Spacer to prevent content from going under sidebar */}
            <div className={`${isCollapsed ? "ml-20" : "ml-64"} transition-all duration-300`} />
        </>
    );
}
