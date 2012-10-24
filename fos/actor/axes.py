import numpy as np
from pyglet.gl import *
from .base import *
from .primitives import Cylinder

class Axes(Actor):

    def __init__(self, name = "Cartesian Axes", scale = 1.0, linewidth = 1.0):
        """ Draw three axes
        """
        super(Axes, self).__init__( name )

        self.scale = scale
        self.linewidth = linewidth

        self.vertices = self.scale * np.array( [ 
            [0.0, 0.0, 0.0],[1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],[0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],[0.0, 0.0, 1.0]], dtype = np.float32 )

        # x axes arrow
        self.x_cone = Cylinder( "XCone", np.array([0.8,0,0]), np.array([1.1,0,0]), 0.15, 0, 10, color = (1.0, 0, 0, 1.0) )
        self.y_cone = Cylinder( "YCone", np.array([0,0.8,0]), np.array([0,1.1,0]), 0.15, 0, 10, color = (0, 1.0, 0, 1.0) )
        self.z_cone = Cylinder( "ZCone", np.array([0,0,0.8]), np.array([0,0,1.1]), 0.15, 0, 10, color = (0, 0, 1.0, 1.0) )

        # store lightning state to set back to default
        self.light_state = GLboolean(0)
        glGetBooleanv(GL_LIGHTING, self.light_state)

    def draw(self):

        glDisable(GL_LIGHTING)

        self.x_cone.draw()
        self.y_cone.draw()
        self.z_cone.draw()
        
        #glPushMatrix()
        glLineWidth(self.linewidth)
        glBegin (GL_LINES)
        # x axes
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(*tuple(self.vertices[0,:]))
        glVertex3f(*tuple(self.vertices[1,:]))
        # y axes
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(*tuple(self.vertices[2,:]))
        glVertex3f(*tuple(self.vertices[3,:]))
        # z axes
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(*tuple(self.vertices[4,:]))
        glVertex3f(*tuple(self.vertices[5,:]))
        glEnd()
        glLineWidth(1.0)
        #glPopMatrix()

        if self.light_state:
            glEnable(GL_LIGHTING)

