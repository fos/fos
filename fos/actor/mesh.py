import numpy as np
from pyglet.gl import *
from .base import Actor

class Mesh(Actor):

    def __init__(self, name, vertices, connectivity, values = None, colormap = None, color = (0.0, 1.0, 0.0, 1.0), wireframe = False):
        """ A Mesh actor with triangular or quad connectivity
        """
        super(Mesh, self).__init__( name )
        # TODO: implement values, colormap functionality
        
        self.vertices, self.connectivity = vertices, connectivity
        
        self.wireframe = wireframe
        self.color = color

        if connectivity.shape[1] == 3:
            self.mode = GL_TRIANGLES
        elif connectivity.shape[1] == 4:
            self.mode = GL_QUADS
        else:
            raise Exception("Invalid connectivity shape")

        self.values = values
        
        if not self.values is None and not colormap is None:
            if isinstance( colormap, dict):
                # TODO: do the dict mapping to colors
                pass
            else:
                # TODO: fix colormapping
                self.colormap_array = colormap( values ).astype( np.float32 )
                self.colors_ptr = self.colormap_array.ctypes.data
        else:
            self.colormap_array = None
            self.colors_ptr = None

        self.vertices_ptr = self.vertices.ctypes.data
        self.connectivity_ptr = self.connectivity.ctypes.data
        self.connectivity_nr = self.connectivity.size

    def draw(self):
        glDisable(GL_CULL_FACE)
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)

        if not self.colormap_array is None:
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)
        else:
            glColor4f( self.color[0], self.color[1], self.color[2], self.color[3] )

        glDrawElements( self.mode, self.connectivity_nr, GL_UNSIGNED_INT, self.connectivity_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)
