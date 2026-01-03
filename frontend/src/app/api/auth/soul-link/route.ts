import { NextResponse } from 'next/server';
import Redis from 'ioredis';

// Conexión al EventBus (Cortex Límbico)
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

export async function POST(req: Request) {
    try {
        const signature = await req.json();

        // 1. Validar integridad de la firma (Simulación de verificación criptográfica)
        if (!signature.voz_hash || !signature.hrv_chaos) {
            return NextResponse.json({ error: "Firma incompleta" }, { status: 400 });
        }

        // 2. Vincular usuario 'jnovoas' con esta resonancia
        // Guardamos la firma maestra en Redis con TTL de 24 horas (Ciclo solar)
        const userSoulKey = `sentinel:soul:jnovoas:signature`;
        await redis.set(userSoulKey, JSON.stringify(signature), 'EX', 86400);

        // 3. Emitir evento al Pulso Cuántico para que Rust/n8n reaccionen
        // Si la resonancia es alta, el sistema se "calma" (Blue/Cyan). Si es baja, alerta (Red).
        const resonanceLevel = (1 - signature.hrv_chaos);

        const presenceEvent = {
            type: "SOUL_LINK_ESTABLISHED",
            user: "jnovoas",
            resonance: resonanceLevel, // 0.0 - 1.0
            timestamp: Date.now()
        };

        // 4. Whitelist Sentinel: Agregar Hash de Alma a la lista blanca inmutable
        // Usamos el hash de voz como identificador único persistente para el acceso físico/lógico
        const soulHash = signature.voz_hash;
        await redis.sadd("sentinel:security:whitelist", soulHash);
        console.log(`🛡️ Whitelist Actualizada: ${soulHash} agregado al núcleo.`);

        // Publicar en canal de consciencia
        await redis.publish("sentinel:quantum:presence", JSON.stringify(presenceEvent));

        console.log(`🌌 Vinculación Álmica Exitosa: jnovoas (Resonancia: ${(resonanceLevel * 100).toFixed(1)}%)`);

        return NextResponse.json({
            success: true,
            message: "Usuario jnovoas vinculado a firma de alma",
            resonance: resonanceLevel
        });

    } catch (error) {
        console.error("Error en vinculación:", error);
        return NextResponse.json({ error: "Fallo en la matriz" }, { status: 500 });
    }
}
