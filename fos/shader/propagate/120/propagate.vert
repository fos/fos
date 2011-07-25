#version 120

// matrices
uniform mat4 projMatrix;
uniform mat4 modelviewMatrix;

void main()
{   
    //gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    //gl_Position = ftransform();
    gl_Position = projMatrix * modelviewMatrix * gl_Vertex;
}

