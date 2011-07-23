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
        in vec4 vColor; void main(){
        // gl_FragColor = vec4(vColor.x, vColor.y, vColor.z,  vColor.w);
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
         }"""

class Actor(object):

    def __init__(self):

        # is this actor currently visible
        self.visible = True

        # is this actor currently selected
        self.selected = False

        # affine transformation of the actor
        # relative to the Region it is associated with
        self.transformation = None

class DynamicActor(Actor):

    def __init__(self):
        """ Dynamic actor either implemented as a list
        of static actors, or with data arrays having a temporal dimension
        """

        # is the actor currently playing
        self.playing = False

        # the reference to the first time frame
        self.current_time_frame = 0

    def next(self):
        """ Next time step
        """
        pass

    def previous(self):
        """ Previous time step
        """
        pass

    def play(self):
        """ Start playing
        """
        pass

    def pause(self):
        """ Pause playing
        """
        pass

    def stop(self):
        """ Stop playing and reset to start
        """
        pass
        



class ScaleBar(object):

    def __init__(self):
        """ ScaleBar actor with text
        """
        pass

class AABB(object):

    def __init__(self):
        """ Axis Aligned Bounding Box
        """
        pass

class CartesianCoordianteSystemAxes(object):

    def __init__(self):
            """ Actor displaying the three cartesian, orthogonal coordinates
            """
            pass

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

        self.tri = ( 60.0,  10.0,  0.0, 110.0, 110.0, 0.0, 10.0,  110.0, 0.0)


    def draw(self):

        # http://www.pyside.org/docs/pyside/PySide/QtOpenGL/QGLShaderProgram.html
        self.program.enableAttributeArray( self.aPosition )

        self.program.setUniformValueArray( self.projMatrix,
            QMatrix4x4( tuple(vsml.projection.T.ravel().tolist()) ),
            16 )

        self.program.setUniformValueArray( self.modelviewMatrix,
            QMatrix4x4( tuple(vsml.modelview.T.ravel().tolist()) ),
            16 )

        self.program.setAttributeArray( self.aPosition, self.tri, 3)

        glDrawArrays(GL_TRIANGLES, 0, 3)

        self.program.disableAttributeArray( self.aPosition )

    

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
