/**
 * Audio Engine for Trinity GUI
 * Provides real-time audio analysis for reactive visualizations
 */

export class AudioEngine {
    private audioContext: AudioContext | null = null;
    private analyser: AnalyserNode | null = null;
    private microphone: MediaStreamAudioSourceNode | null = null;
    private dataArray: Uint8Array<ArrayBuffer> | null = null;
    private isInitialized = false;

    /**
     * Initialize audio engine with microphone input
     * Requires user permission
     */
    async init(): Promise<void> {
        if (this.isInitialized) return;

        try {
            // Create audio context
            this.audioContext = new AudioContext();

            // Create analyser node
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            // Connect microphone to analyser
            this.microphone = this.audioContext.createMediaStreamSource(stream);
            this.microphone.connect(this.analyser);

            // Prepare data array
            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);

            this.isInitialized = true;
            console.log('🎤 Audio Engine initialized');
        } catch (error) {
            console.error('Failed to initialize audio engine:', error);
            throw new Error('Microphone access denied or unavailable');
        }
    }

    /**
     * Get current audio amplitude (0-1)
     * Used for scaling Merkabah
     */
    getAmplitude(): number {
        if (!this.analyser || !this.dataArray) return 0;

        this.analyser.getByteFrequencyData(this.dataArray as Uint8Array);

        // Calculate average amplitude
        const sum = this.dataArray.reduce((a, b) => a + b, 0);
        const average = sum / this.dataArray.length;

        // Normalize to 0-1
        return average / 255;
    }

    /**
     * Get frequency data for advanced visualizations
     */
    getFrequencyData(): Uint8Array | null {
        if (!this.analyser || !this.dataArray) return null;

        this.analyser.getByteFrequencyData(this.dataArray as Uint8Array);
        return this.dataArray;
    }

    /**
     * Get dominant frequency (Hz)
     */
    getDominantFrequency(): number {
        if (!this.analyser || !this.dataArray) return 0;

        this.analyser.getByteFrequencyData(this.dataArray as Uint8Array);

        // Find index of maximum amplitude
        let maxIndex = 0;
        let maxValue = 0;

        for (let i = 0; i < this.dataArray.length; i++) {
            if (this.dataArray[i] > maxValue) {
                maxValue = this.dataArray[i];
                maxIndex = i;
            }
        }

        // Convert index to frequency
        const nyquist = this.audioContext!.sampleRate / 2;
        const frequency = (maxIndex * nyquist) / this.dataArray.length;

        return frequency;
    }

    /**
     * Check if audio engine is ready
     */
    isReady(): boolean {
        return this.isInitialized;
    }

    /**
     * Cleanup and release resources
     */
    destroy(): void {
        if (this.microphone) {
            this.microphone.disconnect();
            this.microphone.mediaStream.getTracks().forEach(track => track.stop());
        }

        if (this.analyser) {
            this.analyser.disconnect();
        }

        if (this.audioContext) {
            this.audioContext.close();
        }

        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.dataArray = null;
        this.isInitialized = false;

        console.log('🎤 Audio Engine destroyed');
    }
}

// Singleton instance
let audioEngineInstance: AudioEngine | null = null;

/**
 * Get or create audio engine instance
 */
export function getAudioEngine(): AudioEngine {
    if (!audioEngineInstance) {
        audioEngineInstance = new AudioEngine();
    }
    return audioEngineInstance;
}

/**
 * Destroy audio engine instance
 */
export function destroyAudioEngine(): void {
    if (audioEngineInstance) {
        audioEngineInstance.destroy();
        audioEngineInstance = null;
    }
}
