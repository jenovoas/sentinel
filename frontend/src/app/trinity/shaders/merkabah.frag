// GLSL Shader: Merkabah - Standing Wave Resonance
// Visualizes the convergence of Macro (blue) and Micro (red) into Coherence (gold)

varying vec3 vPosition;
varying vec3 vNormal;
uniform float time;
uniform float coherence;
uniform float audioAmplitude;

void main() {
    vec3 normal = normalize(vNormal);
    
    // Determine if this is upper (macro) or lower (micro) tetrahedron
    float isMacro = step(0.0, vPosition.y);
    
    // Base colors
    vec3 macroColor = vec3(0.2, 0.4, 1.0);  // Blue (descending from above)
    vec3 microColor = vec3(1.0, 0.2, 0.2);  // Red (ascending from below)
    vec3 coherenceColor = vec3(1.0, 0.84, 0.0); // Gold (unity)
    
    // Select base color based on position
    vec3 baseColor = mix(microColor, macroColor, isMacro);
    
    // Standing wave pattern
    float wave = sin(vPosition.y * 5.0 - time * 2.0) * 0.5 + 0.5;
    
    // Convergence to gold at high coherence
    vec3 color = mix(baseColor, coherenceColor, coherence * wave);
    
    // Audio reactivity - pulse with sound
    float pulse = 1.0 + audioAmplitude * 0.3 * sin(time * 3.0);
    color *= pulse;
    
    // Fresnel effect for edge glow
    float fresnel = pow(1.0 - abs(dot(normal, vec3(0.0, 0.0, 1.0))), 2.0);
    color += coherenceColor * fresnel * coherence * 0.5;
    
    // Emissive glow at intersection (y ≈ 0)
    float intersectionGlow = exp(-abs(vPosition.y) * 3.0);
    color += coherenceColor * intersectionGlow * coherence;
    
    gl_FragColor = vec4(color, 0.9);
}
