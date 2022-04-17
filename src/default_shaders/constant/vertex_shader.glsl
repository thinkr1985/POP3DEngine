#version 410 core

layout (location = 0) in vec3 vertexPosition;
layout (location = 1) in vec3 vertexColor;

out vec4 newColor;
out vec3 newVertexColor;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform vec4 constant_color;

void main()
{
   gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
   newColor = constant_color;
   newVertexColor = vertexColor;
}
