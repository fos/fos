from pyglet.gl import *
from vsml import vsml
import numpy as np

class Camera(object):

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
        super(VSMLCamera, self).__init__()

    def draw(self):
        # use the modelview in the OpenGL fixed-pipeline
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(vsml.get_modelview())

    def reset(self):
        # load identity for modelview when initializing
        vsml.loadIdentity(vsml.MatrixTypes.MODELVIEW)

    def translate(self, x, y, z):
        # need to update .lu and call init identity and lookat again
        # or direclty change the modelview
        vsml.translate(x, y, z, vsml.MatrixTypes.MODELVIEW)

    def scale(self, x, y, z):
        vsml.scale(x, y, z, vsml.MatrixTypes.MODELVIEW)

    def rotate(self, angle, x, y, z):
        vsml.rotate(angle, x, y, z, vsml.MatrixTypes.MODELVIEW)

# http://www.lighthouse3d.com/tutorials/glut-tutorial/keyboard-example-moving-around-the-world/
class SimpleRotationCamera(VSMLCamera):

    def __init__(self):
        """ This camera uses the lookAt function to move """
        super(SimpleRotationCamera, self).__init__()

        self.look_at_point = [0, 0, 0]
        self.camera_distance_from_lookat = 20
        self.angle = 0.0
        self.camera_line_of_sight = [0, 0, -1]
        self.camera_up_vector = [0, 1, 0]
        
        #self.camera_right_vector = [1, 0, 0]

        self.scroll_speed = 10
        self.mouse_speed = 0.1
        self.update()

    def rotate_xz(self, angle):
        """ Move on a circle on the xz plane
        """
        self.angle += angle
        self.camera_line_of_sight[0] = np.sin( self.angle )
        self.camera_line_of_sight[2] = -np.cos( self.angle )
        #print("Rotate camera")
        #print self.angle
        #print self.camera_line_of_sight
        self.update()

    def move(self, amount):
        """ Move along the light of sight
        """
        #self.look_at_point[0] += self.camera_line_of_sight[0] * amount
        #self.look_at_point[2] += self.camera_line_of_sight[2] * amount
        self.camera_distance_from_lookat += amount
        #print("Move camera")
        #print self.look_at_point
        self.update()

    def update(self):
        super(SimpleRotationCamera, self).reset()
        # setup the initial look at updating the modelview
        # vsml.lookAt(*self.lu)
        camera_position = [
            self.look_at_point[0] + self.camera_line_of_sight[0] * self.camera_distance_from_lookat,
            self.look_at_point[1] + self.camera_line_of_sight[1] * self.camera_distance_from_lookat,
            self.look_at_point[2] - self.camera_line_of_sight[2] * self.camera_distance_from_lookat
        ]
        lu = camera_position + self.look_at_point + self.camera_up_vector
        vsml.lookAt(*lu )
        #print("Camera update called.")
        #print lu


class SimpleCamera(Camera):
    pass
# http://nehe.gamedev.net/article/camera_class_tutorial/18010/