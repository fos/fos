#version 130

in vec3 aPosition;
// in vec4 aColor; // This is the per-vertex color

// matrices
uniform mat4 projMatrix;
uniform mat4 modelviewMatrix;

// out vec4 vColor;   // This is the output to the geometry shader

void main()
{

        // vColor = vec4(aColor.x , aColor.y , aColor.z, aColor.w); // Pass from VS -> GS
        gl_Position = projMatrix * modelviewMatrix * vec4(aPosition.x , aPosition.y, aPosition.z, 1.0);
        //gl_Position = projMatrix * modelviewMatrix * gl_Vertex;

}
