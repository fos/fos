import numpy as np
from pyglet.gl import *
from .base import *
from fos.actor.primitives import *
from fos.actor.scatter import *

from PySide.QtGui import QMatrix4x4

from fos.shader.lib import *
from fos.vsml import vsml

class Microcircuit(Actor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             vertices_labels,
             connectivity_labels,
             affine = None):
        """ A Microcircuit actor with skeletons, connectors and incoming
        and outgoing connectivity

        name : str
            The name of the actor
        vertices : Nx3
            3D Coordinates x,y,z
        connectivity : Mx1
            Tree topology
        colors : Nx4 or 1x4
            Per connection color
        affine : 4x4
            Affine transformation of the actor

        Notes
        -----
        Only create this actor when a valid OpenGL context exists.
        Uses Vertex-Buffer objects and propagate shaders.
        """
        super(Microcircuit, self).__init__( name )

        # TODO: simplify by reusing the PolygonLines actor in here!
        self.program = get_shader_program( "propagate", "130" )

        self.aPosition = self.program.attributeLocation("aPosition")
        self.aColor = self.program.attributeLocation("aColor")

        self.projMatrix = self.program.uniformLocation("projMatrix")
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")

        if affine is None:
            self.affine = np.eye(4, dtype = np.float32)
        else:
            self.affine = affine

        # TODO: hard-coded values
        con_skeleton = 1
        con_pre = 2
        con_post = 3

        # use the connectivity labels to extract the connectivity for the skeletons
        self.vertices = vertices[ connectivity[np.where(connectivity_labels == con_skeleton)[0]].ravel() ]
        
        # we have a simplified connectivity now
        self.connectivity = np.array( range(len(self.vertices)), dtype = np.uint32 )

        # extract the pre connectivity and create cones
        preloc = vertices[ connectivity[np.where(connectivity_labels == con_pre)[0]].ravel() ]
        p1 = preloc[::2, :]
        p2 = preloc[1::2, :]
        r1 = np.ones( len(preloc/2), dtype = np.float32 ) * 0.2
        r2 = np.zeros( len(preloc/2), dtype = np.float32 )
        self.pre_actor = ScatterCylinder( "PreConnector", p1, p2, r1, r2, resolution = 8 )

        # extract the post connectivity and create cones
        postloc = vertices[ connectivity[np.where(connectivity_labels == con_post)[0]].ravel() ]
        p1 = postloc[::2, :]
        p2 = postloc[1::2, :]
        r1 = np.zeros( len(postloc/2), dtype = np.float32 )
        r2 = np.ones( len(postloc/2), dtype = np.float32 ) * 0.2
        self.post_actor = ScatterCylinder( "PostConnector", p1, p2, r1, r2, resolution = 8 )
        
        colors = None

        # this coloring section is for per/vertex color
        if colors is None:
            # default colors for each line
            self.colors = np.array( [[1.0, 0.0, 0.0, 1.0]], dtype = np.float32).repeat(len(self.connectivity)/2, axis=0)
        else:
            # colors array is half the size of the connectivity array
            assert( len(self.connectivity)/2 == len(colors) )
            self.colors = colors

        # we want per line color
        # duplicating the color array, we have the colors per vertex
        self.colors =  np.repeat(self.colors, 2, axis=0)

        self.vertices_ptr = self.vertices.ctypes.data
        self.connectivity_ptr = self.connectivity.ctypes.data
        self.connectivity_nr = self.connectivity.size
        self.colors_ptr = self.colors.ctypes.data

        # for vertices location
        glVertexAttribPointer(self.aPosition, 3, GL_FLOAT, GL_FALSE, 0, 0)
        self.vertex_vbo = GLuint(0)
        glGenBuffers(1, self.vertex_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.vertices.size, self.vertices_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableVertexAttribArray(self.aPosition)

        # for colors
        glVertexAttribPointer(self.aColor, 4, GL_FLOAT, GL_FALSE, 0, 0)
        self.colors_vbo = GLuint(0)
        glGenBuffers(1, self.colors_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.colors.size, self.colors_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableVertexAttribArray(self.aColor)

        # for indices
        self.connectivity_vbo = GLuint(0)
        glGenBuffers(1, self.connectivity_vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)
        # uint32 has 4 bytes
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * self.connectivity_nr, self.connectivity_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def draw(self):

        self.pre_actor.draw()
        self.post_actor.draw()

        self.program.bind()

        # we just retrieve the matrices from vsml. they are
        # updated from the Region's transformation
        self.program.setUniformValueArray( self.projMatrix,
            QMatrix4x4( tuple(vsml.projection.ravel().tolist()) ),
            16 )

        self.program.setUniformValueArray( self.modelviewMatrix,
            QMatrix4x4( tuple(vsml.modelview.ravel().tolist()) ),
            16 )

        # http://www.pyside.org/docs/pyside/PySide/QtOpenGL/QGLShaderProgram.html
        glEnableVertexAttribArray( self.aPosition )
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
        glVertexAttribPointer(self.aPosition, 3, GL_FLOAT, GL_FALSE, 0, 0)

        glEnableVertexAttribArray(self.aColor)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo)
        glVertexAttribPointer(self.aColor, 4, GL_FLOAT, GL_FALSE, 0, 0)

        # bind the indices buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)

        glDrawElements( GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, 0 )

        # required, otherwise the other draw commands do not work
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        self.program.disableAttributeArray( self.aPosition )
        self.program.disableAttributeArray( self.aColor )

        self.program.release()
