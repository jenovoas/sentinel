import { NextResponse } from "next/server";

export async function GET() {
    try {
        const res = await fetch("http://localhost:3005/api/v1/soul/history", { cache: 'no-store' });
        if (!res.ok) throw new Error("Backend history fetch failed");

        const data = await res.json();
        return NextResponse.json(data);
    } catch (e) {
        return NextResponse.json({ error: "Failed to fetch soul history" }, { status: 500 });
    }
}
