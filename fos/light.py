from pyglet.gl import *

# Define a simple function to create ctypes arrays of floats:
def vec(*args):
    return (GLfloat * len(args))(*args)

class Light(object):

    def __init__(self):

        # lights
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glLightfv(GL_LIGHT0, GL_POSITION, vec(100, 100, 100, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vec(0,0,0,1))
        glLightfv(GL_LIGHT0, GL_AMBIENT, vec(0,0,0,1))

        #glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,1)
        
        glMaterialfv(GL_FRONT,GL_AMBIENT,vec(0,0,0,0))
        glMaterialfv(GL_FRONT,GL_SPECULAR,vec(0,0,0,0))
        #glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
        #glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
        #glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT,GL_DIFFUSE)

    def update_lightposition(self, x, y, z):
        glLightfv(GL_LIGHT0, GL_POSITION, vec(x, y, z, 0))
        