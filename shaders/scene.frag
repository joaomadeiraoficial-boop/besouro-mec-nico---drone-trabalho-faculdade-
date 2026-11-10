#version 150 core
uniform sampler2D surfaceImage, shadowMap;
uniform vec3 baseColor, toLight;
uniform vec2 repeatUV;
uniform vec2 texel;
in vec3 normal;
in vec2 uv;
in vec4 lightClip;
out vec4 fragColor;
float visibility(float diffuse) {
    vec3 p = lightClip.xyz / lightClip.w * 0.5 + 0.5;
    if (any(lessThan(p, vec3(0))) || any(greaterThan(p, vec3(1)))) return 1.0;
    float bias = max(0.0005, 0.0018 * (1.0 - diffuse));
    float lit = 0.0;
    for (int y = -1; y <= 1; ++y)
        for (int x = -1; x <= 1; ++x)
            lit += step(p.z - bias, texture(shadowMap, p.xy + vec2(x,y)*texel).r);
    return lit / 9.0;
}
void main() {
    float diffuse = max(dot(normalize(normal), toLight), 0.0);
    vec3 albedo = baseColor * texture(surfaceImage, uv * repeatUV).rgb;
    fragColor = vec4(albedo * (0.36 + 0.64 * diffuse * visibility(diffuse)), 1.0);
}
