import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        const backendUrl =
            process.env.CORTEX_INTERNAL_URL ||
            process.env.NEXT_PUBLIC_API_URL ||
            "https://cortex.pinguinoseguro.cl";
        console.log(`[AI Proxy] Forwarding to ${backendUrl}/api/v1/ai/query`);

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

export async function GET() {
    try {
        const backendUrl =
            process.env.CORTEX_INTERNAL_URL ||
            process.env.NEXT_PUBLIC_API_URL ||
            "https://cortex.pinguinoseguro.cl";
        const response = await fetch(`${backendUrl}/api/v1/ai/health`);
        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("AI health check error:", error);
        return NextResponse.json(
            { error: "Failed to connect to AI service", enabled: false },
            { status: 500 }
        );
    }
}
