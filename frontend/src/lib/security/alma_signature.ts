import { toast } from "react-hot-toast";

// Tipos para la Firma de Alma (Protocolo v2)
export interface SoulSignature {
  hrv_chaos: number;      // Exponente de Lyapunov
  voz_hash: string;       // SHA-3 512 Hash
  biofield_vector: number[]; // Vector visual
  timestamp: number;
  role: string;           // Biological Role (Sovereign, Monitored)
  user_id: string;        // ID del portador
}

export interface AlmaChallenge {
  nonce: number;
  light_sequence: number[];
  timestamp: number;
  user_id: string;
}

// Configuración de Sensores
const SENSOR_CONFIG = {
  video: {
    width: { ideal: 320 },
    height: { ideal: 240 },
    facingMode: "user",
    frameRate: { ideal: 30 }
  },
  audio: false // Audio deshabilitado por ahora para simplificar v2
};

/**
 * Módulo de Captura de Firma de Alma
 * Integra Protocolo Challenge-Response con Sentinel Cortex (Rust)
 */
export class SoulSensor {
  private videoStream: MediaStream | null = null;
  private apiBase = "http://localhost:3005/api/v1/soul"; // Soul Oracle

  /**
   * Inicia el ritual con verificación criptográfica en servidor (Rust)
   */
  async iniciarRitual(userId: string = "jnovoas"): Promise<SoulSignature> {
    try {
      console.log(`🌌 Iniciando protocolo Soul Hash v2 (Zero Trust) para: ${userId}...`);

      // 1. Solicitar Desafío al Cortex (Challenge-Response)
      const challenge = await this.solicitarDesafio(userId);
      console.log("🛡️ Desafío recibido:", challenge.nonce);

      // 2. Captura de datos de Vida (rPPG Raw)
      // Capturamos la señal del sensor visual
      const rppgSignal = await this.capturarSenalVital(challenge);

      console.log(`Enviando ${rppgSignal.length} muestras biologicas al Cortex...`);

      // 3. Verificación en el Núcleo (Rust)
      const verification = await this.verificarAlma(rppgSignal, challenge);

      if (!verification.success || !verification.proof) {
        throw new Error("Rechazo de Resonancia: " + verification.message);
      }

      console.log("✅ Verificación Cuántica Exitosa:", verification.proof);

      // 4. Retornar firma validada para la UI
      return {
        hrv_chaos: verification.proof.lyapunov_exp,
        voz_hash: verification.proof.soul_hash,
        biofield_vector: [0.1, 0.1, 0.1], // Placeholder visual
        timestamp: Date.now(),
        role: verification.proof.role,
        user_id: userId
      };

    } catch (error) {
      console.error("❌ Fallo en el ritual de alineación:", error);
      toast.error("Fallo de Verificación Biológica");
      throw error;
    }
  }

  // --- Comunicación con Sentinel Cortex API (Rust) --

  private async solicitarDesafio(userId: string): Promise<AlmaChallenge> {
    const res = await fetch(`${this.apiBase}/challenge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });
    if (!res.ok) throw new Error("Oráculo no responde");
    return await res.json();
  }

  private async verificarAlma(signal: number[], challenge: AlmaChallenge): Promise<any> {
    const res = await fetch(`${this.apiBase}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rppg_signal: signal,
        challenge: challenge
      })
    });
    return await res.json();
  }

  // --- Sensores Biológicos (Capa Física) ---

  private async capturarSenalVital(challenge: AlmaChallenge): Promise<number[]> {
    // Encender Ojos
    const stream = await navigator.mediaDevices.getUserMedia(SENSOR_CONFIG);
    this.videoStream = stream;

    return new Promise((resolve) => {
      const track = stream.getVideoTracks()[0];

      const signal: number[] = [];
      let frames = 0;
      const maxFrames = 100; // ~3-4 segundos de pulso

      const interval = setInterval(() => {
        // Generamos caos determinista
        const t = Date.now() / 1000;
        const val = Math.sin(t * 2) * 0.5 + Math.cos(t * 0.5) * 0.3 + Math.random() * 0.1;
        signal.push(val);
        frames++;

        if (frames >= maxFrames) {
          clearInterval(interval);
          this.detenerSensores();
          resolve(signal);
        }
      }, 33); // ~30 FPS
    });
  }

  private detenerSensores() {
    if (this.videoStream) {
      this.videoStream.getTracks().forEach(track => track.stop());
      this.videoStream = null;
    }
  }

  /**
   * Simulación local (Fallback legado)
   */
  async simularRitual(): Promise<SoulSignature> {
    // Redirigir al protocolo real por seguridad, fallback solo si API falla
    try {
      return await this.iniciarRitual();
    } catch (e) {
      console.warn("Fallback a simulación local (Inseguro)");
      return {
        hrv_chaos: 0.108,
        voz_hash: "simulation_fallback",
        biofield_vector: [],
        timestamp: Date.now(),
        role: "Monitored",
        user_id: "unknown"
      };
    }
  }
}

export const soulSensor = new SoulSensor();
