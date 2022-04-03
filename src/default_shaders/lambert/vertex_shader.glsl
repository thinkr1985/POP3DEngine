#version 410 core

layout (location = 0) in vec3 vertexPosition;
layout (location = 1) in vec3 vertexColor;
layout (location = 2) in vec2 vertexUV;
layout (location = 3) in vec3 vertexNormal;


out vec3 fragmentNormal;
out vec2 fragmentTexCoord;
out vec3 fragmentPosition;
out vec3 fragAtmosphereColor;
out float fragAtmosphereIntensity;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 atmosphereColor;
uniform float atmosphereIntensity;

void main()
{
    gl_Position = projection * model * vec4(vertexPosition, 1.0);
    fragmentTexCoord = vertexUV;
    fragmentPosition = (model * vec4(vertexPosition, 1.0)).xyz;
    fragmentNormal = mat3(model) * vertexNormal;
    fragAtmosphereColor = atmosphereColor;
    fragAtmosphereIntensity = atmosphereIntensity;
}

