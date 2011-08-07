import numpy as np
from pyglet.gl import *
from .base import Actor
from fos.actor.primitives import *
from pylab import cm

class Scatter(Actor):

    def __init__(self, name, x, y, z, values = None, colormap = cm.Accent, type = 'sphere', iterations = 2, wireframe = False):
        """ A Scatter actor to display scatter plots
        """
        super(Scatter, self).__init__( name )

        if type == 'sphere':
            self.vertices, self.faces, self.colors = make_sphere_scatter( x, y, z, values, iterations, colormap )
        else:
            raise Exception("Only valid type for Scatter is 'sphere'")

        self.wireframe = wireframe
        self.vertices_ptr = self.vertices.ctypes.data
        if not self.colors is None:
            self.colors_ptr = self.colors.ctypes.data
        self.faces_ptr = self.faces.ctypes.data
        self.faces_nr = self.faces.size
        
    def draw(self):
        glDisable(GL_CULL_FACE)
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(1.0)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)

        if not self.colors is None:
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)

        glDrawElements( GL_TRIANGLES, self.faces_nr, GL_UNSIGNED_INT, self.faces_ptr )

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)

class ScatterCylinder(Actor):

    def __init__(self, name, p1, p2, r1, r2, values = None, colormap = None, resolution = 4):
        """ A ScatterCylinder actor to display scatter plots
        """
        super(ScatterCylinder, self).__init__( name )

        self.vertices, self.faces = make_cylinder_scatter( p1, p2, r1, r2, resolution )

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

