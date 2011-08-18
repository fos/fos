#version 120

// matrices
uniform mat4 projMatrix;
uniform mat4 modelviewMatrix;

// bColor is selectionID
attribute vec4 bColor;
varying vec4 aColor;
attribute vec3 aPosition;

void main()
{
    aColor = bColor; // vec4(1.0, 0,0,0);
    gl_Position = projMatrix * modelviewMatrix * vec4(aPosition.x , aPosition.y, aPosition.z, 1.0);
}

