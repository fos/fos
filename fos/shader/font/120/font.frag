uniform sampler2D texture;
uniform vec2 pixel;
varying float m;
void main() {
    vec2 uv    = gl_TexCoord[0].xy;
    vec4 current = texture2D(texture, uv);
    vec4 previous= texture2D(texture, uv+vec2(-1,0)*pixel);
    float r = current.r;
    float g = current.g;
    float b = current.b;
    float a = current.a;
    if( m <= 0.333 )
    {
        float z = m/0.333;
        r = mix(current.r, previous.b, z);
        g = mix(current.g, current.r,  z);
        b = mix(current.b, current.g,  z);
    }
    else if( m <= 0.666 )
    {
        float z = (m-0.33)/0.333;
        r = mix(previous.b, previous.g, z);
        g = mix(current.r,  previous.b, z);
        b = mix(current.g,  current.r,  z);
    }
   else if( m < 1.0 )
    {
        float z = (m-0.66)/0.334;
        r = mix(previous.g, previous.r, z);
        g = mix(previous.b, previous.g, z);
        b = mix(current.r,  previous.b, z);
    }
    //gl_FragColor = vec4(r,g,b,a);
    gl_FragColor = vec4(1.0,0.0,0.0,0.5);
}