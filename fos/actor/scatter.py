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
        elif type == 'cube':
            self.vertices, self.faces, self.colors = make_cube_scatter( x, y, z, values, colormap )
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

class VectorScatter(Actor):

    def __init__(self, name, p1, p2, r1, r2, type = 'cylinder', values = None, colormap = None, resolution = 4, wireframe = False):
        """ A ScatterCylinder actor to display scatter plots
        """
        super(VectorScatter, self).__init__( name )

        # TODO: arrow scatter
        if type == 'cylinder':
            self.vertices, self.faces, self.colors, self.index_range = make_cylinder_scatter( p1, p2, r1, r2, values, resolution, colormap )
        else:
            raise Exception("Only valid type for VectorScatter is 'cylinder'")

        # self.index_range
        # columns: index, range from vertices array, range to vertices array
        # TODO: might be required for faces as well. in order to retrieve the index (first column)
        # of a selected face (would require looping through the datastructure, which is unnecessary)

        self.wireframe = wireframe

        if not self.colors is None:
            self.colors_ptr = self.colors.ctypes.data
        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.faces.ctypes.data
        self.faces_nr = self.faces.size

    def set_coloralpha_index(self, index_list, alphavalue = 0.2):
        """ Sets the color alpha value for a list of indices to alphavalue """
        for i in index_list:
            self.colors[self.index_range[i,1]:self.index_range[i,2],3] = alphavalue

    def set_coloralpha_all(self, alphavalue = 0.2):
        self.colors[:,3] = alphavalue

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

