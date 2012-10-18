from pyglet.gl import *
from camera import *
from light import *
from fos.actor import Box, Actor
from fos.transform import *
from vsml import vsml
from actor.base import DynamicActor


class Scene(object):

    def __init__(self, scenename="Main", transform=None,
                 extent_min=None, extent_max=None,
                 aabb_color=(1.0, 1.0, 1.0, 1.0),
                 activate_aabb=True):
        """Create a Scene which is a spatial reference system
        and acts as a container for Actors presenting datasets.

        Parameters
        ----------
        scenename : str
            The unique name of the Scene
        transform : fos.transform.Transform3D
            The affine transformation of the Scene, defining
            origo and the axes orientation, i.e. the local coordinate
            system of the Scene
        extent_min, extent_max : two 3x1 numpy.array
            Defines the minimum and maximum extent of the Scene along
            all three axes. This implicitly defines an
            axis-aligned bounding box which can be overwritten by the
            addition of Actors bigger then the extent and calling the
            update() function of the Scene

        Notes
        -----
        Scenes can be overlapping

        """
        super(Scene, self).__init__()

        self.scenename = scenename
        self.aabb_color = aabb_color
        self.activate_aabb = activate_aabb
        if transform is None:
            self.transform = IdentityTransform()
        else:
            self.transform = transform
        self.actors = {}
        
        if not extent_min is None and not extent_max is None:
            self.extent_min = np.array(extent_min, dtype=np.float32)
            self.extent_max = np.array(extent_max, dtype=np.float32)
            if self.activate_aabb:
                self.add_actor(Box(name="AABB", 
                                blf=self.extent_min, 
                                trb=self.extent_max, 
                                color=self.aabb_color))
        else:
            self.extent_min = None
            self.extent_max = None

    def get_centroid(self, apply_transform = True):
        """Returns the centroid of the Scene.

        Parameters
        ----------
        apply_transform : bool
            Applies the Scene affine transformation to the centroid
            
        """
        if not self.extent_min is None and not self.extent_max is None:
            ret = np.vstack( (self.extent_min,self.extent_max) ).mean( axis = 0 )
        else:
            ret = np.zeros( (1,3), dtype = np.float32 )

        if apply_transform:
            ret = self.transform.apply( ret )
            
        return ret

    def get_extent_min(self, apply_transform = True):
        if not self.extent_min is None:
            ret = self.extent_min
        else:
            ret = np.zeros( (1,3), dtype = np.float32 )
        if apply_transform:
            ret = self.transform.apply( ret )
        return ret

    def get_extent_max(self, apply_transform = True):
        if not self.extent_max is None:
            ret = self.extent_max
        else:
            ret = np.zeros( (1,3), dtype = np.float32 )            
        if apply_transform:
            ret = self.transform.apply( ret )
        return ret

    def update_extent(self):
        """
        Loop over all contained actors and query for the min/max extent
        and update the Scene's extent accordingly
        """
        for name, actor in self.actors.items():
            if not self.extent_min is None:
                self.extent_min = np.vstack( (self.extent_min,
                    actor.get_extent_min()) ).min( axis = 0 )
            else:
                self.extent_min = actor.get_extent_min()

            if not self.extent_max is None:
                self.extent_max = np.vstack( (self.extent_max,
                    actor.get_extent_max()) ).max( axis = 0 )
            else:
                self.extent_max = actor.get_extent_max()

        # update AABB
        if self.activate_aabb:
            if "AABB" in self.actors:
                self.actors['AABB'].update( self.extent_min, 
                                            self.extent_max, 0.0 )
            else:
                self.add_actor( Box(name="AABB", 
                                blf=self.extent_min, 
                                trb=self.extent_max, 
                                color=self.aabb_color) )

    def update(self):
        self.update_extent()

    def add_actor(self, actor, trigger_update = True):
        if isinstance( actor, Actor ):
            if actor.name in self.actors:
                print("Actor {0} already exist in Scene {1}".format(actor.name, self.scenename) )
            else:
                self.actors[actor.name] = actor
                self.update()
        else:
            print("Not a valid Actor instance.")

    def remove_actor(self, actor, trigger_update = True):
        if isinstance( actor, Actor ):
            if actor.name in self.actors:
                del self.actors[actor.name]
                self.update()
            else:
                print("Actor {0} does not exist in Scene {1}".format(actor.name, self.scenename) )
        elif isinstance( actor, str ):
            # actor is the unique name of the actor
            if actor in self.actors:
                del self.actors[actor]
                self.update()
            else:
                print("Actor {0} does not exist in Scene {1}".format(actor.name, self.scenename) )
        else:
            print("Not a valid Actor instance or actor name.")

    def nextTimeFrame(self):
        for k, actor in self.actors.items():
            if actor.visible and isinstance(actor, DynamicActor):
                actor.next()

    def previousTimeFrame(self):
        for k, actor in self.actors.items():
            if actor.visible and isinstance(actor, DynamicActor):
                actor.previous()

    def draw_actors(self):
        """ Draw all visible actors in the scene
        """
        for k, actor in self.actors.items():
            if actor.visible:
                #print("Draw actor", actor.name)
                actor.draw()

    def pick_actors(self, x, y):
        """ Pick all visible actors in the scene
        """
        for k, actor in self.actors.items():
            if actor.visible:
                #print("Pick actor", actor.name)
                actor.pick( x, y )

    def send_messages(self,messages):
        for k, actor in self.actors.items():
            if actor.visible:
                #print('Actor: ',actor.name)
                actor.process_messages(messages)

class World(object):

    def __init__(self):
        self.scenes = {}
        self.set_camera( SimpleCamera() )
        self.light = None

    def setup_light(self):
        self.light = Light()

    def update_lightposition(self, x, y, z):
        self.light.update_lightposition(x, y, z)

    def add_scene(self, scene):
        if scene.scenename in self.scenes:
            print("Scene {0} already exist.".format(scene.scenename))
        else:
            self.scenes[scene.scenename] = scene

    def set_camera(self, camera):
        self.camera = camera
        # hackish, store a reference to the camera in the global static
        # vsml object to enable actor's positioning depending on camera parameters
        vsml.camera = self.camera

    def get_camera(self):
        return self.camera

    def refocus_camera(self):
        # loop over all scenes, get global min, max, centroid
        # set focus point to average, and location to centroid + 2x(max-min).z

        centroids = np.zeros( (len(self.scenes), 3), dtype = np.float32 )
        maxextent = np.zeros( (len(self.scenes), 3), dtype = np.float32 )
        minextent = np.zeros( (len(self.scenes), 3), dtype = np.float32 )
        
        for i, scene in enumerate(self.scenes.items()):
            centroids[i,:] = scene[1].get_centroid()
            maxextent[i,:] = scene[1].get_extent_max()
            minextent[i,:] = scene[1].get_extent_min()

        newfoc = centroids.mean( axis = 0 )
        self.camera.set_focal( newfoc )
        newloc = newfoc.copy()
        # move along z axes sufficiently far to see all the scenes
        # TODO: better
        dist = maxextent.max( axis = 0 ) - minextent.min( axis = 0 )
        newloc[2] += dist[0] 
        self.camera.set_location( newloc, np.array([0.0,1.0,0.0]) )
        self.camera.update()

    def nextTimeFrame(self):
        for k, scene in self.scenes.items():
            scene.nextTimeFrame()

    def previousTimeFrame(self):
        for k, scene in self.scenes.items():
            scene.previousTimeFrame()

    def pick_all(self, x, y):
        """ Calls the pick function on all Scenes
        """
        self.camera.draw()
        for k, scene in self.scenes.items():
            # use transformation matrix of the scene to setup the modelview
            vsml.pushMatrix( vsml.MatrixTypes.MODELVIEW ) 
            vsml.multMatrix( vsml.MatrixTypes.MODELVIEW, 
                                scene.transform.get_transform_numpy() )
            glMatrixMode(GL_MODELVIEW)
            glLoadMatrixf(vsml.get_modelview())
            scene.pick_actors( x, y )
            # take back the old camera modelview
            vsml.popMatrix( vsml.MatrixTypes.MODELVIEW )
            
    def draw_all(self):
        """ Draw all actors
        """
        self.camera.draw()
        for k, scene in self.scenes.items():
            # use transformation matrix of the scene to setup the modelview
            vsml.pushMatrix( vsml.MatrixTypes.MODELVIEW ) # in fact, push the camera modelview
            vsml.multMatrix( vsml.MatrixTypes.MODELVIEW, 
                    scene.transform.get_transform_numpy() )
            glMatrixMode(GL_MODELVIEW)
            glLoadMatrixf(vsml.get_modelview())
            scene.draw_actors()
            # take back the old camera modelview
            vsml.popMatrix( vsml.MatrixTypes.MODELVIEW )

    def send_all_messages(self,messages):
        #print 'scenes.items',self.scenes.items
        #print self.scenes.items()
        for regname,scene in self.scenes.items():
            #print 'Scene name ',regname
            scene.send_messages(messages)
            #print 
