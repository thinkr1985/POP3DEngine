#version 330 core

in vec3 newColor;
in vec2 outTexCoords;
in vec3 normalMap;

layout(location = 0) out vec4 outColor;
layout(location = 1) out vec3 outNormal;

uniform sampler2D samplerTex;
uniform sampler2D normalTex;
uniform vec3 lightColor;

void main()
{
    outColor = texture(samplerTex, outTexCoords);
    //FragColor = vec4(1.0, 1.0, 1.0, 1.0);
    outNormal = normalize(texture( normalTex, outTexCoords ).rgb*2.0 - 1.0);
}
