// GLSL Shader: Flower of Life - Constructive Interference
// This shader visualizes wave interference across 7 circles

varying vec2 vUv;
uniform float time;
uniform float coherence;
uniform vec2 circlePositions[7];

void main() {
    vec2 uv = vUv;
    
    // Accumulate waves from all 7 sources
    float wave = 0.0;
    float amplitude = 0.0;
    
    for(int i = 0; i < 7; i++) {
        vec2 center = circlePositions[i];
        float dist = distance(uv, center);
        
        // Standing wave equation: sin(kx - ωt)
        float k = 10.0; // Wave number
        float omega = 2.0; // Angular frequency
        
        float w = sin(k * dist - omega * time) / (1.0 + dist * 5.0);
        wave += w;
        amplitude += abs(w);
    }
    
    // Normalize
    wave = wave / 7.0;
    amplitude = amplitude / 7.0;
    
    // Constructive interference creates bright spots
    float interference = smoothstep(0.3, 0.7, amplitude);
    
    // Color gradient: Blue (low) → Green (mid) → Gold (high)
    vec3 colorLow = vec3(0.1, 0.4, 0.9);    // Blue
    vec3 colorMid = vec3(0.2, 0.9, 0.5);    // Green
    vec3 colorHigh = vec3(1.0, 0.84, 0.0);  // Gold
    
    vec3 color = mix(
        mix(colorLow, colorMid, interference),
        colorHigh,
        coherence * interference
    );
    
    // Add glow at interference peaks
    float glow = pow(interference, 3.0);
    color += vec3(glow * 0.5);
    
    gl_FragColor = vec4(color, 0.8 + interference * 0.2);
}
