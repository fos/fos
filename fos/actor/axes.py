import numpy as np
from pyglet.gl import *
from .base import *
from primitives import Cylinder

class Axes(Actor):

    def __init__(self, name = "Cartesian Axes", scale = 10.0, linewidth = 1.0):
        """ Draw three axes
        """
        super(Axes, self).__init__( name )

        self.scale = scale
        self.linewidth = linewidth

        # x axes arrow
        self.x_cone = Cylinder( "XVone", np.array([self.scale*1.1-5,0,0]), np.array([self.scale*1.1,0,0]), 1 , 0, 10 )

    def draw(self):

        self.x_cone.draw()
        
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