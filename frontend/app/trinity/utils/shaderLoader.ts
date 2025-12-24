/**
 * Shader Loader Utility
 * Loads GLSL shaders and creates ShaderMaterial instances
 */

import * as THREE from 'three';

/**
 * Load shader files and create ShaderMaterial
 */
export async function loadShader(
    vertexPath: string,
    fragmentPath: string,
    uniforms: { [key: string]: THREE.IUniform }
): Promise<THREE.ShaderMaterial> {
    try {
        const [vertexShader, fragmentShader] = await Promise.all([
            fetch(vertexPath).then(r => r.text()),
            fetch(fragmentPath).then(r => r.text())
        ]);

        return new THREE.ShaderMaterial({
            vertexShader,
            fragmentShader,
            uniforms,
            transparent: true,
            side: THREE.DoubleSide,
        });
    } catch (error) {
        console.error('Failed to load shader:', error);
        throw error;
    }
}

/**
 * Create Merkabah shader material
 */
export function createMerkabahShader(time: number, coherence: number, audioAmplitude: number): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
        vertexShader: `
      varying vec3 vPosition;
      varying vec3 vNormal;

      void main() {
        vPosition = position;
        vNormal = normal;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
        fragmentShader: `
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
    `,
        uniforms: {
            time: { value: time },
            coherence: { value: coherence },
            audioAmplitude: { value: audioAmplitude }
        },
        transparent: true,
        side: THREE.DoubleSide,
    });
}

/**
 * Create Flower of Life interference shader material
 */
export function createFlowerShader(
    time: number,
    coherence: number,
    circlePositions: THREE.Vector2[]
): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
        vertexShader: `
      varying vec2 vUv;

      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
        fragmentShader: `
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
    `,
        uniforms: {
            time: { value: time },
            coherence: { value: coherence },
            circlePositions: { value: circlePositions }
        },
        transparent: true,
        side: THREE.DoubleSide,
    });
}

/**
 * Create Hierarchy fractal flow shader material
 */
export function createHierarchyShader(
    time: number,
    coherence: number,
    alphaBalance: number[],
    betaBalance: number[]
): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
        vertexShader: `
      varying vec2 vUv;
      varying float vLevel;

      void main() {
        vUv = uv;
        vLevel = position.y; // Y position determines hierarchy level
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
        fragmentShader: `
      varying vec2 vUv;
      varying float vLevel;
      uniform float time;
      uniform float coherence;
      uniform float alphaBalance[7];
      uniform float betaBalance[7];

      void main() {
        // Determine which level (0-6) based on Y position
        int level = int(floor(vLevel * 7.0));
        level = clamp(level, 0, 6);
        
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
    `,
        uniforms: {
            time: { value: time },
            coherence: { value: coherence },
            alphaBalance: { value: alphaBalance },
            betaBalance: { value: betaBalance }
        },
        transparent: true,
        side: THREE.DoubleSide,
    });
}
