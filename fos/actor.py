from pyglet.gl import *
from PySide.QtOpenGL import QGLShader, QGLShaderProgram

from PySide.QtGui import QMatrix4x4

from vsml import vsml

vert = """#version 130
            in vec3 aPosition;
            in vec4 aColor; // This is the per-vertex color
            // matrices
            uniform mat4 projMatrix;
            uniform mat4 modelviewMatrix;
            out vec4 vColor;   // This is the output to the geometry shader
            void main()
            {
                    vColor = vec4(aColor.x , aColor.y , aColor.z, aColor.w); 
                    gl_Position = projMatrix * modelviewMatrix * vec4(aPosition.x , aPosition.y, aPosition.z, 1.0);
            }"""
frag = """#version 130
        in vec4 vColor; void main(){    gl_FragColor = vec4(vColor.x, vColor.y, vColor.z,  vColor.w); }"""


class ShaderActor(object):
    def __init__(self):
        """ Only create this actor of a valid OpenGL context exists
        """

        shader = QGLShader(QGLShader.Fragment)
        shader.compileSourceCode(frag)

        self.program = QGLShaderProgram()
        self.program.addShader(shader)

        shader = QGLShader(QGLShader.Vertex)
        shader.compileSourceCode(vert)

        self.program.addShader(shader)

        self.program.link()
        self.program.bind()

        self.aPosition = self.program.attributeLocation("aPosition")
        self.aColor = self.program.attributeLocation("aColor")
        self.projMatrix = self.program.uniformLocation("projMatrix")
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")

        # TODO: retrieve tuple array row-major order QMatrix4x4(vsml.get_projection())


    def draw(self):

        # http://www.pyside.org/docs/pyside/PySide/QtOpenGL/QGLShaderProgram.html
        self.program.enableAttributeArray( self.aPosition )
        
        #program.setAttributeArray(vertexLocation, triangleVertices, 3)
        #program.setUniformValue(matrixLocation, pmvMatrix)
        #program.setUniformValue(colorLocation, color)
        #glDrawArrays(GL_TRIANGLES, 0, 3)
        #self.program.disableAttributeArray(vertexLocation)


    

class Axes(object):

    def __init__(self, scale = 10.0):
        """ Draw three axes
        """
        super(Axes, self).__init__()

        self.scale = scale

    def draw(self):

        #glPushMatrix()

        glLineWidth(2.0)

        glBegin (GL_LINES)
        # x axes
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(self.scale,0.0,0.0)
        # y axes
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(0.0,self.scale,0.0)
        # z axes
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(0.0,0.0,self.scale)
        glEnd()

        #glPopMatrix()

class TriangleActor(object):
    def __init__(self):
        pass

    def draw(self):

        glBegin(GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)

        glEnd()

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):

        glVertex3d(x1, y1, -0.05)
        glVertex3d(x2, y2, -0.05)
        glVertex3d(x3, y3, -0.05)
        glVertex3d(x4, y4, -0.05)

        glVertex3d(x4, y4, +0.05)
        glVertex3d(x3, y3, +0.05)
        glVertex3d(x2, y2, +0.05)
        glVertex3d(x1, y1, +0.05)
