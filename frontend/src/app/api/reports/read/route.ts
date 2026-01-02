import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const filename = searchParams.get("file");

    if (!filename) {
        return NextResponse.json({ error: "File name required" }, { status: 400 });
    }

    // Security: Prevent directory traversal
    const safeFilename = path.basename(filename);
    const docsDir = "/home/jnovoas/sentinel/docs";
    const filePath = path.join(docsDir, safeFilename);

    try {
        if (!fs.existsSync(filePath)) {
            return NextResponse.json({ error: "File not found" }, { status: 404 });
        }

        const content = fs.readFileSync(filePath, "utf-8");
        return NextResponse.json({ content });
    } catch (error) {
        return NextResponse.json({ error: "Failed to read file" }, { status: 500 });
    }
}
