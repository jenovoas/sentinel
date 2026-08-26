/**
 * Navigation Component - Top NavBar
 *
 * Estilo consistente con pinguinoseguro.cl
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Badge } from "@/components/ui/badge";

interface NavItem {
    label: string;
    href: string;
    icon: string;
    badge?: string;
}

const NAV_ITEMS: NavItem[] = [
    { label: "Dashboard",    href: "/dashboard",         icon: "📊" },
    { label: "Lattice S60",  href: "/dashboard/lattice", icon: "💎", badge: "Live" },
    { label: "AI Playground",href: "/ai/playground",     icon: "🤖", badge: "AI" },
    { label: "Security",     href: "/security/watchdog", icon: "🔒", badge: "New" },
    { label: "Metrics",      href: "/metrics",           icon: "📈" },
    { label: "Analytics",    href: "/analytics",         icon: "📉" },
];

export function Navigation() {
    const pathname = usePathname();
    const [menuOpen, setMenuOpen] = useState(false);

    const isActive = (href: string) =>
        href === "/dashboard"
            ? pathname === "/" || pathname === "/dashboard"
            : pathname?.startsWith(href);

    return (
        <nav
            style={{
                position: "fixed",
                top: 0,
                left: 0,
                right: 0,
                zIndex: 50,
                background: "rgba(15, 23, 42, 0.95)",
                borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
                backdropFilter: "blur(16px)",
            }}
            role="navigation"
            aria-label="Navegación principal"
        >
            <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "0 1.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: "72px" }}>

                    {/* Logo — izquierda */}
                    <Link
                        href="/dashboard"
                        style={{ display: "flex", alignItems: "center", gap: "0.625rem", textDecoration: "none", flexShrink: 0 }}
                        aria-label="Sentinel — Inicio"
                    >
                        <span style={{ fontSize: "1.75rem" }}>🛡️</span>
                        <span style={{ fontWeight: 700, fontSize: "1.2rem", color: "#f1f5f9", letterSpacing: "-0.01em" }}>
                            Sentinel<span style={{ color: "#22d3ee" }}> Cortex</span>
                        </span>
                    </Link>

                    {/* Nav central — desktop */}
                    <div
                        role="menubar"
                        className="desktop-nav"
                        style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}
                    >
                        {NAV_ITEMS.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                role="menuitem"
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "0.4rem",
                                    padding: "0.5rem 0.875rem",
                                    color: isActive(item.href) ? "#22d3ee" : "#94a3b8",
                                    textDecoration: "none",
                                    fontSize: "0.95rem",
                                    fontWeight: 500,
                                    borderRadius: "8px",
                                    background: isActive(item.href) ? "rgba(34,211,238,0.08)" : "transparent",
                                    border: isActive(item.href) ? "1px solid rgba(34,211,238,0.2)" : "1px solid transparent",
                                    transition: "all 0.2s ease",
                                    whiteSpace: "nowrap",
                                }}
                                onMouseEnter={(e) => {
                                    if (!isActive(item.href)) {
                                        (e.currentTarget as HTMLElement).style.color = "#fff";
                                        (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.06)";
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (!isActive(item.href)) {
                                        (e.currentTarget as HTMLElement).style.color = "#94a3b8";
                                        (e.currentTarget as HTMLElement).style.background = "transparent";
                                    }
                                }}
                            >
                                <span>{item.icon}</span>
                                {item.label}
                                {item.badge && (
                                    <Badge
                                        variant="outline"
                                        style={{
                                            background: "rgba(168,85,247,0.1)",
                                            color: "#c084fc",
                                            borderColor: "rgba(168,85,247,0.2)",
                                            fontSize: "0.7rem",
                                            padding: "0 0.4rem",
                                        }}
                                    >
                                        {item.badge}
                                    </Badge>
                                )}
                            </Link>
                        ))}
                    </div>

                    {/* Status indicator — derecha */}
                    <div className="desktop-status" style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexShrink: 0 }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#34d399", display: "inline-block", animation: "pulse 2s infinite" }} />
                        <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Online</span>
                        <span style={{ color: "#475569", fontSize: "0.75rem", marginLeft: "0.5rem" }}>v2.0.0</span>
                        <Link
                            href="https://www.pinguinoseguro.cl"
                            style={{
                                marginLeft: "0.75rem",
                                padding: "0.4rem 1rem",
                                fontSize: "0.85rem",
                                fontWeight: 500,
                                color: "#22d3ee",
                                border: "1px solid rgba(34,211,238,0.3)",
                                borderRadius: "8px",
                                textDecoration: "none",
                                transition: "all 0.2s ease",
                            }}
                            onMouseEnter={(e) => {
                                (e.currentTarget as HTMLElement).style.background = "rgba(34,211,238,0.1)";
                            }}
                            onMouseLeave={(e) => {
                                (e.currentTarget as HTMLElement).style.background = "transparent";
                            }}
                        >
                            PinguinoSeguro
                        </Link>
                    </div>

                    {/* Hamburger — mobile */}
                    <button
                        className="mobile-menu-btn"
                        onClick={() => setMenuOpen((v) => !v)}
                        aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
                        aria-expanded={menuOpen}
                        style={{
                            display: "none",
                            alignItems: "center",
                            justifyContent: "center",
                            width: "40px",
                            height: "40px",
                            borderRadius: "8px",
                            background: "rgba(255,255,255,0.05)",
                            border: "1px solid rgba(255,255,255,0.08)",
                            color: "#94a3b8",
                            cursor: "pointer",
                            fontSize: "1.25rem",
                        }}
                    >
                        {menuOpen ? "✕" : "☰"}
                    </button>
                </div>
            </div>

            {/* Mobile menu */}
            {menuOpen && (
                <div
                    style={{
                        borderTop: "1px solid rgba(255,255,255,0.06)",
                        background: "rgba(15, 23, 42, 0.98)",
                        padding: "1rem 1.5rem",
                        display: "flex",
                        flexDirection: "column",
                        gap: "0.25rem",
                    }}
                    aria-label="Menú móvil"
                >
                    {NAV_ITEMS.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            onClick={() => setMenuOpen(false)}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "0.75rem",
                                padding: "0.75rem 1rem",
                                color: isActive(item.href) ? "#22d3ee" : "#94a3b8",
                                textDecoration: "none",
                                fontSize: "1rem",
                                fontWeight: 500,
                                borderRadius: "8px",
                                background: isActive(item.href) ? "rgba(34,211,238,0.08)" : "transparent",
                            }}
                        >
                            <span>{item.icon}</span>
                            {item.label}
                            {item.badge && (
                                <Badge variant="outline" style={{ fontSize: "0.7rem" }}>
                                    {item.badge}
                                </Badge>
                            )}
                        </Link>
                    ))}
                </div>
            )}

            <style jsx>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.4; }
                }
                @media (max-width: 768px) {
                    .desktop-nav { display: none !important; }
                    .desktop-status { display: none !important; }
                    .mobile-menu-btn { display: flex !important; }
                }
            `}</style>
        </nav>
    );
}
