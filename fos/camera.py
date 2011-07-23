from pyglet.gl import *
from vsml import vsml

class Camera():

    def __init__(self):
        pass

    def update(self):
        " This should update the camera "
        pass

    def draw(self):
        pass

    def info(self):
        pass

# for ideas:
# http://code.enthought.com/projects/mayavi/docs/development/html/mayavi/auto/mlab_camera.html
# http://www.opengl.org/resources/faq/technical/viewing.htm

class VSMLCamera(Camera):
    def __init__(self):
        self.lu = [0,0,120, 0,0,0, 0,1,0]
        self.scroll_speed = 10
        self.mouse_speed = 0.1
        self.reset()

    def draw(self):
        # use the modelview in the OpenGL fixed-pipeline
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(vsml.get_modelview())

    def reset(self):
        # load identity for modelview when initializing
        vsml.loadIdentity(vsml.MatrixTypes.MODELVIEW)
        # setup the initial look at updating the modelview
        vsml.lookAt(*self.lu)

    def translate(self, x, y, z):
        # need to update .lu and call init identity and lookat again
        # or direclty change the modelview
        vsml.translate(x, y, z, vsml.MatrixTypes.MODELVIEW)

    def scale(self, x, y, z):
        vsml.scale(x, y, z, vsml.MatrixTypes.MODELVIEW)

    def rotate(self, angle, x, y, z):
        vsml.rotate(angle, x, y, z, vsml.MatrixTypes.MODELVIEW)