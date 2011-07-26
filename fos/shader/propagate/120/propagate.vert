#version 120

// matrices
uniform mat4 projMatrix;
uniform mat4 modelviewMatrix;

void main()
{   
    gl_Position = projMatrix * modelviewMatrix * gl_Vertex;
}

