import { NextResponse } from "next/server";

export async function GET() {
    try {
        const res = await fetch("http://localhost:3005/api/v1/sentinel/alerts", { cache: 'no-store' });
        if (!res.ok) throw new Error("Backend alerts fetch failed");

        const data = await res.json();
        return NextResponse.json(data);
    } catch (e) {
        return NextResponse.json({ error: "Failed to fetch sentinel alerts" }, { status: 500 });
    }
}
