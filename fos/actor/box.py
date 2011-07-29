import numpy as np
from pyglet.gl import *
from .base import *

class Box(Actor):

    def __init__(self, name, blf = None, trb = None, margin = 0):
        """ Box from bottom-left-front and top-right-back point coordinates
        (Axis Aligned Bounding)
        """
        super(Box, self).__init__( name )
        
        self.update(blf, trb, margin)

        self.vertices_nr = self.vertices.shape[0]
        self.indices_nr = self.indices.size

        self.vertices_ptr = self.vertices.ctypes.data
        self.indices_ptr = self.indices.ctypes.data

    def update(self, c1, c2, margin):
        """ c1 is botton-left-front, and c2 is top-right-back point
        """
        # add the margin on all sides
        c1[0] = c1[0] - margin
        c1[1] = c1[1] - margin
        c1[2] = c1[2] - margin

        c2[0] = c2[0] + margin
        c2[1] = c2[1] + margin
        c2[2] = c2[2] + margin

        self.coord = (np.array(c1, dtype = np.float32),
                      np.array(c2, dtype = np.float32))

        self.vertices = np.array([
               [c1[0],c1[1],c2[2]],
               [c1[0],c1[1],c1[2]],
               [c1[0],c2[1],c2[2]],
               [c1[0],c2[1],c1[2]],
               [c2[0],c1[1],c2[2]],
               [c2[0],c1[1],c1[2]],
               [c2[0],c2[1],c2[2]],
               [c2[0],c2[1],c1[2]]], dtype = np.float32)

        self.indices = np.array([ [0,1,5,4],
                           [2,3,7,6],
                           [2,0,1,3],
                           [3,7,5,1],
                           [7,6,4,5],
                           [6,2,0,4] ], dtype = np.uint32)


    def draw(self):
        #glPushMatrix()
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(1.0)
        glColor3f(1.0, 1.0, 0.0)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glDrawElements( GL_QUADS, self.indices_nr, GL_UNSIGNED_INT, self.indices_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)
        #glPopMatrix()
