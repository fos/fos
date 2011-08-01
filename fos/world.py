from pyglet.gl import *
from camera import *
from fos.actor import Box

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

    def __init__(self, regionname, transform, resolution, extent = None ):
        super(Region,self).__init__()
        
        self.regionname = regionname
        self.transform = transform
        self.resolution = resolution
        self.actors = {}
        
        if extent:
            self.extent = extent
            self.add_actor( Box( "AABB", extent[0], extent[1] ) )


    def add_actor(self, actor):
        if actor in self.actors:
            print("Actor {0} already exist in Region {1}".format(actor.name, self.regionname) )
        else:
            self.actors[actor.name] = actor

    def remove_actor(self, actor):
        # TODO: check if isinstance str
        if actor.name in self.actors:
            del self.actors[actor.name]
        else:
            print("Actor {0} does not exist in Region {1}".format(actor.name, self.regionname) )

    def draw_actors(self):
        """ Draw all visible actors in the region
        """
        for k, actor in self.actors.items():
            if actor.visible:
                # use transformation matrix of the region to setup the modelview
                vsml.pushMatrix( vsml.MatrixTypes.MODELVIEW ) # in fact, push the camera modelview
                vsml.multMatrix( vsml.MatrixTypes.MODELVIEW, self.transform.get_transform_numpy() )
                glMatrixMode(GL_MODELVIEW)
                glLoadMatrixf(vsml.get_modelview())
                actor.draw()
                # take back the old camera modelview
                vsml.popMatrix( vsml.MatrixTypes.MODELVIEW )

class World(object):

    def __init__(self):
        self.regions = {}
        self.camera = SimpleCamera()

    def add_region(self, region):
        if region.regionname in self.regions:
            print("Region {0} already exist.".format(region.regionname))
        else:
            self.regions[region.regionname] = region

    def new_region(self, regionname, transform, resolution, extent = None ):
        if regionname in self.regions:
            print("Region {0} already exist.".format(regionname))
        else:
            self.regions[regionname] = Region( regionname = regionname, transform = transform, resolution = resolution, extent = extent )

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