// GLSL Shader: Neural Hierarchy - Fractal Temporal Flow
// Visualizes 7 hierarchical levels with α/β balance

varying vec2 vUv;
varying float vLevel;
uniform float time;
uniform float coherence;
uniform float alphaBalance[7];
uniform float betaBalance[7];

void main() {
    // Determine which level (0-6) based on Y position
    int level = int(floor(vLevel * 7.0));
    
    // Get α (excitation) and β (inhibition) for this level
    float alpha = alphaBalance[level];
    float beta = betaBalance[level];
    
    // Colors
    vec3 alphaColor = vec3(0.2, 0.5, 1.0);  // Blue (excitation)
    vec3 betaColor = vec3(1.0, 0.3, 0.3);   // Red (inhibition)
    vec3 balanceColor = vec3(0.5, 1.0, 0.5); // Green (equilibrium)
    
    // Balance ratio
    float balance = alpha / (alpha + beta + 0.001);
    
    // Mix colors based on balance
    vec3 color = mix(betaColor, alphaColor, balance);
    
    // At equilibrium (α ≈ β), shift to green
    float equilibrium = 1.0 - abs(balance - 0.5) * 2.0;
    color = mix(color, balanceColor, equilibrium * coherence);
    
    // Temporal flow - waves moving up the hierarchy
    float wave = sin(vUv.y * 10.0 - time * 1.5 + float(level) * 0.5);
    color += vec3(wave * 0.1);
    
    // Golden spiral overlay at high coherence
    float spiral = sin(atan(vUv.x - 0.5, vUv.y - 0.5) * 5.0 - time);
    color += vec3(1.0, 0.84, 0.0) * spiral * coherence * 0.2;
    
    gl_FragColor = vec4(color, 0.85);
}
