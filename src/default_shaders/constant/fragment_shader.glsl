#version 410 core

layout(location = 0) out vec4 FragColor;
in vec4 newColor;

void main()
{
    FragColor = newColor;
}
