"use client";

import { useState, useEffect } from "react";

export function WipModal() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const dismissed = localStorage.getItem("cortex-wip-dismissed");
    if (!dismissed) setVisible(true);
  }, []);

  if (!visible) return null;

  const handleClose = () => {
    localStorage.setItem("cortex-wip-dismissed", "1");
    setVisible(false);
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0, 0, 0, 0.75)",
        backdropFilter: "blur(8px)",
        padding: "1rem",
      }}
      onClick={handleClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "rgba(15, 23, 42, 0.98)",
          border: "1px solid rgba(34, 211, 238, 0.25)",
          borderRadius: "16px",
          padding: "2.5rem 2rem",
          maxWidth: "480px",
          width: "100%",
          textAlign: "center",
          boxShadow: "0 0 60px rgba(34, 211, 238, 0.1), 0 25px 50px rgba(0,0,0,0.5)",
        }}
      >
        {/* Icono */}
        <div style={{ fontSize: "3.5rem", marginBottom: "1rem" }}>🚧</div>

        {/* Título */}
        <h2 style={{
          fontSize: "1.5rem",
          fontWeight: 700,
          color: "#f1f5f9",
          marginBottom: "0.75rem",
          letterSpacing: "-0.01em",
        }}>
          Sentinel <span style={{ color: "#22d3ee" }}>Cortex</span>
        </h2>

        {/* Subtítulo */}
        <p style={{
          fontSize: "1rem",
          color: "#94a3b8",
          marginBottom: "0.5rem",
          fontWeight: 500,
        }}>
          Servicio en implementación
        </p>

        <p style={{
          fontSize: "0.875rem",
          color: "#64748b",
          marginBottom: "2rem",
          lineHeight: "1.6",
        }}>
          Estamos construyendo la plataforma de observabilidad y seguridad empresarial.
          Algunas funcionalidades pueden no estar disponibles aún.
        </p>

        {/* Badges de estado */}
        <div style={{
          display: "flex",
          gap: "0.5rem",
          justifyContent: "center",
          flexWrap: "wrap",
          marginBottom: "2rem",
        }}>
          {[
            { label: "Dashboard", color: "#22d3ee", bg: "rgba(34,211,238,0.1)" },
            { label: "Métricas", color: "#a78bfa", bg: "rgba(167,139,250,0.1)" },
            { label: "AI Playground", color: "#f59e0b", bg: "rgba(245,158,11,0.1)" },
            { label: "Security", color: "#f43f5e", bg: "rgba(244,63,94,0.1)" },
          ].map((b) => (
            <span
              key={b.label}
              style={{
                padding: "0.25rem 0.75rem",
                borderRadius: "99px",
                fontSize: "0.75rem",
                fontWeight: 600,
                color: b.color,
                background: b.bg,
                border: `1px solid ${b.color}33`,
              }}
            >
              {b.label}
            </span>
          ))}
        </div>

        {/* Botón */}
        <button
          onClick={handleClose}
          style={{
            padding: "0.75rem 2rem",
            background: "linear-gradient(135deg, rgba(34,211,238,0.15), rgba(34,211,238,0.05))",
            border: "1px solid rgba(34,211,238,0.4)",
            borderRadius: "10px",
            color: "#22d3ee",
            fontSize: "0.95rem",
            fontWeight: 600,
            cursor: "pointer",
            transition: "all 0.2s ease",
            width: "100%",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.background = "rgba(34,211,238,0.2)";
            (e.currentTarget as HTMLElement).style.boxShadow = "0 0 20px rgba(34,211,238,0.2)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.background = "linear-gradient(135deg, rgba(34,211,238,0.15), rgba(34,211,238,0.05))";
            (e.currentTarget as HTMLElement).style.boxShadow = "none";
          }}
        >
          Entendido, explorar igual →
        </button>

        <p style={{ fontSize: "0.75rem", color: "#475569", marginTop: "1rem" }}>
          ← PinguinoSeguro · cortex.pinguinoseguro.cl
        </p>
      </div>
    </div>
  );
}
