#version 150 core
in vec3 vertexPosition;
in vec3 vertexNormal;
in vec2 vertexUV;
uniform mat4 modelMatrix, viewMatrix, projectionMatrix, lightMatrix;
out vec3 normal;
out vec2 uv;
out vec4 lightClip;
void main() {
    vec4 world = modelMatrix * vec4(vertexPosition, 1.0);
    normal = transpose(inverse(mat3(modelMatrix))) * vertexNormal;
    uv = vertexUV;
    lightClip = lightMatrix * world;
    gl_Position = projectionMatrix * viewMatrix * world;
}
