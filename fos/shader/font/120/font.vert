// matrices
uniform mat4 projMatrix;
uniform mat4 modelviewMatrix;

uniform sampler2D texture;
uniform vec2 pixel;
attribute float modulo;
varying float m;
void main() {
    gl_FrontColor = gl_Color;
    gl_TexCoord[0].xy = gl_MultiTexCoord0.xy;
    //gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_Position = projMatrix * modelviewMatrix * gl_Vertex;

    m = modulo;
}