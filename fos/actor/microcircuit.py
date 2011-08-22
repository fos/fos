import numpy as np
from pyglet.gl import *
from .base import *
from fos.actor.primitives import *
from fos.actor.skeleton import *
from fos.actor.scatter import *

from PySide.QtGui import QMatrix4x4

from fos.shader.lib import *
from fos.vsml import vsml

class Microcircuit(Actor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             vertices_properties = None,
             connectivity_properties = None,
             connectivity_index = None,
             connectivity_colormap = None,
             affine = None):
        """ A Microcircuit actor with skeletons, connectors and incoming
        and outgoing connectivity

        name : str
            The name of the actor
        vertices : Nx3
            3D Coordinates x,y,z
        connectivity : Mx1
            Tree topology
        colors : Nx4 or 1x4
            Per connection color
        affine : 4x4
            Affine transformation of the actor

        Notes
        -----
        Only create this actor when a valid OpenGL context exists.
        Uses Vertex-Buffer objects and propagate shaders.
        """
        super(Microcircuit, self).__init__( name )

        if affine is None:
            self.affine = np.eye(4, dtype = np.float32)
        else:
            self.affine = affine

        # TODO: properly structure
        self.vertices_properties = vertices_properties
        self.connectivity_index = connectivity_index

        if connectivity_properties is None:
            print("Need to provide connectivity_properties dictionary with label and data")
            return
        else:

            if isinstance(connectivity_properties, dict):
                
                self.connectivity_properties = connectivity_properties

                # extract connectivity labels
                if self.connectivity_properties.has_key("label"):
                    self.connectivity_labels = self.connectivity_properties["label"]["data"]

                if self.connectivity_properties.has_key("id"):
                    self.connectivity_ids = self.connectivity_properties["id"]["data"]

                for semanticdict in self.connectivity_properties["label"]["metadata"]["semantics"]:
                    # name needs to be based on convention, TODO: best from ontology id rather than string!
                    if semanticdict.has_key("name"):
                        name = semanticdict["name"]
                    if "skeleton" in name:
                        self.con_skeleton = int(semanticdict["value"])
                    elif "presynaptic" in name:
                        self.con_pre = int(semanticdict["value"])
                    elif "postsynaptic" in name:
                        self.con_post = int(semanticdict["value"])

        # selection stores integer ids from connectivity_selectionID
        # when selected
        self.skeleton_selection = []

        # use the connectivity labels to extract the connectivity for the skeletons
        self.index_skeleton = np.where(self.connectivity_labels == self.con_skeleton)[0]
        self.index_allpre = np.where(self.connectivity_labels == self.con_pre)[0]
        self.index_allpost = np.where(self.connectivity_labels == self.con_post)[0]
        
        self.vertices = vertices
        self.connectivity = connectivity

        connectivity_skeleton = self.connectivity[self.index_skeleton]
        self.vertices_skeleton = self.vertices[ connectivity_skeleton.ravel() ]
        
        # we have a simplified connectivity now
        self.connectivity_skeleton = np.array( range(len(self.vertices_skeleton)), dtype = np.uint32 )
        self.connectivity_skeleton = self.connectivity_skeleton.reshape( (len(self.connectivity_skeleton)/2, 2) )
        self.connectivity_ids_skeleton = self.connectivity_ids[ self.index_skeleton ]
        print "connectivity ids skel", self.connectivity_ids_skeleton.dtype
        # look up the start and end vertex id
        # map these to _skeleton arrays, and further to actor???

        size = 0.6
        ##########
        # Incoming connectors
        ##########

        # extract the pre connectivity and create cones
        # store the indices for to be used to create the vector scatter
        # by itself, it represent implicitly the index used to select/deselect the vectors

        self.vertices_pre = vertices[ connectivity[self.index_allpre].ravel() ]
        self.pre_p1 = self.vertices_pre[::2, :] # data is NOT copied here
        self.pre_p2 = self.vertices_pre[1::2, :]
        pren = len(self.index_allpre)
        r1 = np.ones( pren, dtype = np.float32 ) * size
        r2 = np.zeros( pren, dtype = np.float32 )
        if isinstance(connectivity_colormap, dict) and connectivity_colormap.has_key( self.con_pre ):
            preval = np.ones( pren, dtype = np.dtype(type(self.con_pre)) ) * self.con_pre
        else:
            preval = None
        self.pre_actor = VectorScatter( "PreConnector", self.pre_p1, self.pre_p2, r1, r2, values = preval,
                                        resolution = 8, colormap = connectivity_colormap )
        # len(self.index_pre) = len(self.pre_p1) = len(preval)

        ##########
        # Outgoing connectors
        ##########

        # extract the post connectivity and create cones
        self.vertices_post = vertices[ connectivity[self.index_allpost].ravel() ]
        self.post_p1 = self.vertices_post[::2, :]
        self.post_p2 = self.vertices_post[1::2, :]
        postn = len(self.index_allpost)
        r1 = np.zeros( postn, dtype = np.float32 )
        r2 = np.ones( postn, dtype = np.float32 ) * size
        if isinstance(connectivity_colormap, dict) and connectivity_colormap.has_key( self.con_post ):
            postval = np.ones( postn, dtype = np.dtype(type(self.con_post)) ) * self.con_post
        else:
            postval = None
        self.post_actor = VectorScatter( "PostConnector", self.post_p1, self.post_p2, r1, r2, values = postval,
                                         resolution = 8, colormap = connectivity_colormap )

        ##########
        # Skeletons
        ##########
        self.skeleton = Skeleton( name = "Polygon Lines",
                                             vertices = self.vertices_skeleton,
                                             connectivity = self.connectivity_skeleton,
                                             ID = self.connectivity_ids_skeleton )

        self.connectivity_skeletononly_ids = None
        self.connectivity_preonly_ids = None
        self.connectivity_postonly_ids = None

        self.global_deselect_alpha = 0.2
        self.global_select_alpha = 1.0

    def pick(self, x, y):
        ID = self.skeleton.pick( x, y )
        print "got id from skeleton", ID
        if ID is None or ID == 0:
            return
        self.select_skeleton( [ ID ] )

    def deselect_all(self, value = 0.2):
        """
        Sets the alpha value of all polygon lines to 0.2
        """
        self.skeleton_selection = []
        self.pre_actor.set_coloralpha_all( alphavalue = value )
        self.post_actor.set_coloralpha_all( alphavalue = value )
        self.skeleton.deselect( )

    def select_skeleton(self, skeleton_id_list, value = 1.0 ):

        print "select..."
        if self.connectivity_skeletononly_ids is None:
            self.connectivity_skeletononly_ids = self.connectivity_ids[self.index_skeleton]

        if self.connectivity_preonly_ids is None:
            self.connectivity_preonly_ids = self.connectivity_ids[self.index_allpre]

        if self.connectivity_postonly_ids is None:
            self.connectivity_postonly_ids = self.connectivity_ids[self.index_allpost]

        for skeleton_id in skeleton_id_list:

            print "... skeleton id", skeleton_id
            # retrieve skeleton indices for the skeleton ids from vertices_index
            if skeleton_id in self.skeleton_selection:
                print "micro: call deselect"
                self.skeleton.deselect( skeleton_id )
            else:
                print "micro: call select"
                self.skeleton.select( skeleton_id )

            if skeleton_id in self.skeleton_selection:
                print("Skeleton with id {0} already selected. Deselect".format(skeleton_id))
                selvalue = self.global_deselect_alpha
                self.skeleton_selection.remove( skeleton_id )
            else:
                print("Newly selected skeleton")
                selvalue = self.global_select_alpha
                self.skeleton_selection.append( skeleton_id )


            pre_id_index = np.where( self.connectivity_preonly_ids == skeleton_id )[0]
            self.pre_actor.set_coloralpha_index( pre_id_index , selvalue )

            post_id_index = np.where( self.connectivity_postonly_ids == skeleton_id )[0]
            self.post_actor.set_coloralpha_index( post_id_index , selvalue )


    def draw(self):
        self.pre_actor.draw()
        self.post_actor.draw()
        self.skeleton.draw()