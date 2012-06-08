import numpy as np
from pyglet.gl import *
from .base import *
from fos.actor.primitives import *
from fos.actor.skeleton import *
from fos.actor.scatter import *

from PySide.QtGui import QMatrix4x4

from fos.shader.lib import *
from fos.vsml import vsml

import microcircuit as mc

DEBUG=True

class Microcircuit(Actor):

    def __init__(self,
             name,
             vertices_location,
             connectivity,
             connectivity_ids=None,
             connectivity_label=None,
             connectivity_label_metadata=None,
             connectivity_colormap = None,
             connector_size=2.6,
             global_deselect_alpha=0.2,
             global_select_alpha=1.0,
             skeleton_linewidth=2.0):
        """ A Microcircuit actor with skeletons, connectors and incoming
        and outgoing connectivity

        name : str
            The name of the actor
        vertices : Nx3
            3D Coordinates x,y,z
        connectivity : Mx1
            Tree topology, using indices into the vertices array

        Notes
        -----
        Only create this actor when a valid OpenGL context exists.
        Uses Vertex-Buffer objects and propagate shaders.
        """
        super(Microcircuit, self).__init__( name )

        if not connectivity_ids is None:
            self.connectivity_ids = connectivity_ids

        if not connectivity_label is None:
            self.connectivity_labels = connectivity_label

            if not connectivity_label_metadata is None:

                for semanticdict in connectivity_label_metadata:
                    # name needs to be based on convention, TODO: best from ontology id rather than string!
                    # TODO: use microcircuit convention
                    if semanticdict.has_key("name"):
                        name = semanticdict["name"]
                    if "skeleton" in name:
                        self.con_skeleton = int(semanticdict["value"])
                    elif "presynaptic" in name:
                        self.con_pre = int(semanticdict["value"])
                    elif "postsynaptic" in name:
                        self.con_post = int(semanticdict["value"])

            else:
                # TODO: default
                self.con_skeleton = 1
                self.con_pre = 2
                self.con_post = 3

        # selection stores integer ids from connectivity_selectionID
        # when selected
        self.skeleton_selection = []

        # use the connectivity labels to extract the connectivity for the skeletons
        self.index_skeleton = np.where(self.connectivity_labels == self.con_skeleton)[0]
        self.index_allpre = np.where(self.connectivity_labels == self.con_pre)[0]
        self.index_allpost = np.where(self.connectivity_labels == self.con_post)[0]
        
        self.vertices = vertices_location
        self.connectivity = connectivity

        connectivity_skeleton = self.connectivity[self.index_skeleton]
        self.vertices_skeleton = self.vertices[ connectivity_skeleton.ravel() ]
        
        # we have a simplified connectivity now
        self.connectivity_skeleton = np.array( range(len(self.vertices_skeleton)), dtype = np.uint32 )
        self.connectivity_skeleton = self.connectivity_skeleton.reshape( (len(self.connectivity_skeleton)/2, 2) )
        self.connectivity_ids_skeleton = self.connectivity_ids[ self.index_skeleton ]

        # look up the start and end vertex id
        # map these to _skeleton arrays, and further to actor???

        # colors for skeletons
        if isinstance(connectivity_colormap, dict) and connectivity_colormap.has_key( self.con_skeleton ):
            self.connectivity_skeleton_colors = np.repeat(connectivity_colormap[self.con_skeleton], len(self.connectivity_skeleton), axis=0).astype( np.float32 )

        ##########
        # Incoming connectors
        ##########

        # extract the pre connectivity and create cones
        # store the indices for to be used to create the vector scatter
        # by itself, it represent implicitly the index used to select/deselect the vectors
        if len(self.index_allpre) == 0:
            if DEBUG:
                print "no presynaptic connection"
            self.pre_actor = None
        else:
            self.vertices_pre = self.vertices[ connectivity[self.index_allpre].ravel() ]
            self.pre_p1 = self.vertices_pre[::2, :] # data is NOT copied here
            self.pre_p2 = self.vertices_pre[1::2, :]
            pren = len(self.index_allpre)
            r1 = np.ones( pren, dtype = np.float32 ) * connector_size
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
        if len(self.index_allpost) == 0:
            if DEBUG:
                print "no postsynaptic connection"
            self.post_actor = None
        else:
            self.vertices_post = self.vertices[ connectivity[self.index_allpost].ravel() ]
            self.post_p1 = self.vertices_post[::2, :]
            self.post_p2 = self.vertices_post[1::2, :]
            postn = len(self.index_allpost)
            r1 = np.zeros( postn, dtype = np.float32 )
            r2 = np.ones( postn, dtype = np.float32 ) * connector_size
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
                     connectivity_colors = self.connectivity_skeleton_colors,
                     connectivity_ID = self.connectivity_ids_skeleton,
                     linewidth = skeleton_linewidth,
                     global_deselect_alpha = global_deselect_alpha,
                     global_select_alpha = global_select_alpha )

        self.connectivity_skeletononly_ids = None
        self.connectivity_preonly_ids = None
        self.connectivity_postonly_ids = None

        self.global_deselect_alpha = global_deselect_alpha
        self.global_select_alpha = global_select_alpha

    def pick(self, x, y):
        ID = self.skeleton.pick( x, y )
        if DEBUG:
            print "pick skeleton id", ID

        if ID is None or ID == 0:
            return
        self.select_skeleton( [ ID ] )

    def deselect_all(self, value=None):
        """
        Sets the alpha value of all polygon lines to 0.2
        """
        if value is None:
            value=self.global_deselect_alpha
        self.skeleton_selection = []
        if self.pre_actor:
            self.pre_actor.set_coloralpha_all( alphavalue = value )
        if self.post_actor:
            self.post_actor.set_coloralpha_all( alphavalue = value )
        self.skeleton.deselect( )

    def select_skeleton(self, skeleton_id_list ):
        if DEBUG:
            print "select skeleton..."
        if self.connectivity_skeletononly_ids is None:
            self.connectivity_skeletononly_ids = self.connectivity_ids[self.index_skeleton]

        if self.connectivity_preonly_ids is None:
            self.connectivity_preonly_ids = self.connectivity_ids[self.index_allpre]

        if self.connectivity_postonly_ids is None:
            self.connectivity_postonly_ids = self.connectivity_ids[self.index_allpost]

        for skeleton_id in skeleton_id_list:
            if DEBUG:
                print "... skeleton id", skeleton_id
            # retrieve skeleton indices for the skeleton ids from vertices_index
            if skeleton_id in self.skeleton_selection:
                if DEBUG:
                    print "micro: call deselect"
                self.skeleton.deselect( skeleton_id )
            else:
                if DEBUG:
                    print "micro: call select"
                self.skeleton.select( skeleton_id )

            if skeleton_id in self.skeleton_selection:
                if DEBUG:
                    print("Skeleton with id {0} already selected. Deselect".format(skeleton_id))
                selvalue = self.global_deselect_alpha
                self.skeleton_selection.remove( skeleton_id )
            else:
                if DEBUG:
                    print("Newly selected skeleton")
                selvalue = self.global_select_alpha
                self.skeleton_selection.append( skeleton_id )

            if not self.pre_actor is None:
                pre_id_index = np.where( self.connectivity_preonly_ids == skeleton_id )[0]
                self.pre_actor.set_coloralpha_index( pre_id_index , selvalue )

            if not self.post_actor is None:
                post_id_index = np.where( self.connectivity_postonly_ids == skeleton_id )[0]
                self.post_actor.set_coloralpha_index( post_id_index , selvalue )


    def draw(self):
        if self.pre_actor:
            self.pre_actor.draw()
        if self.post_actor:
            self.post_actor.draw()
        self.skeleton.draw()
