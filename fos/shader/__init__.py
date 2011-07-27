from shaders import Shader
from .lib import *
from pyglet.gl import *

def get_vary_line_width_shader():
    return Shader( [get_shader_code('extrusion', '130', 'vert')],
                   [get_shader_code('extrusion', '130', 'frag')],
                   [get_shader_code('extrusion', '130', 'geom'), GL_LINES, GL_TRIANGLE_STRIP, 6]
                  )