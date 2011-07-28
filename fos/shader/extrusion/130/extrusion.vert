#version 130

in vec3 aPosition;
in vec4 aColor;

uniform mat4 projMatrix;
uniform mat4 modelviewMatrix;

// uniform ivec2 viewportWH;

out vec4 vColor;
out float vWidth;

uniform samplerBuffer radiusSampler;

void main()
{
    vWidth = texelFetch( radiusSampler, gl_VertexID ).x;
    gl_Position = projMatrix * modelviewMatrix * vec4(aPosition.x , aPosition.y, aPosition.z, 1.0);
    vColor = vec4(aColor.x , aColor.y , aColor.z, aColor.w);
}
