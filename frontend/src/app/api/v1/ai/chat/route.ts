import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const { message, context } = await request.json();

        if (!message) {
            return NextResponse.json(
                { error: "Message is required" },
                { status: 400 }
            );
        }

        // Build context-aware system prompt
        const systemPrompt = buildSystemPrompt(context);

        // Call Ollama API
        const response = await fetch("http://localhost:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: "llama3.2:3b",
                prompt: `${systemPrompt}\n\nUser: ${message}\n\nAssistant:`,
                stream: false,
                options: {
                    temperature: 0.7,
                    top_p: 0.9,
                    num_predict: 256,
                },
            }),
        });

        if (!response.ok) {
            throw new Error(`Ollama API returned ${response.status}`);
        }

        const data = await response.json();

        return NextResponse.json({
            response: data.response.trim(),
            model: "llama3.2:3b",
            context: context,
        });
    } catch (error) {
        console.error("AI chat error:", error);
        return NextResponse.json(
            { error: "Failed to get AI response", details: String(error) },
            { status: 500 }
        );
    }
}

function buildSystemPrompt(context: any): string {
    const { pathname, trustMetrics } = context || {};

    let prompt = `You are Sentinel AI, an advanced security and observability assistant integrated into the Sentinel Cortex operating system.

Your role is to:
- Provide security insights and recommendations
- Explain system metrics and trust scores
- Guide users through the Sentinel interface
- Alert users to potential security issues
- Answer questions about eBPF, Guardian systems, and TruthSync

Current Context:
- Page: ${pathname || "unknown"}
- Trust Score: ${trustMetrics?.overall || 0}%
- Data Support: ${trustMetrics?.dataSupport || 0}%
- Base-60 Valid: ${trustMetrics?.base60Valid ? "Yes" : "No"}
- Hallucination Rate: ${((trustMetrics?.hallucinationRate || 0) * 100).toFixed(2)}%

Guidelines:
- Be concise and technical
- Use security terminology appropriately
- Reference Sentinel-specific components (Guardian Alpha/Beta, TruthSync, LSM Hook ID 199)
- If trust score < 90%, recommend caution
- Provide actionable recommendations

Respond in a helpful, professional manner.`;

    return prompt;
}
