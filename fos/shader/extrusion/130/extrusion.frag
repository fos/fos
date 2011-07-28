#version 130

in vec4 vColor0;

void main()
{
    gl_FragColor = vec4(vColor0.x, vColor0.y, vColor0.z,  vColor0.w);
}