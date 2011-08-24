import numpy as np
from pyglet.gl import *
from .base import Actor

class Mesh(Actor):

    def __init__(self, name, vertices, connectivity, vertices_colors = None, vertices_normals = None, wireframe = False):
        """ A Mesh actor with triangular or quad connectivity

        Parameters
        ----------
        vertices : array, shape (N,3)
        connectivity : array, shape (M,3) or (M,4)
        vertices_colors = array, shape (M,4) or None
        
        """
        super(Mesh, self).__init__( name )

        self.vertices= vertices
        self.connectivity = connectivity
        
        self.wireframe = wireframe
        self.colors = vertices_colors
        self.normals = vertices_normals
        
        if self.colors is None:
            self.colors = np.ones( (len(self.vertices),4), dtype = np.float32 )
            # make it yellow
            self.colors[:,2] = 0.0

        if not self.normals is None:
            self.normals_ptr = self.normals.ctypes.data

        if connectivity.shape[1] == 3:
            self.mode = GL_TRIANGLES
        elif connectivity.shape[1] == 4:
            self.mode = GL_QUADS
        else:
            raise Exception("Invalid connectivity shape")

        self.vertices_ptr = self.vertices.ctypes.data
        self.connectivity_ptr = self.connectivity.ctypes.data
        self.connectivity_nr = self.connectivity.size
        self.colors_ptr = self.colors.ctypes.data

    def draw(self):
        # TODO: need some state for the color
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)

        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)

        if not self.normals is None:
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, self.normals_ptr)

        glDrawElements( self.mode, self.connectivity_nr, GL_UNSIGNED_INT, self.connectivity_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        if not self.normals is None:
            glDisableClientState(GL_NORMAL_ARRAY)
            
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)
