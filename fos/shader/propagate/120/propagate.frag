varying vec4 aColor;

void main()
{
    gl_FragColor = vec4(aColor.x, aColor.y, aColor.z, aColor.w);
}

