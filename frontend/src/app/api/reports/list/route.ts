import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
    try {
        const docsDir = "/home/jnovoas/sentinel/docs";

        if (!fs.existsSync(docsDir)) {
            return NextResponse.json({ files: [] });
        }

        const files = fs.readdirSync(docsDir)
            .filter(file => file.endsWith(".md"))
            .map(file => ({
                name: file,
                path: path.join(docsDir, file)
            }));

        return NextResponse.json({ files });
    } catch (error) {
        return NextResponse.json({ error: "Failed to list docs" }, { status: 500 });
    }
}
