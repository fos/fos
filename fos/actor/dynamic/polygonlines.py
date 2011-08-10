import numpy as np
from pyglet.gl import *

from ..base import *

class DynamicPolygonLinesSimple(DynamicActor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             colors = None,
             affine = None):
        """ Dynamic PolygonLines, composed of many (branching) polygons
        Colors change over time

        name : str
            The name of the actor
        vertices : Nx3
            3D Coordinates x,y,z
        connectivity : Mx1
            Tree topology
        colors : Nx4xT or 1x4
            Per connection color
        affine : 4x4
            Affine transformation of the actor

        """
        super(DynamicPolygonLinesSimple, self).__init__( name )

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

        # self.colors stores a reference to the original (N,3,T) array

        # we want per line color
        # duplicating the color array, we have the colors per vertex
        #self.colors =  np.repeat(self.colors, 2, axis=0)

        self.max_time_frame = self.colors.shape[2] - 1
        self.updatePtr()
        
        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.connectivity.ctypes.data
        self.faces_nr = self.connectivity.size
        
    def updatePtr(self):
        # duplicate color array and store a reference
        self.colors_render =  np.repeat(self.colors[:,:,self.current_time_frame], 2, axis=0)
        self.colors_ptr = self.colors_render.ctypes.data

    def draw(self):

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)

        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)

        glDrawElements( GL_LINES, self.faces_nr, GL_UNSIGNED_INT, self.faces_ptr )

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
