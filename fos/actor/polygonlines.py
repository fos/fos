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


class Selector(object):
    pass




class PolygonLines(Actor, Selector):

    def __init__(self,
             name,
             vertices,
             connectivity,
             connectivity_selectionID = None,
             colors = None,
             affine = None,
             linewidth = 3.0):
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

        self.vertices_orig = vertices
        self.connectivity_orig = connectivity
        self.linewidth = linewidth
        self.connectivity_selectionID_orig = connectivity_selectionID
        
        # TODO: fix API
        # unfortunately, we need to duplicate vertices if we want per line color
        #self.vertices = vertices[connectivity,:]
        #self.connectivity = np.array( range(len(self.vertices)), dtype = np.uint32 )

        self.vertices = vertices
        assert( connectivity.shape[1] == 2 )
        self.connectivity = connectivity.ravel()

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
        print "colors array", self.colors
        
        if not self.connectivity_selectionID_orig is None:
            self.connectivity_selectionID = np.repeat(self.connectivity_selectionID_orig, 2, axis=0)
            self.connectivity_selection_array = np.ones( self.colors.shape, dtype = np.float32 )

            # selectionId to color
            def con( ID ):
                r = (ID & 0x00FF0000) >> 16
                g = (ID & 0x0000FF00) >> 8
                b = (ID & 0x000000FF)
                return r,g,b

            for i in range(len(self.colors)):
                self.connectivity_selection_array[i,:3] = np.array(con(self.connectivity_selectionID[i]))/255.0

            print "selection array", self.connectivity_selection_array
            self.connectivity_selection_array_ptr = self.connectivity_selection_array.ctypes.data

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
        self.colors_vbo = (GLuint * 2)(0)
        glGenBuffers(2, self.colors_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
        glBufferData(GL_ARRAY_BUFFER, 4 * self.colors.size, self.colors_ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        if not self.connectivity_selectionID_orig is None:
            print "bind selection"
            glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[1])
            glBufferData(GL_ARRAY_BUFFER, 4 * self.connectivity_selection_array.size, self.connectivity_selection_array_ptr, GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

        glDisableVertexAttribArray(self.aColor)

        # for indices
        self.connectivity_vbo = GLuint(0)
        glGenBuffers(1, self.connectivity_vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)
        # uint32 has 4 bytes
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * self.connectivity_nr, self.connectivity_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        # help from
        # http://groups.google.com/group/pyglet-users/browse_thread/thread/71cb064ee1f11714
        # http://www.gamedev.net/page/resources/_//feature/fprogramming/opengl-frame-buffer-object-101-r2331
        # http://www.flashbang.se/archives/48
        
        # FBO
        self.fbo = GLuint()
        # create our frame buffer
        glGenFramebuffersEXT(1, self.fbo)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.fbo)

        # //create the colorbuffer texture and attach it to the frame buffer
        self.color_tex = GLuint()
        self.depth_rb = GLuint()
        self.color_tex_ptr = GLuint(0)
        # http://www.songho.ca/opengl/gl_fbo.html
        # if renderbuffer objects, no texture required ?
        
        glGenTextures(1, self.color_tex);
        glBindTexture(GL_TEXTURE_2D, self.color_tex)
        #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # TODO check
        # or glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8,  width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
        # Thanks to pyglet for the blank

        #blank = (GLubyte * ( vsml.width * vsml.height * 4))()
        #glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, vsml.width, vsml.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, blank )

        blank = (GLfloat * ( vsml.width * vsml.height * 4))()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, vsml.width, vsml.height, 0, GL_RGBA, GL_FLOAT, blank )


        # tex = image.Texture.create_for_size(gl.GL_TEXTURE_2D, w, h, gl.GL_RGBA) -> check
        
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT,GL_COLOR_ATTACHMENT0_EXT,GL_TEXTURE_2D, self.color_tex, 0)

        # // create a render buffer as our depthbuffer and attach it
        #glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, self.depth_rb)
        #glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT,GL_DEPTH_COMPONENT24, vsml.width, vsml.height)
        #glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT,GL_RGB, vsml.width, vsml.height)
        #glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT,GL_DEPTH_ATTACHMENT_EXT,GL_RENDERBUFFER_EXT, self.depth_rb)

        status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
        assert status == GL_FRAMEBUFFER_COMPLETE_EXT

        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

    def cleanup(self):
        # clean up
        glDeleteFramebuffersEXT(1, self.fbo)

    def set_coloralpha_all(self, alphavalue = 0.2 ):
        print self.colors
        self.colors[:,3] = alphavalue

        # TODO: FIX also need to update FBO colors VBO ?
        
        # update VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
        glBufferData(GL_ARRAY_BUFFER, 4 * self.colors.size, self.colors_ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        print self.colors

    def select_vertices(self, vertices_indices, value = 0.6):
        # select a subset of vertices (e.g. for a skeleton)
        self.colors[self.connectivity_orig[vertices_indices.ravel()].ravel(), 3] = value

        # TODO: FIX also need to update FBO colors VBO ?

        # update VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
        glBufferData(GL_ARRAY_BUFFER, 4 * self.colors.size, self.colors_ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def pick(self, x, y):
        if self.connectivity_selectionID_orig is None:
            print "no connectivity ids for polylines given"
            return
        
        print "pick polylines", x, y

        print "vsml", vsml.width, vsml.height


        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.fbo)



        glPushAttrib(GL_VIEWPORT_BIT)
        glViewport(0, 0, vsml.width, vsml.height)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        #glDisable(GL_BLEND)
        #glDisable(GL_MULTISAMPLE)
        glLineWidth(self.linewidth)
        
        # FBO render pass, need to use the selection id color array
        ################

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
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[1])
        glVertexAttribPointer(self.aColor, 4, GL_FLOAT, GL_FALSE, 0, 0)

        # bind the indices buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)

        glDrawElements( GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, 0 )

        self.program.disableAttributeArray( self.aPosition )
        self.program.disableAttributeArray( self.aColor )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        self.program.release()
        ############

        a = (GLfloat * 4)(0)
        glReadPixels(x, y, 1, 1, GL_RGBA, GL_FLOAT, a)
        print a[0], a[1], a[2], a[3]
        ID = (int(a[0]*255) << 16) | (int(a[1]*255) << 8) | int(a[2]*255)
        print "id found", ID

        glPopAttrib()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        return ID

    def draw(self):

        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        
        glLineWidth(self.linewidth)

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
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
        glVertexAttribPointer(self.aColor, 4, GL_FLOAT, GL_FALSE, 0, 0)

        # bind the indices buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)

        glDrawElements( GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, 0 )

        self.program.disableAttributeArray( self.aPosition )
        self.program.disableAttributeArray( self.aColor )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        self.program.release()
        

class PolygonLinesSimple(Actor, Selector):

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
            assert( len(self.connectivity)/2 == len(colors) )
            self.colors = colors

        # we want per line color
        # duplicating the color array, we have the colors per vertex
        self.colors =  np.repeat(self.colors, 2, axis=0)
        
        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.connectivity.ctypes.data
        self.faces_nr = self.connectivity.size
        self.colors_ptr = self.colors.ctypes.data

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
        