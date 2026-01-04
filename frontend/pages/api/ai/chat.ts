import type { NextApiRequest, NextApiResponse } from "next";
import axios from "axios";

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== "POST") {
        return res.status(405).json({ message: "Method not allowed" });
    }

    const { prompt, model = "llama3" } = req.body;

    if (!prompt) {
        return res.status(400).json({ message: "Prompt is required" });
    }

    try {
        // Conexión directa a Ollama local
        // Asegúrate de que Ollama esté corriendo en el puerto 11434
        const response = await axios.post("http://127.0.0.1:11434/api/generate", {
            model: model,
            prompt: prompt,
            stream: false
        }, {
            timeout: 60000 // 60 segundos de timeout para respuestas largas
        });

        return res.status(200).json(response.data);
    } catch (error: any) {
        console.error("AI Proxy Error:", error.message);

        // Manejo de errores específicos
        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                message: "Ollama no está disponible. Asegúrate de ejecutar 'ollama serve' o 'ollama run llama3'."
            });
        }

        return res.status(500).json({
            message: "Error connecting to AI Core",
            error: error.message
        });
    }
}
