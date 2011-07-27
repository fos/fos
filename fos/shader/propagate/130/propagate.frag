#version 130

in vec4 vColor;

void main()
{
    gl_FragColor = vec4(vColor.x, vColor.y, vColor.z,  vColor.w);
}
