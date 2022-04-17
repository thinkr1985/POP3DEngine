#version 410 core

layout(location = 0) out vec4 FragColor;
layout(location = 1) out vec3 currentCameraPosition;

in vec4 newColor;
in vec4 newVertexColor;

uniform vec3 cameraPosition;

void main()
{
    FragColor = newColor;
    currentCameraPosition = cameraPosition;
}
