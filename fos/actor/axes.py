import numpy as np
from pyglet.gl import *
from .base import *
from primitives import Cylinder

class Axes(Actor):

    def __init__(self, name = "Cartesian Axes", scale = 1.0, linewidth = 1.0):
        """ Draw three axes
        """
        super(Axes, self).__init__( name )

        self.scale = scale
        self.linewidth = linewidth

        # x axes arrow
        self.x_cone = Cylinder( "XCone", np.array([0.8,0,0]), np.array([1.1,0,0]), 0.15, 0, 10, color = (1.0, 0, 0, 1.0) )
        self.y_cone = Cylinder( "YCone", np.array([0,0.8,0]), np.array([0,1.1,0]), 0.15, 0, 10, color = (0, 1.0, 0, 1.0) )
        self.z_cone = Cylinder( "ZCone", np.array([0,0,0.8]), np.array([0,0,1.1]), 0.15, 0, 10, color = (0, 0, 1.0, 1.0) )

    def draw(self):

        self.x_cone.draw()
        self.y_cone.draw()
        self.z_cone.draw()
        
        #glPushMatrix()
        glLineWidth(self.linewidth)
        glBegin (GL_LINES)
        # x axes
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(self.scale,0.0,0.0)
        # y axes
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(0.0,self.scale,0.0)
        # z axes
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0,0.0,0.0)
        glVertex3f(0.0,0.0,self.scale)
        glEnd()
        glLineWidth(1.0)
        #glPopMatrix()

class CartesianAxes(object):

    def __init__(self):
            """ Actor displaying the three cartesian, orthogonal coordinates
            """
            pass