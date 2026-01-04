// GLSL Vertex Shader: Hierarchy with level information

varying vec2 vUv;
varying float vLevel;

void main() {
    vUv = uv;
    vLevel = position.y; // Y position determines hierarchy level
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
