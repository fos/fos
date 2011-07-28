
from PySide.QtOpenGL import QGLShader, QGLShaderProgram

import os.path as op

def get_shader_code(name, version, shadertype ):
    """ Returns the shader as a string """
    
    if shadertype == "frag":
        ext = ".frag"
    elif shadertype == "vert":
        ext = ".vert"
    elif shadertype == "geom":
        ext = ".geom"

    fname = op.join( op.dirname(__file__), name, version, name + ext )
    if op.exists( fname ):
        with open(fname) as f:
            return f.read()
    else:
        return None

def get_shader_program(name, version):
    """ Returns a QGLShaderProgram for a specific version.
    Bound and linked.
    """

    vert = get_shader_code( name, version, "vert" )
    frag = get_shader_code( name, version, "frag" )
    geom = get_shader_code( name, version, "geom" )

    program = QGLShaderProgram()

    if frag:
        fshader = QGLShader(QGLShader.Fragment)
        fshader.compileSourceCode(frag)
        program.addShader(fshader)

    if vert:
        vshader = QGLShader(QGLShader.Vertex)
        vshader.compileSourceCode(vert)
        program.addShader(vshader)

    if geom:
        gshader = QGLShader(QGLShader.Geometry)
        gshader.compileSourceCode(geom)
        program.addShader(gshader)

    print "link"
    program.link()
    print "bind"
    program.bind()

    return program
