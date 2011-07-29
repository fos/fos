#version 130
#extension GL_EXT_geometry_shader4 : enable

layout(lines) in;
layout(triangle_strip, max_vertices=6) out;

uniform int viewportWidth;
uniform int viewportHeight;

in vec4 vColor[2]; // One for each vertex in the line
in float vWidth[2]; // one width for each vertex in the line
out vec4 vColor0; // Output color, pass from GS -> FS

// Authors
// Dan Ginsburg & Stephan Gerhard

//
//  clipCoord - incoming clipCoord, output from vertex shader
//  viewport - arguments to glViewport(x,y,width,height)
//  winCoord - [output] Window coordinates
//
void projectCoord(vec4 clipCoord, ivec4 viewport, out vec3 winCoord)
{
    // The clipCoord is already multiplied by the MVP, so we can just do
    // the second half of gluProject()
    vec3 inCoord = clipCoord.xyz / clipCoord.w;
    inCoord = inCoord.xyz * 0.5 + 0.5;

    // Map x/y to viewport
    // The viewport is just the four arguments to glViewport()
    inCoord.x = inCoord.x * viewport.z + viewport.x;
    inCoord.y = inCoord.y * viewport.w + viewport.y;

    winCoord = inCoord;
}

//
//  winCoord - incoming winCoord, unproject back to clip-space
//  w - this should be (incomingClipCoord.w)
//  viewport - arguments to glViewport(x,y,width,height)
//  clipCoord - [output] Clip coordinates
//
void unProjectCoord(vec3 winCoord, float w, ivec4 viewport, out vec4 clipCoord)
{
    vec4 inCoord = vec4(winCoord.xyz, 1.0);

    // Map x and y from window coordinates
    inCoord.x = (inCoord.x - viewport.x) / viewport.z;
    inCoord.y = (inCoord.y - viewport.y) / viewport.w;

    // Map to range -1 to 1
    inCoord.xyz = inCoord.xyz * 2.0 - 1.0;

    // Multiply by w to undo perspective division
    inCoord.xyz = inCoord.xyz * w;

    clipCoord = vec4(inCoord.xyz, w);
}


void main()
{
    float extrude1 = vWidth[0];
    float extrude2 = vWidth[1];

    vec3 winCoord0;
    vec3 winCoord1;
    vec3 computedWinCoord0;
    vec3 computedWinCoord1;
    vec3 computedWinCoord2;
    vec3 computedWinCoord3;

    vec4 clipCoord0;
    vec4 clipCoord1;
    vec4 clipCoord2;
    vec4 clipCoord3;
    vec3 dir;
    vec2 perp;

    ivec4 viewport = ivec4(0, 0, viewportWidth, viewportHeight);

    // viewport should be a uniform ivec4 that you set
    projectCoord(gl_PositionIn[0], viewport, winCoord0);
    projectCoord(gl_PositionIn[1], viewport, winCoord1);

    // Now do the quad extrusion in screen-coordinates, don't have time to work this out now, if you need help with it let me know...
    // using winCoord0

    dir = normalize(winCoord1 - winCoord0);

    perp = vec2(-dir.y, dir.x);

    // extrude in both directions
    computedWinCoord0.xyz = vec3(winCoord0.xy + perp.xy * extrude1, winCoord0.z );
    computedWinCoord1.xyz = vec3(winCoord0.xy - perp.xy * extrude1, winCoord0.z );
    computedWinCoord2.xyz = vec3(winCoord1.xy - perp.xy * extrude2, winCoord1.z );
    computedWinCoord3.xyz = vec3(winCoord1.xy + perp.xy * extrude2, winCoord1.z );

    // Unproject the window-coordinates BACK to clip-space
    unProjectCoord(computedWinCoord0, gl_PositionIn[0].w, viewport, clipCoord0);
    unProjectCoord(computedWinCoord1, gl_PositionIn[0].w, viewport, clipCoord1);
    unProjectCoord(computedWinCoord2, gl_PositionIn[1].w, viewport, clipCoord2);
    unProjectCoord(computedWinCoord3, gl_PositionIn[1].w, viewport, clipCoord3);

    // (you'll do one of the above for each computed coordinate
    // Now you can pass those along as clip-space coords for the frag shader
    // first triangle
    gl_Position = clipCoord0; vColor0 = vColor[0]; EmitVertex();
    gl_Position = clipCoord1; vColor0 = vColor[0]; EmitVertex();
    gl_Position = clipCoord2; vColor0 = vColor[1]; EmitVertex();
    EndPrimitive();
    
    // second triangle
    gl_Position = clipCoord0; vColor0 = vColor[0]; EmitVertex();
    gl_Position = clipCoord2; vColor0 = vColor[1]; EmitVertex();
    gl_Position = clipCoord3; vColor0 = vColor[1]; EmitVertex();
    EndPrimitive();

}