from pyglet.gl import *
from .base import *

class Axes(Actor):

    def __init__(self, scale = 10.0):
        """ Draw three axes
        """
        super(Axes, self).__init__()
        self.scale = scale

    def draw(self):
        #glPushMatrix()
        glLineWidth(2.0)
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
        #glPopMatrix()

class CartesianAxes(object):

    def __init__(self):
            """ Actor displaying the three cartesian, orthogonal coordinates
            """
            pass