import numpy as np
from pyglet.gl import *

from PySide.QtGui import QMatrix4x4

from fos.shader.lib import *
from fos.vsml import vsml
from .base import *

class PolygonLinesExtruded(Actor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             colors = None,
             radius = None,
             affine = None):
        """ A PolygonLinesExtruded, composed of many (branching) polygons

        name : string
            The name of the actor
        vertices : Nx3
            3D Coordinates x,y,z
        connectivity : Mx1
            Tree topology
        colors : Nx4 or 1x4
            Per connection color
        radius : N
            Per vertex radius
        affine : 4x4
            Affine transformation of the actor

        Notes
        -----
        Only create this actor of a valid OpenGL context exists
        """
        super(PolygonLinesExtruded, self).__init__(name)
        
        self.program = get_shader_program( "extrusion", "130" )

        self.aPosition = self.program.attributeLocation("aPosition")
        self.aColor = self.program.attributeLocation("aColor")

        self.projMatrix = self.program.uniformLocation("projMatrix")
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")
        self.radiusSampler = self.program.uniformLocation("widthSampler")

        self.viewportWidth = self.program.uniformLocation("viewportWidth")
        self.viewportHeight = self.program.uniformLocation("viewportHeight")

        if affine is None:
            self.affine = np.eye(4, dtype = np.float32)
        else:
            self.affine = affine

        # unfortunately, we need to duplicate vertices if we want per line color
        self.vertices = vertices[connectivity,:]

        if radius is None:
            self.radius = np.ones( len(connectivity), dtype = np.float32 )
        else:
            radius = radius[connectivity]
            self.radius = radius.astype( np.float32 )

        # we have a simplified connectivity now
        self.connectivity = np.array( range(len(self.vertices)), dtype = np.uint32 )

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
        self.radius_ptr = self.radius.ctypes.data

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
        self.colors_vbo = GLuint(1)
        glGenBuffers(1, self.colors_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.colors.size, self.colors_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableVertexAttribArray(self.aColor)

        # for indices
        self.connectivity_vbo = GLuint(2)
        glGenBuffers(1, self.connectivity_vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)
        # uint32 has 4 bytes
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * self.connectivity_nr, self.connectivity_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        # for radius
        # create buffer object
        self.radius_vbo = GLuint(3)
        glGenBuffers(1, self.radius_vbo)
        glBindBuffer(GL_TEXTURE_BUFFER_EXT, self.radius_vbo)
        # init buffer object
        glBufferData(GL_TEXTURE_BUFFER_EXT, 4 * self.radius.size, self.radius_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_TEXTURE_BUFFER_EXT, 0)

        # texture
        from ctypes import byref
        self.radius_unit = GLuint(0)
        glGenTextures(1, byref(self.radius_unit))
        glBindTexture(GL_TEXTURE_BUFFER_EXT, self.radius_unit)
        glTexBufferEXT( GL_TEXTURE_BUFFER_EXT, GL_LUMINANCE32F_ARB, self.radius_vbo ) #    GL_RGBA32F_ARB GL_ALPHA32F_ARB
        glBindTexture(GL_TEXTURE_BUFFER_EXT, 0)

        oint = GLint(0)
        glGetIntegerv(GL_MAX_TEXTURE_BUFFER_SIZE_EXT, oint)
        #print "Max texture buffer size", oint.value

    def draw(self):

        self.program.bind()

        self.program.setUniformValueArray( self.projMatrix,
            QMatrix4x4( tuple(vsml.projection.ravel().tolist()) ),
            16 )

        self.program.setUniformValueArray( self.modelviewMatrix,
            QMatrix4x4( tuple(vsml.modelview.ravel().tolist()) ),
            16 )

        self.program.setUniformValue( self.radiusSampler, 0 )

        self.program.setUniformValue( self.viewportWidth, vsml.width )
        self.program.setUniformValue( self.viewportHeight, vsml.height )

        # http://www.pyside.org/docs/pyside/PySide/QtOpenGL/QGLShaderProgram.html
        self.program.enableAttributeArray( self.aPosition )
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
        glVertexAttribPointer(self.aPosition, 3, GL_FLOAT, GL_FALSE, 0, 0)

        glEnableVertexAttribArray(self.aColor)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo)
        glVertexAttribPointer(self.aColor, 4, GL_FLOAT, GL_FALSE, 0, 0)

        # bind the indices buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)

        glActiveTexture(GL_TEXTURE0) # do i need this?
        #glBindBuffer(GL_TEXTURE_BUFFER_EXT, self.radius_vbo)
        glBindTexture(GL_TEXTURE_BUFFER_EXT, self.radius_unit)

        glDrawElements( GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, 0 )

        self.program.disableAttributeArray( self.aPosition )
        self.program.disableAttributeArray( self.aColor )

        self.program.release()



class PolygonLines(Actor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             colors = None,
             affine = None):
        """ A PolygonLines, composed of many (branching) polygons

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
        Uses Vertex-Buffer objects and dummy shaders.
        """
        super(PolygonLines, self).__init__( name )

        self.program = get_shader_program( "propagate", "120" )

        self.aPosition = self.program.attributeLocation("aPosition")
        self.aColor = self.program.attributeLocation("bColor")

        self.projMatrix = self.program.uniformLocation("projMatrix")
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")

        if affine is None:
            self.affine = np.eye(4, dtype = np.float32)
        else:
            self.affine = affine

        # unfortunately, we need to duplicate vertices if we want per line color
        self.vertices = vertices[connectivity,:]

        # we have a simplified connectivity now
        self.connectivity = np.array( range(len(self.vertices)), dtype = np.uint32 )

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

        self.program.disableAttributeArray( self.aPosition )
        self.program.disableAttributeArray( self.aColor )

        self.program.release()
        

class PolygonLinesSimple(Actor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             colors = None,
             affine = None,
             linewidth = 3.0):
        """ A PolygonLines, composed of many (branching) polygons

        name : str
            The name of the actor
        vertices : Nx3
            3D Coordinates x,y,z
        connectivity : Mx2
            Tree topology
        colors : Nx4 or 1x4
            Per connection color
        affine : 4x4
            Affine transformation of the actor

        """
        super(PolygonLinesSimple, self).__init__( name )

        if affine is None:
            self.affine = np.eye(4, dtype = np.float32)
        else:
            self.affine = affine

        self.linewidth = linewidth
        self.vertices_orig = vertices
        self.connectivity_orig = connectivity

        # unfortunately, we need to duplicate vertices if we want per line color
        # not necessary if we assume this was done before!
        # self.vertices = vertices[connectivity.ravel(),:]
        # print "vertices new", self.vertices
        self.vertices = vertices

        # we have a simplified connectivity now
        # self.connectivity = np.array( range(len(self.vertices)), dtype = np.uint32 )
        assert( connectivity.shape[1] == 2 )
        self.connectivity = connectivity.ravel()

        # this coloring section is for per/vertex color
        if colors is None:
            # default colors for each line
            self.colors = np.array( [[1.0, 0.0, 0.0, 1.0]], dtype = np.float32).repeat(len(self.connectivity)/2, axis=0)
        else:
            # colors array is half the size of the connectivity array
            assert( len(self.connectivity)/4 == len(colors) )
            self.colors = colors

        # we want per line color
        # duplicating the color array, we have the colors per vertex
        self.colors =  np.repeat(self.colors, 2, axis=0)
        
        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.connectivity.ctypes.data
        self.faces_nr = self.connectivity.size
        self.colors_ptr = self.colors.ctypes.data

    def set_coloralpha_all(self, alphavalue = 0.2 ):
        self.colors[:,3] = alphavalue

    def select_vertices(self, vertices_indices, value = 0.6):
        # select a subset of vertices (e.g. for a skeleton)
        self.colors[self.connectivity_orig[vertices_indices.ravel()].ravel(), 3] = value

    def draw(self):
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glLineWidth(self.linewidth)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)

        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)
        
        glDrawElements( GL_LINES, self.faces_nr, GL_UNSIGNED_INT, self.faces_ptr )
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        