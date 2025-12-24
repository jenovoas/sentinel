'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { createMerkabah, createHierarchy, createFlowerOfLife, detectGPUQuality } from '../utils/geometry';
import { getAudioEngine, destroyAudioEngine } from '../utils/audioEngine';
import { createMerkabahShader, createFlowerShader, createHierarchyShader } from '../utils/shaderLoader';

interface TrinityScene3DProps {
    coherence?: number;
    audioEnabled?: boolean;
    onAudioToggle?: (enabled: boolean) => void;
}

export default function TrinityScene3D({
    coherence = 0,
    audioEnabled = false,
    onAudioToggle
}: TrinityScene3DProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const composerRef = useRef<EffectComposer | null>(null);
    const merkabahRef = useRef<ReturnType<typeof createMerkabah> | null>(null);
    const hierarchyRef = useRef<ReturnType<typeof createHierarchy> | null>(null);
    const flowerRef = useRef<ReturnType<typeof createFlowerOfLife> | null>(null);
    const animationFrameRef = useRef<number | null>(null);

    const [quality, setQuality] = useState<'high' | 'medium' | 'low'>('high');

    useEffect(() => {
        if (!containerRef.current) return;

        // Detect GPU quality
        const gpuQuality = detectGPUQuality();
        setQuality(gpuQuality);
        console.log(`🎮 GPU Quality: ${gpuQuality}`);

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000);
        scene.fog = new THREE.Fog(0x000000, 10, 50);
        sceneRef.current = scene;

        // Camera
        const camera = new THREE.PerspectiveCamera(
            75,
            containerRef.current.clientWidth / containerRef.current.clientHeight,
            0.1,
            1000
        );
        camera.position.set(0, 0, 15);

        // Renderer
        const renderer = new THREE.WebGLRenderer({
            antialias: gpuQuality !== 'low',
            alpha: true,
            powerPreference: gpuQuality === 'high' ? 'high-performance' : 'default'
        });
        renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, gpuQuality === 'high' ? 2 : 1));
        containerRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.5;

        // Post-processing (only on medium/high quality)
        let composer: EffectComposer;
        if (gpuQuality !== 'low') {
            composer = new EffectComposer(renderer);
            const renderPass = new RenderPass(scene, camera);
            composer.addPass(renderPass);

            const bloomPass = new UnrealBloomPass(
                new THREE.Vector2(containerRef.current.clientWidth, containerRef.current.clientHeight),
                gpuQuality === 'high' ? 1.5 : 1.0,  // strength
                0.4,  // radius
                0.85  // threshold
            );
            composer.addPass(bloomPass);
            composerRef.current = composer;
        }

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x3B82F6, 1, 100);
        pointLight1.position.set(5, 5, 5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0xEF4444, 1, 100);
        pointLight2.position.set(-5, -5, 5);
        scene.add(pointLight2);

        const pointLight3 = new THREE.PointLight(0xFFD700, 2, 100);
        pointLight3.position.set(0, 0, 5);
        scene.add(pointLight3);

        // Create Trinity layers
        const merkabah = createMerkabah();
        merkabah.group.position.y = 5;
        scene.add(merkabah.group);
        merkabahRef.current = merkabah;

        const hierarchy = createHierarchy();
        hierarchy.group.position.y = 0;
        scene.add(hierarchy.group);
        hierarchyRef.current = hierarchy;

        const flower = createFlowerOfLife();
        flower.group.position.y = -5;
        scene.add(flower.group);
        flowerRef.current = flower;

        // Apply shaders to geometries (if GPU quality allows)
        if (gpuQuality !== 'low') {
            console.log('🎨 Applying GLSL shaders to Trinity geometries');

            // Apply Merkabah shader to both tetrahedrons
            const merkabahShader = createMerkabahShader(0, 0, 0);
            merkabah.macro.material = merkabahShader.clone();
            merkabah.micro.material = merkabahShader.clone();
        }

        // Particle field (only on high quality)
        if (gpuQuality === 'high') {
            const particleCount = 1000;
            const particlesGeometry = new THREE.BufferGeometry();
            const particlePositions = new Float32Array(particleCount * 3);

            for (let i = 0; i < particleCount * 3; i++) {
                particlePositions[i] = (Math.random() - 0.5) * 50;
            }

            particlesGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
            const particlesMaterial = new THREE.PointsMaterial({
                color: 0xffffff,
                size: 0.05,
                transparent: true,
                opacity: 0.6
            });
            const particles = new THREE.Points(particlesGeometry, particlesMaterial);
            scene.add(particles);
        }

        // Animation loop
        let time = 0;
        const animate = () => {
            animationFrameRef.current = requestAnimationFrame(animate);
            time += 0.01;

            // Get audio amplitude if enabled
            let audioAmplitude = 0;
            if (audioEnabled) {
                const audioEngine = getAudioEngine();
                if (audioEngine.isReady()) {
                    audioAmplitude = audioEngine.getAmplitude();
                }
            }

            // Animate Merkabah
            if (merkabahRef.current) {
                const { macro, micro, coherenceSphere } = merkabahRef.current;

                // Rotate tetrahedrons
                macro.rotation.y = time * 0.5;
                micro.rotation.y = -time * 0.5;

                // Update shader uniforms if using ShaderMaterial
                if (macro.material instanceof THREE.ShaderMaterial) {
                    macro.material.uniforms.time.value = time;
                    macro.material.uniforms.coherence.value = coherence;
                    macro.material.uniforms.audioAmplitude.value = audioAmplitude;
                }
                if (micro.material instanceof THREE.ShaderMaterial) {
                    micro.material.uniforms.time.value = time;
                    micro.material.uniforms.coherence.value = coherence;
                    micro.material.uniforms.audioAmplitude.value = audioAmplitude;
                }

                // Pulse coherence sphere with audio
                const baseScale = 1.0;
                const audioScale = audioAmplitude * 0.3;
                const pulseScale = Math.sin(time * 2) * 0.1;
                const scale = baseScale + audioScale + pulseScale;
                coherenceSphere.scale.set(scale, scale, scale);

                // Update coherence sphere color based on coherence level
                let color = 0xFF3366; // THERMAL (red)
                if (coherence >= 0.95) color = 0xFFD700; // MERKABAH (gold)
                else if (coherence >= 0.75) color = 0x33FF99; // RESONANT (green)
                else if (coherence >= 0.50) color = 0xFFCC33; // SYNCING (yellow)

                (coherenceSphere.material as THREE.MeshPhongMaterial).color.setHex(color);
                (coherenceSphere.material as THREE.MeshPhongMaterial).emissive.setHex(color);
            }

            // Animate Hierarchy (wave pattern)
            if (hierarchyRef.current) {
                hierarchyRef.current.levels.forEach((level, i) => {
                    const wave = Math.sin(time * 2 + i * 0.5) * 0.1;
                    level.position.y = i * 0.8 - (7 * 0.8) / 2 + wave;
                });

                // Rotate spiral
                hierarchyRef.current.spiral.rotation.y = time * 0.2;
            }

            // Animate Flower of Life
            if (flowerRef.current) {
                flowerRef.current.group.rotation.z = time * 0.2;

                // Pulse circles
                flowerRef.current.circles.forEach((circle, i) => {
                    const pulse = Math.sin(time * 2 + i * 0.3) * 0.05 + 1;
                    circle.scale.set(pulse, pulse, pulse);
                });
            }

            controls.update();

            // Render with or without post-processing
            if (composerRef.current) {
                composerRef.current.render();
            } else {
                renderer.render(scene, camera);
            }
        };

        animate();

        // Handle window resize
        const handleResize = () => {
            if (!containerRef.current || !rendererRef.current) return;

            const width = containerRef.current.clientWidth;
            const height = containerRef.current.clientHeight;

            camera.aspect = width / height;
            camera.updateProjectionMatrix();

            rendererRef.current.setSize(width, height);

            if (composerRef.current) {
                composerRef.current.setSize(width, height);
            }
        };

        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);

            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }

            if (containerRef.current && rendererRef.current) {
                containerRef.current.removeChild(rendererRef.current.domElement);
            }

            rendererRef.current?.dispose();
            sceneRef.current?.clear();
        };
    }, []);

    // Update coherence when prop changes
    useEffect(() => {
        // Coherence updates are handled in animation loop
    }, [coherence]);

    // Handle audio toggle
    useEffect(() => {
        const initAudio = async () => {
            if (audioEnabled) {
                try {
                    const audioEngine = getAudioEngine();
                    await audioEngine.init();
                    console.log('🎤 Audio enabled');
                } catch (error) {
                    console.error('Failed to enable audio:', error);
                    onAudioToggle?.(false);
                }
            } else {
                destroyAudioEngine();
                console.log('🎤 Audio disabled');
            }
        };

        initAudio();

        return () => {
            if (!audioEnabled) {
                destroyAudioEngine();
            }
        };
    }, [audioEnabled, onAudioToggle]);

    return (
        <div className="relative w-full h-full">
            <div ref={containerRef} className="w-full h-full" />

            {/* Quality indicator */}
            <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm px-3 py-1 rounded text-xs text-white/60">
                Quality: {quality.toUpperCase()}
            </div>
        </div>
    );
}
