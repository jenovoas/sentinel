/**
 * WASM Loader for Sentinel
 * 
 * Handles initialization and provides typed interface for Rust WASM functions
 */

let wasmModule: typeof import('../../../sentinel-wasm/pkg/sentinel_wasm') | null = null;
let wasmInitialized = false;

export interface TelemetryEvent {
    message: string;
    source: string;
    timestamp: number;
}

/**
 * Initialize WASM module (call once on app start)
 */
export async function initWasm(): Promise<void> {
    if (wasmInitialized) return;

    try {
        // Dynamic import of WASM module
        wasmModule = await import('../../../sentinel-wasm/pkg/sentinel_wasm');
        wasmInitialized = true;
        console.log('✅ WASM module initialized');
    } catch (error) {
        console.error('❌ Failed to initialize WASM:', error);
        throw error;
    }
}

/**
 * Detect AIOpsDoom attack in single message
 * @returns true if malicious pattern detected
 */
export function detectAIOpsD(message: string): boolean {
    if (!wasmModule) {
        throw new Error('WASM not initialized. Call initWasm() first.');
    }

    return wasmModule.detect_aiopsdoom(message);
}

/**
 * Detect AIOpsDoom in batch (optimized for bulk processing)
 * @returns array of boolean results (same order as input)
 */
export function detectAIOpsDoomBatch(events: TelemetryEvent[]): boolean[] {
    if (!wasmModule) {
        throw new Error('WASM not initialized. Call initWasm() first.');
    }

    return wasmModule.detect_aiopsdoom_batch(events);
}

/**
 * Calculate anomaly score for metric values
 * @param values - Array of metric values
 * @param threshold - Z-score threshold (default: 2.0)
 * @returns Anomaly score (0-1, higher = more anomalous)
 */
export function calculateAnomalyScore(values: number[], threshold: number = 2.0): number {
    if (!wasmModule) {
        throw new Error('WASM not initialized. Call initWasm() first.');
    }

    return wasmModule.calculate_anomaly_score(values, threshold);
}

/**
 * Benchmark WASM performance
 * @param numEvents - Number of events to process
 * @returns Time in milliseconds
 */
export function benchmarkDetection(numEvents: number): number {
    if (!wasmModule) {
        throw new Error('WASM not initialized. Call initWasm() first.');
    }

    return wasmModule.benchmark_detection(numEvents);
}

/**
 * Check if WASM is initialized
 */
export function isWasmReady(): boolean {
    return wasmInitialized;
}
