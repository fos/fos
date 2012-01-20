import numpy as np
from pyglet.gl import *

from PySide.QtGui import QMatrix4x4

from fos.shader.lib import *
from fos.vsml import vsml
from .base import *
import fos.util

DEBUG=False

class Skeleton(Actor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             connectivity_ID = None,
             connectivity_colors = None,
             connectivity_radius = None,
             extruded = False,
             linewidth = 2.0,
             useva = True):
        """ A skeleton focused on connectivity

        Parameters
        ----------
        vertices : array, shape (N,3)
        connectivity : array, shape (M,2)
        connectivity_ID : array, shape (M,)
        connectivity_colors : array, shape (M,4)
        connectivity_radius : array, shape (M,)

        """
        super(Skeleton, self).__init__( name )

        self.useva = useva

        self.vertices = vertices
        self.connectivity = connectivity
        self.radius = connectivity_radius
        self.colors = connectivity_colors
        self.extruded = extruded
        self.linewidth = linewidth
        self.ID = connectivity_ID
        if self.ID is None:
            self.enable_picking = False
        else:
            if self.useva:
                # force disable picking when using vertex arrays
                self.enable_picking = True
            else:
                self.enable_picking = True
        self.global_deselect_alpha = 0.2
        self.global_select_alpha = 1.0
        self.current_selection = []

        assert( len(connectivity) == connectivity.shape[0] )
        M = len(connectivity)
        N = len(vertices)

        # setting default values when not existing
        if self.colors is None:
            self.colors = np.ones( (M,4), dtype = np.float32 )
            # make it yellow
            self.colors[:,2] = 0.0
            
        if self.radius is None:
            self.radius = np.ones( (M,1), dtype = np.float32 )

        # setup the shader
        if self.extruded and not self.useva:
            if gl_info.have_version(3,0):
                self._setup_shader_extruded()
            else:
                raise Exception("Need at least OpenGL 3.0 for extrusion shaders")
        else:
            if not self.useva:
                self._setup_shader_lines()

        # duplicate arrays
        self._duplicate_arrays()

        # create the pointers
        self._setup_pointers()

        # if picking enabled, setup colors_pick array and FBO
        if self.enable_picking:
            self.colors_pick, self.colors_pick_ptr = \
                self._setup_colors_pick( self.colors_draw.shape, self.ID_draw )

        # bind buffers
        if not self.useva:
            self._bind_buffer()

        if self.enable_picking:
            self._create_fbo()

        # overwrite draw and pick functions
        if self.extruded and not self.useva:
            self.draw = self._draw_extruded
            if self.enable_picking:
                self.pick = self._pick_extruded
        else:
            if self.useva:
                self.draw = self._draw_va
                if self.enable_picking:
                    self.pick = self._pick_lines_va
            else:
                self.draw = self._draw_lines
                if self.enable_picking:
                    self.pick = self._pick_lines


    def update_colors(self, connectivity_colors):
        """ Update connectivity color array

        If shape (M,4), replace array, if shape (M,3) only
        update color values but keep alpha value
        """
        assert( len(self.colors) == len(connectivity_colors) )

        if connectivity_colors.shape[1] == 4:
            # replace color values, keep alpha
            self.colors = connectivity_colors
            # duplicate array
            self.colors_draw = np.repeat(self.colors, 2, axis=0)
            # setup pointers
            self.colors_ptr = self.colors_draw.ctypes.data
            self.colors_nr = self.colors_draw.size
        else:
            # only refresh the array
            self.colors[:,:3] = connectivity_colors
            self.colors_draw[::2,:3] = connectivity_colors
            self.colors_draw[1::2,:3] = connectivity_colors

        # bind buffer
        # TODO: depending on useva?
        if not self.useva:
            glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
            glBufferData(GL_ARRAY_BUFFER, 4 * self.colors_draw.size, self.colors_ptr, GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _setup_shader_lines(self):
        self.program = get_shader_program( "propagate", "330" )

        self.aPosition = self.program.attributeLocation("aPosition")
        self.aColor = self.program.attributeLocation("bColor")

        self.projMatrix = self.program.uniformLocation("projMatrix")
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")

    def _setup_shader_extruded(self):
        self.program = get_shader_program( "extrusion", "130" )

        self.aPosition = self.program.attributeLocation("aPosition")
        self.aColor = self.program.attributeLocation("aColor")

        self.projMatrix = self.program.uniformLocation("projMatrix")
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")
        self.radiusSampler = self.program.uniformLocation("widthSampler")

        self.viewportWidth = self.program.uniformLocation("viewportWidth")
        self.viewportHeight = self.program.uniformLocation("viewportHeight")

    def _setup_pointers(self):
        self.vertices_ptr = self.vertices_draw.ctypes.data
        self.connectivity_ptr = self.connectivity_draw.ctypes.data
        self.connectivity_nr = self.connectivity_draw.size
        self.colors_ptr = self.colors_draw.ctypes.data
        self.colors_nr = self.colors_draw.size
        self.radius_ptr = self.radius_draw.ctypes.data

    def _duplicate_arrays(self):
        # duplication of values for ID, colors, radius to make it per-vertex
        # memory-intensive, but we want per-connectivity attributes
        # TODO: radius could already be per-vertex for extruded case
        self.vertices_draw, self.connectivity_draw = \
            fos.util.reindex_connectivity( self.vertices, self.connectivity )
        self.connectivity_draw = self.connectivity_draw.ravel()
        self.colors_draw = np.repeat(self.colors, 2, axis=0)
        self.radius_draw = np.repeat(self.radius, 2, axis=0)
        if self.enable_picking:
            self.ID_draw = np.repeat(self.ID, 2, axis=0)
            
    def _setup_colors_pick(self, colorsshape, ID):
        """ Setups the colors_pick array using the ID for picking
        """
        colors_pick = np.ones( colorsshape, dtype = np.float32 )

        # selectionId to color
        def con( ID ):
            r = (ID & 0x00FF0000) >> 16
            g = (ID & 0x0000FF00) >> 8
            b = (ID & 0x000000FF)
            return r,g,b

        for i in range(colorsshape[0]):
            #TODO: check dimensions
            colors_pick[i,:3] = np.array(con(ID[i])).T/255.0

        return colors_pick, colors_pick.ctypes.data

    def _pick_extruded(self, x, y):
        pass

    def _draw_extruded(self):
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
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
        glVertexAttribPointer(self.aColor, 4, GL_FLOAT, GL_FALSE, 0, 0)

        # bind the indices buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)

        #glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_BUFFER_EXT, self.radius_unit)

        glDrawElements( GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, 0 )

        self.program.disableAttributeArray( self.aPosition )
        self.program.disableAttributeArray( self.aColor )

        self.program.release()

    def _create_fbo(self):
        # FBO if enabled picking

        # with help from
        # http://groups.google.com/group/pyglet-users/browse_thread/thread/71cb064ee1f11714
        # http://www.gamedev.net/page/resources/_//feature/fprogramming/opengl-frame-buffer-object-101-r2331
        # http://www.flashbang.se/archives/48
        # FBO
        self.fbo = GLuint()
        # create our frame buffer
        glGenFramebuffersEXT(1, self.fbo)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.fbo)

        # create the colorbuffer texture and attach it to the frame buffer
        self.color_tex = GLuint(0)
        glGenTextures(1, self.color_tex)
        glBindTexture(GL_TEXTURE_2D, self.color_tex)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # Thanks to pyglet for the blank
        blank = (GLfloat * ( vsml.width * vsml.height * 4))()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, vsml.width, vsml.height, 0, GL_RGBA, GL_FLOAT, blank )
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT,GL_COLOR_ATTACHMENT0_EXT,GL_TEXTURE_2D, self.color_tex, 0)

        status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
        assert status == GL_FRAMEBUFFER_COMPLETE_EXT

        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

    def _bind_buffer(self):

        # for vertices location
        glVertexAttribPointer(self.aPosition, 3, GL_FLOAT, GL_FALSE, 0, 0)
        self.vertex_vbo = GLuint(0)
        glGenBuffers(1, self.vertex_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.vertices_draw.size, self.vertices_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableVertexAttribArray(self.aPosition)

        # for colors
        glVertexAttribPointer(self.aColor, 4, GL_FLOAT, GL_FALSE, 0, 0)
        self.colors_vbo = (GLuint * 2)(0)
        glGenBuffers(2, self.colors_vbo)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
        glBufferData(GL_ARRAY_BUFFER, 4 * self.colors_draw.size, self.colors_ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        if self.enable_picking:
            glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[1])
            glBufferData(GL_ARRAY_BUFFER, 4 * self.colors_pick.size, self.colors_pick_ptr, GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableVertexAttribArray(self.aColor)

        # for connectivity
        self.connectivity_vbo = GLuint(0)
        glGenBuffers(1, self.connectivity_vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.connectivity_vbo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * self.connectivity_nr, self.connectivity_ptr, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        if self.extruded:
            # create buffer object
            self.radius_vbo = GLuint(3)
            glGenBuffers(1, self.radius_vbo)
            glBindBuffer(GL_TEXTURE_BUFFER_EXT, self.radius_vbo)
            # init buffer object
            glBufferData(GL_TEXTURE_BUFFER_EXT, 4 * self.radius_draw.size, self.radius_ptr, GL_STATIC_DRAW)
            glBindBuffer(GL_TEXTURE_BUFFER_EXT, 0)

            # texture
            self.radius_unit = GLuint(0)
            glGenTextures(1, self.radius_unit)
            glBindTexture(GL_TEXTURE_BUFFER_EXT, self.radius_unit)
            glTexBufferEXT( GL_TEXTURE_BUFFER_EXT, GL_LUMINANCE32F_ARB, self.radius_vbo ) #    GL_RGBA32F_ARB GL_ALPHA32F_ARB
            glBindTexture(GL_TEXTURE_BUFFER_EXT, 0)


    def _pick_lines_va(self, x, y):
        #print('pick lines va')
        if not self.enable_picking:
            print("Picking not enabled. You need to set the ID parameter for the actor {0}".format(self.name) )
            return

        # resize texture as well
        glBindTexture(GL_TEXTURE_2D, self.color_tex)
        blank = (GLfloat * ( vsml.width * vsml.height * 4))()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, vsml.width, vsml.height, 0, GL_RGBA, GL_FLOAT, blank )

        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.fbo)

        glPushAttrib(GL_VIEWPORT_BIT)
        glViewport(0, 0, vsml.width, vsml.height)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #glDisable(GL_BLEND)
        #glDisable(GL_MULTISAMPLE)
        glLineWidth(self.linewidth)

        # FBO render pass, need to use the selection id color array
        ################
        glLineWidth(self.linewidth)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)

        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(4, GL_FLOAT, 0, self.colors_pick_ptr)

        glDrawElements( GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, self.connectivity_ptr )

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        
        ############

        a = (GLfloat * 4)(0)
        glReadPixels(x, y, 1, 1, GL_RGBA, GL_FLOAT, a)
        ID = (int(a[0]*255) << 16) | (int(a[1]*255) << 8) | int(a[2]*255)

        glPopAttrib()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        if ID in self.current_selection:
            self.deselect( ID )
        else:
            self.select( ID )

        return ID

    def _pick_lines(self, x, y):

        if not self.enable_picking:
            print("Picking not enabled. You need to set the ID parameter for the actor {0}".format(self.name) )
            return

        # resize texture as well
        glBindTexture(GL_TEXTURE_2D, self.color_tex)
        blank = (GLfloat * ( vsml.width * vsml.height * 4))()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, vsml.width, vsml.height, 0, GL_RGBA, GL_FLOAT, blank )

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
        ID = (int(a[0]*255) << 16) | (int(a[1]*255) << 8) | int(a[2]*255)

        glPopAttrib()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        if ID in self.current_selection:
            self.deselect( ID )
        else:
            self.select( ID )

        return ID


    def deselect(self, ID = None):
        if DEBUG:
            print "deselect(ID)", ID

        if ID is None:
            # deselect all
            self.current_selection = []
            self._reset_color_alpha( self.global_deselect_alpha )
        else:
            if ID in self.current_selection:
                selarr = np.where( self.ID_draw == ID )[0]
                self._update_color_alpha( selarr, self.global_deselect_alpha )
                self.current_selection.remove( ID )
            else:
                if DEBUG:
                    print("Not selected identifier {0}".format(ID))

        return self.current_selection

    def select(self, ID):
        if DEBUG:
            print "select(ID)", ID
        
        if ID is None or ID == 0:
            return

        if ID in self.current_selection:
            if DEBUG:
                print("Already selected identifier {0}".format(ID))
        else:
            selarr = np.where( self.ID_draw == ID )[0]
            self._update_color_alpha( selarr, self.global_select_alpha )
            self.current_selection.append(ID)

        return self.current_selection

    def _update_color_alpha(self, index, value ):

        # select a subset of vertices (e.g. for a skeleton)
        self.colors_draw[self.connectivity_draw[index.ravel()].ravel(), 3] = value

        # update VBO
        if not self.useva:
            glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
            glBufferData(GL_ARRAY_BUFFER, 4 * self.colors_nr, self.colors_ptr, GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _reset_color_alpha(self, value):
        self.colors_draw[:,3] = value
        # update VBO if existing
        if hasattr(self, "colors_vbo"):
            glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo[0])
            glBufferData(GL_ARRAY_BUFFER, 4 * self.colors_nr, self.colors_ptr, GL_DYNAMIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _draw_lines(self):
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

    def _draw_va(self):
        glEnable(GL_BLEND)

        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glLineWidth(self.linewidth)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)

        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)

        glDrawElements( GL_LINES, self.connectivity_nr, GL_UNSIGNED_INT, self.connectivity_ptr )

        glDisableClientState(GL_VERTEX_ARRAY)   
        glDisableClientState(GL_COLOR_ARRAY)

    def pick(self, x, y):
        pass

    def draw(self):
        pass
