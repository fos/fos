#version 330

layout (location = 0) in vec4 aPosition;
layout (location = 1) in vec4 aColor;

uniform mat4 projMatrix;
uniform mat4 modelviewMatrix;

smooth out vec4 theColor;

void main()
{
    gl_Position = projMatrix * modelviewMatrix * vec4(aPosition.x , aPosition.y, aPosition.z, 1.0);
    theColor = aColor;
}
