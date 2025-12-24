/**
 * Geometry utilities for Trinity sacred geometry
 */

import * as THREE from 'three';

/**
 * Create Merkabah (Star Tetrahedron) geometry
 * Two interlocking tetrahedrons representing Macro/Micro
 */
export function createMerkabah(): {
    macro: THREE.Mesh;
    micro: THREE.Mesh;
    coherenceSphere: THREE.Mesh;
    group: THREE.Group;
} {
    const group = new THREE.Group();

    // Tetrahedron geometry
    const tetraGeometry = new THREE.TetrahedronGeometry(2);

    // Upper tetrahedron (MACRO - Blue)
    const macroMaterial = new THREE.MeshPhongMaterial({
        color: 0x3B82F6,
        emissive: 0x1E40AF,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.7,
        side: THREE.DoubleSide,
    });
    const macro = new THREE.Mesh(tetraGeometry, macroMaterial);
    macro.position.y = 1;
    (macro as any).userData.isMacro = true; // Tag for shader replacement
    group.add(macro);

    // Lower tetrahedron (MICRO - Red)
    const microMaterial = new THREE.MeshPhongMaterial({
        color: 0xEF4444,
        emissive: 0x991B1B,
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.7,
        side: THREE.DoubleSide,
    });
    const micro = new THREE.Mesh(tetraGeometry, microMaterial);
    micro.position.y = -1;
    micro.rotation.z = Math.PI; // Inverted
    (micro as any).userData.isMicro = true; // Tag for shader replacement
    group.add(micro);

    // Coherence sphere (GOLD - Unity)
    const sphereGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const coherenceMaterial = new THREE.MeshPhongMaterial({
        color: 0xFFD700,
        emissive: 0xFFD700,
        emissiveIntensity: 2.0,
        transparent: true,
        opacity: 0.9,
    });
    const coherenceSphere = new THREE.Mesh(sphereGeometry, coherenceMaterial);
    group.add(coherenceSphere);

    return { macro, micro, coherenceSphere, group };
}

/**
 * Create Neural Hierarchy (7 levels with α/β balance)
 */
export function createHierarchy(): {
    levels: THREE.Mesh[];
    spiral: THREE.Line;
    group: THREE.Group;
} {
    const group = new THREE.Group();
    const levels: THREE.Mesh[] = [];
    const levelCount = 7;
    const levelSpacing = 0.8;

    for (let i = 0; i < levelCount; i++) {
        const size = 3 - (i * 0.3); // Decreasing size
        const geometry = new THREE.BoxGeometry(size, 0.1, size);

        // Alternate α (blue) and β (red)
        const isAlpha = i % 2 === 0;
        const material = new THREE.MeshPhongMaterial({
            color: isAlpha ? 0x60A5FA : 0xF87171,
            emissive: isAlpha ? 0x3B82F6 : 0xEF4444,
            emissiveIntensity: 0.3,
            transparent: true,
            opacity: 0.6,
        });

        const level = new THREE.Mesh(geometry, material);
        level.position.y = i * levelSpacing - (levelCount * levelSpacing) / 2;
        (level as any).userData.hierarchyLevel = i; // Tag for shader
        group.add(level);
        levels.push(level);
    }

    // Golden spiral connecting levels
    const spiralPoints: THREE.Vector3[] = [];
    for (let i = 0; i < 100; i++) {
        const t = i / 100;
        const angle = t * Math.PI * 4;
        const radius = t * 2;
        const y = t * levelCount * levelSpacing - (levelCount * levelSpacing) / 2;
        spiralPoints.push(new THREE.Vector3(
            Math.cos(angle) * radius,
            y,
            Math.sin(angle) * radius
        ));
    }

    const spiralGeometry = new THREE.BufferGeometry().setFromPoints(spiralPoints);
    const spiralMaterial = new THREE.LineBasicMaterial({
        color: 0xFFD700,
        transparent: true,
        opacity: 0.5,
    });
    const spiral = new THREE.Line(spiralGeometry, spiralMaterial);
    group.add(spiral);

    return { levels, spiral, group };
}

/**
 * Create Flower of Life (7 circles in sacred geometry pattern)
 */
export function createFlowerOfLife(): {
    circles: THREE.Mesh[];
    group: THREE.Group;
} {
    const group = new THREE.Group();
    const circles: THREE.Mesh[] = [];

    const circleRadius = 1;
    const circlePositions = [
        { x: 0, y: 0 }, // Center
        { x: circleRadius * Math.cos(0), y: circleRadius * Math.sin(0) },
        { x: circleRadius * Math.cos(Math.PI / 3), y: circleRadius * Math.sin(Math.PI / 3) },
        { x: circleRadius * Math.cos(2 * Math.PI / 3), y: circleRadius * Math.sin(2 * Math.PI / 3) },
        { x: circleRadius * Math.cos(Math.PI), y: circleRadius * Math.sin(Math.PI) },
        { x: circleRadius * Math.cos(4 * Math.PI / 3), y: circleRadius * Math.sin(4 * Math.PI / 3) },
        { x: circleRadius * Math.cos(5 * Math.PI / 3), y: circleRadius * Math.sin(5 * Math.PI / 3) },
    ];

    circlePositions.forEach((pos) => {
        const geometry = new THREE.TorusGeometry(0.5, 0.05, 16, 100);
        const material = new THREE.MeshPhongMaterial({
            color: 0x10B981,
            emissive: 0x059669,
            emissiveIntensity: 0.4,
            transparent: true,
            opacity: 0.7,
        });
        const circle = new THREE.Mesh(geometry, material);
        circle.position.set(pos.x, pos.y, 0);
        circle.rotation.x = Math.PI / 2;
        group.add(circle);
        circles.push(circle);
    });

    return { circles, group };
}

/**
 * Detect GPU capability and return quality level
 */
export function detectGPUQuality(): 'high' | 'medium' | 'low' {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');

    if (!gl) return 'low';

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (!debugInfo) return 'medium';

    const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

    // Check for high-end GPUs
    if (renderer.includes('NVIDIA') || renderer.includes('AMD') || renderer.includes('Radeon')) {
        return 'high';
    }

    // Check for integrated GPUs
    if (renderer.includes('Intel') || renderer.includes('Mali')) {
        return 'low';
    }

    return 'medium';
}
