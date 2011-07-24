from camera import *

class Region(object):
    """ A Region is a spatial container concept and is defined as a cuboid box with
    - a name as text string
    - transformation from the parent region or world coordinate system,to the
    - local coordinate system defined by the transformation
    - resolution strings
    - oriented-bounding box

    Regions can be overlapping.
    Static and dynamic actors are part of Region, defining the boundaries of the bounding box
    """

    def __init__(self, regionname, transform, resolution ):
        self.regionname = regionname
        self.transform = transform
        self.resolution = resolution
        self.actors = {}

    def add_actor(self, actor):
        if actor in self.actors:
            print("Actor {0} already exist in Region {1}".format(actor, self.regionname) )
        else:
            self.actors[actor] = actor

    def remove_actor(self, actor):
        if actor in self.actors:
            del self.actors[actor]
        else:
            print("Actor {0} does not exist in Region {1}".format(actor, self.regionname) )

    def draw_actors(self):
        """ Draw all visible actors in the region
        """
        for k, actor in self.actors.items():
            if actor.visible:
                actor.draw()

class World(object):

    def __init__(self):
        self.regions = {}
        self.camera = SimpleCamera()

    def new_region(self, regionname, transform, resolution ):
        if regionname in self.regions:
            print("Region {0} already exist.".format(regionname))
        else:
            self.regions[regionname] = Region( regionname, transform, resolution )

    def add_actor_to_region(self, regionname, actor):
        if regionname in self.regions:
            self.regions[regionname].add_actor( actor )
        else:
            print("Create Region first before adding actors.")

    def remove_actor_from_region(self, regionname, actor):
        if regionname in self.regions:
            self.regions[regionname].remove_actor()
        else:
            print("Region {0} does not exist.".format(regionname))

    def set_camera(self, camera):
        self.camera = camera

    def get_camera(self):
        return self.camera

    def draw_all(self):
        """ Draw all actors
        """
        self.camera.draw()
        for k, region in self.regions.items():
            region.draw_actors()