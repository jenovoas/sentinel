import { NextResponse } from "next/server";

export async function GET() {
    try {
        const backendUrl = "http://backend:8000";
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
