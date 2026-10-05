import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const configuredUrl = (process.env.CORTEX_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "").trim();
        if (!configuredUrl) {
            return NextResponse.json(
                { error: "La URL de Cortex no está configurada" },
                { status: 503 }
            );
        }
        const backendUrl = configuredUrl.replace(/\/+$/, "").replace(/\/api$/, "");

        const response = await fetch(`${backendUrl}/api/v1/ai/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        console.log(`[AI Proxy] Response status: ${response.status}`);

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`[AI Proxy] Backend error: ${errorText}`);
            return NextResponse.json(
                { error: `Backend returned ${response.status}` },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("[AI Proxy] Error:", error);
        return NextResponse.json(
            { error: "No se pudo conectar con Cortex", details: String(error) },
            { status: 500 }
        );
    }
}

export async function GET() {
    const configuredUrl = (process.env.CORTEX_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "").trim();
    if (!configuredUrl) {
        return NextResponse.json(
            { error: "La URL de Cortex no está configurada", available: false },
            { status: 503 }
        );
    }

    const backendUrl = configuredUrl.replace(/\/+$/, "").replace(/\/api$/, "");
    try {
        const response = await fetch(`${backendUrl}/api/v1/ai/health`, { cache: "no-store" });
        const data = await response.json();
        return NextResponse.json(data, { status: response.status });
    } catch (error) {
        console.error("AI health check error:", error);
        return NextResponse.json(
            { error: "No se pudo conectar con Cortex", available: false },
            { status: 503 }
        );
    }
}
