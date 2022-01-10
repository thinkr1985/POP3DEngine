#version 330 core

in vec4 newColor;

layout(location = 0) out vec4 outColor;


void main()
{
    outColor = newColor;
}
