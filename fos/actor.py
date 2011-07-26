import numpy as np

from pyglet.gl import *

from PySide.QtOpenGL import QGLShader, QGLShaderProgram
from PySide.QtGui import QMatrix4x4, QVector3D

from vsml import vsml
from .shader.lib import *

class Actor(object):

    def __init__(self):

        # is this actor currently visible
        self.visible = True

        # is this actor currently selected
        self.selected = False

        # affine transformation of the actor
        # relative to the Region it is associated with
        self.transformation = None

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False


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

class ShaderActor(Actor):
    def __init__(self):
        """ Only create this actor of a valid OpenGL context exists
        """
        super(ShaderActor, self).__init__()

        self.program = get_shader_program( "propagate", "120" )
        
        self.aPosition = self.program.attributeLocation("aPosition")
        self.aColor = self.program.attributeLocation("aColor")
        self.projMatrix = self.program.uniformLocation("projMatrix")
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")

        # TODO: retrieve tuple array row-major order QMatrix4x4(vsml.get_projection())
        # VBO: http://www.songho.ca/opengl/gl_vbo.html
        # http://www.opengl.org/wiki/Tutorial2:_VAOs,_VBOs,_Vertex_and_Fragment_Shaders_%28C_/_SDL%29
        
        self.tri = ( 60.0,  10.0,  0.0, 110.0, 110.0, 0.0, 10.0,  110.0, 0.0)

        self.mode = GL_LINES
        self.type = GL_UNSIGNED_INT

        #self.vertices = np.array( [ [0,0,0],[10,10,0]], dtype = np.float32 )
        #self.connectivity = np.array( [ 0, 1], dtype = np.uint32 )


        self.vertices = np.array( [ [0,0,0],
                           [5,5,0],
                           [5,10,0],
                           [10,5,0]], dtype = np.float32 )

        self.connectivity = np.array( [ 0, 1, 1, 2, 1, 3 ], dtype = np.uint32 ).ravel()

        self.colors = np.array( [ [0, 0, 1, 1],
                           [1, 0, 1, 1],
                           [0, 0, 1, 0.5],
                           [1.0, 0.4, 1, 0.5]] , dtype = np.float32 )


        self.vertices_ptr = self.vertices.ctypes.data
        self.connectivity_ptr = self.connectivity.ctypes.data
        self.connectivity_nr = self.connectivity.size
        self.colors_ptr = self.colors.ctypes.data

        #self.vertex_vbo = GLuint(0)
        #glGenBuffers(1, self.vertex_vbo)
        #glBindBuffer(GL_ARRAY_BUFFER_ARB, self.vertex_vbo)
        #glBufferData(GL_ARRAY_BUFFER_ARB, 4 * self.vertices.size, self.vertices_ptr, GL_STATIC_DRAW)
        #glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, 0)

        #self.indices_vbo = GLuint(0)
        #glGenBuffers(1, self.indices_vbo)
        #glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_vbo)
        # uint32 has 4 bytes
        #glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * self.indices_nr, self.indices_ptr, GL_STATIC_DRAW)


    def draw(self):
        
        print "the draw"

        #glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)
        glDrawElements(GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, self.connectivity_ptr)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        #print "d"
        #glPopMatrix()
        
    def draw1(self):
        
        print "draw"
        self.program.bind()

        self.program.setUniformValueArray( self.projMatrix,
            QMatrix4x4( tuple(vsml.projection.T.ravel().tolist()) ),
            16 )

        self.program.setUniformValueArray( self.modelviewMatrix,
            QMatrix4x4( tuple(vsml.modelview.T.ravel().tolist()) ),
            16 )

        #glPushMatrix()
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnableClientState(GL_VERTEX_ARRAY)
       # print "a"
        #glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        #print "b"
        #glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)
        glDrawElements(GL_LINES, self.indices_nr, GL_UNSIGNED_INT, self.indices_ptr)
        #print "c"
        #glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        #print "d"
        #glPopMatrix()


    def draw_vbo(self):
        
        # http://www.pyside.org/docs/pyside/PySide/QtOpenGL/QGLShaderProgram.html
        self.program.enableAttributeArray( self.aPosition )

        self.program.setUniformValueArray( self.projMatrix,
            QMatrix4x4( tuple(vsml.projection.T.ravel().tolist()) ),
            16 )

        self.program.setUniformValueArray( self.modelviewMatrix,
            QMatrix4x4( tuple(vsml.modelview.T.ravel().tolist()) ),
            16 )

        glBindBuffer(GL_ARRAY_BUFFER_ARB, self.vertex_vbo)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, 0)

        # bind the indices buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_vbo)

        glDrawElements(self.mode,self.indices_nr,self.type,0)


        #self.program.setUniformValueArray( self.aPosition,
#            *self.tri, len(self.tri) )


        #glDrawArrays(GL_TRIANGLES, 0, 3)

        self.program.disableAttributeArray( self.aPosition )

    

class Axes(Actor):

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

class TriangleActor(Actor):
    def __init__(self):
        super(TriangleActor, self).__init__()

    def draw(self):
        glColor3f(1.0, 0.0, 1.0)
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


class PolygonLines(Actor):

    def __init__(self,
                 vertices,
                 connectivity,
                 colors = None):
        """ A PolygonLines, a generic irregular data structure

        vertices : Nx3
            Local 3D coordinates x,y,z
        connectivity : Mx2
            Polygon line topology
        colors : Nx4 or 1x4, float [0,1]
            Color per vertex

        """
        super(PolygonLines, self).__init__()

        self.vertices = vertices
        self.connectivity = connectivity.ravel()

        # this coloring section is for per/vertex color
        if colors is None:
            # default colors for each line
            self.colors = np.array( [[1.0, 0.0, 0.0, 1.0]], dtype = np.float32).repeat(len(self.vertices), axis=0)
        else:
            # colors array is half the size of the connectivity array
            assert( len(self.vertices) == len(colors) )
            self.colors = colors

        # create pointers
        self.vertices_ptr = self.vertices.ctypes.data
        self.connectivity_ptr = self.connectivity.ctypes.data
        self.connectivity_nr = self.connectivity.size
        self.colors_ptr = self.colors.ctypes.data

    def draw(self):
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)
        glDrawElements(GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, self.connectivity_ptr)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glPopMatrix()