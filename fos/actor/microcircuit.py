import numpy as np
from pyglet.gl import *
from .base import *
from fos.actor.primitives import *
from fos.actor.scatter import *
from fos.actor.polygonlines import *

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
                        con_post = int(semanticdict["value"])

        # use the connectivity labels to extract the connectivity for the skeletons
        self.index_skeleton = np.where(self.connectivity_labels == self.con_skeleton)[0]
        self.index_allpre = np.where(self.connectivity_labels == self.con_pre)[0]
        # print "conn ids reindexed", 
        self.connectivity_ids_index = self.connectivity_ids[self.index_skeleton]
        self.connectivity_labels_index = self.connectivity_labels[self.index_skeleton]

        self.vertices = vertices
        self.connectivity = connectivity
        self.connectivity_index_old = connectivity[self.index_skeleton]
        self.vertices_skeleton = vertices[ self.connectivity_index_old.ravel() ]

        # we have a simplified connectivity now
        self.connectivity_skeleton = np.array( range(len(self.vertices_skeleton)), dtype = np.uint32 )
        self.connectivity_skeleton = self.connectivity_skeleton.reshape( (len(self.connectivity_skeleton)/2, 2) )

        # look up the start and end vertex id
        # map these to _skeleton arrays, and further to actor???

        ##########
        # Incoming connectors
        ##########

        # extract the pre connectivity and create cones
        # store the indices for to be used to create the vector scatter
        # by itself, it represent implicitly the index used to select/deselect the vectors
        self.index_pre = np.where(self.connectivity_labels == self.con_pre)[0]
        self.vertices_pre = vertices[ connectivity[self.index_pre].ravel() ]
        self.pre_p1 = self.vertices_pre[::2, :] # data is NOT copied here
        self.pre_p2 = self.vertices_pre[1::2, :]
        pren = len(self.index_pre)
        r1 = np.ones( pren, dtype = np.float32 ) * 0.2
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
        self.index_post = np.where(self.connectivity_labels == con_post)[0]
        self.vertices_post = vertices[ connectivity[self.index_post].ravel() ]
        self.post_p1 = self.vertices_post[::2, :]
        self.post_p2 = self.vertices_post[1::2, :]
        postn = len(self.index_post)
        r1 = np.zeros( postn, dtype = np.float32 )
        r2 = np.ones( postn, dtype = np.float32 ) * 0.2
        if isinstance(connectivity_colormap, dict) and connectivity_colormap.has_key( con_post ):
            postval = np.ones( postn, dtype = np.dtype(type(con_post)) ) * con_post
        else:
            postval = None
        self.post_actor = VectorScatter( "PostConnector", self.post_p1, self.post_p2, r1, r2, values = postval,
                                         resolution = 8, colormap = connectivity_colormap )

        ##########
        # Skeletons
        ##########
        self.polylines = PolygonLinesSimple( name = "Polygon Lines",
                                             vertices = self.vertices_skeleton,
                                             connectivity = self.connectivity_skeleton )

    def deselect_all(self):
        """
        Sets the alpha value of all polygon lines to 0.2
        """
        self.pre_actor.set_coloralpha_all( alphavalue = 0.2 )
        self.post_actor.set_coloralpha_all( alphavalue = 0.2 )
        self.polylines.set_coloralpha_all( alphavalue = 0.2 )

    def select_skeleton(self, skeleton_id_list, value = 1.0 ):

        # TODO: retrieve indices with con_pre type and skeleton_id
        print "select..."
        for skeleton_id in skeleton_id_list:
            print "... skeleton id", skeleton_id
            # retrieve skeleton indices for the skeleton ids from vertices_index
            skeleton_id_index = np.where( self.connectivity_ids_index == skeleton_id )[0]

            print "skeleton id index", skeleton_id_index
            print "another", np.where( (self.connectivity_labels_index == self.con_skeleton) & (self.connectivity_ids_index == skeleton_id) )[0]

            self.polylines.select_vertices( vertices_indices = skeleton_id_index, value = value )

            # retrieve skeleton indices for the skeleton ids from connectivity_index
            # preidxlist = np.where(self.connectivity_index[:,0] == skeleton_id)[0]
            # self.pre_actor.set_coloralpha_index( preidxlist , 1.0 )
            
            
            print self.connectivity_ids_index
            print skeleton_id

            preidxlist =  np.where( (self.connectivity_labels[self.index_allpre] == self.con_pre) & (self.connectivity_ids_index == skeleton_id) )[0]
            # preidxlist = np.where(self.connectivity_index[:,0] == skeleton_id)[0]
            self.pre_actor.set_coloralpha_index( preidxlist , 1.0 )

            #postidxlist = np.where(self.connectivity_index[:,0] == skeleton_id)[0]

            #self.post_actor.set_coloralpha_index( postidxlist , 1.0 )


    def draw(self):

        self.pre_actor.draw()
        self.post_actor.draw()
        self.polylines.draw()