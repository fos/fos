from camera import *

class World(object):

    def __init__(self):

        self.actors = []
        self.camera = SimpleRotationCamera()

    def add_actor(self, actor):
        if not actor in self.actors:
            self.actors.append( actor )

    def remove_actor(self, actor):
        if actor in self.actors:
            self.actors.remove( actor )

    def set_camera(self, camera):
        self.camera = camera

    def draw_all(self):
        """ Draw all actors
        """
        self.camera.draw()
        for actor in self.actors:
            actor.draw()