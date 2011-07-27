#version 110
#extension GL_EXT_gpu_shader4 : enable    //Include support for this extension, which defines usampler2D

varying vec4 vColor0; // Input from GS
//uniform sampler1D Texture0;

void main()
{
    gl_FragColor = vec4(vColor0.x, vColor0.y, vColor0.z,  vColor0.w);
}
