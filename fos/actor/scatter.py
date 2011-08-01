import numpy as np
from pyglet.gl import *
from .base import Actor
from fos.actor.primitives import makeNSphere

class Scatter(Actor):

    def __init__(self, name, x, y, z, values = None, type = 'sphere', iterations = 2):
        """ A Scatter actor to display scatter plots
        """
        super(Scatter, self).__init__( name )

        n = len(x)
        self.vertices = []
        self.faces = []
        face_offset = 0
        for i in range(n):

            vertices, faces = makeNSphere( iterations )
            if not values is None:
                vertices *= values[i]
                
            # translate
            vertices[:,0] += x[i]
            vertices[:,1] += y[i]
            vertices[:,2] += z[i]

            self.vertices.append( vertices )
            faces += face_offset
            self.faces.append( faces )
            face_offset += len(vertices)

        self.vertices = np.concatenate( self.vertices ).astype( np.float32 )
        self.faces = np.concatenate( self.faces ).astype( np.uint32 )

        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.faces.ctypes.data
        self.faces_nr = self.faces.size

    def draw(self):
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(1.0)
        glColor3f(1.0, 1.0, 0.0)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glDrawElements( GL_TRIANGLES, self.faces_nr, GL_UNSIGNED_INT, self.faces_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)