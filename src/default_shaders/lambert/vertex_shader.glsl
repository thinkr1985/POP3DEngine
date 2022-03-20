#version 410 core

layout (location = 0) in vec3 vertexPosition;
layout (location = 1) in vec3 vertexColor;
layout (location = 2) in vec2 vertexUV;
layout (location = 3) in vec3 vertexNormals;

out vec3 fragmentColor;
out vec3 normalMap;
out vec2 outTexCoords;
out vec3 lightColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 vertexLightColor;

void main()
{
    gl_Position = projection * model * vec4(vertexPosition, 1.0);
    fragmentColor = vertexColor;
    outTexCoords = vertexUV;
    normalMap = vertexNormals;
    lightColor = vertexLightColor;
}

