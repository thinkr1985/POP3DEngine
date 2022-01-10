#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec2 inTexCoords;
layout(location = 3) in vec3 normalTex;

out vec3 newColor;
out vec3 normalMap;
out vec2 outTexCoords;

uniform mat4 model;
uniform mat4 projection;

void main()
{
    gl_Position = projection * model * vec4(position, 1.0);
    newColor = color;
    outTexCoords = inTexCoords;
    normalMap = normalTex;
}

