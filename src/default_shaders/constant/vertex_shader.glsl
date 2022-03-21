#version 410 core

layout (location = 0) in vec3 vertexPosition;

out vec4 newColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec4 constant_color;

void main()
{
   gl_Position = projection * model * vec4(vertexPosition, 1.0);
   newColor = constant_color;
}
