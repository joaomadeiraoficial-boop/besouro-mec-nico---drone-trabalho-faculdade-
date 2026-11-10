#version 150 core
in vec3 vertexPosition;
uniform mat4 modelMatrix, lightMatrix;
void main() {
    gl_Position = lightMatrix * modelMatrix * vec4(vertexPosition, 1.0);
}
