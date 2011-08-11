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
                    connectivity_labels = self.connectivity_properties["label"]["data"]

                for semanticdict in self.connectivity_properties["label"]["metadata"]["semantics"]:
                    # name needs to be based on convention, TODO: best from ontology id rather than string!
                    if semanticdict.has_key("name"):
                        name = semanticdict["name"]
                    if "skeleton" in name:
                        con_skeleton = int(semanticdict["value"])
                    elif "presynaptic" in name:
                        con_pre = int(semanticdict["value"])
                    elif "postsynaptic" in name:
                        con_post = int(semanticdict["value"])

        # use the connectivity labels to extract the connectivity for the skeletons
        self.vertices = vertices[ connectivity[np.where(connectivity_labels == con_skeleton)[0]].ravel() ]
        
        # we have a simplified connectivity now
        self.connectivity = np.array( range(len(self.vertices)), dtype = np.uint32 )

        # extract the pre connectivity and create cones
        preloc = vertices[ connectivity[np.where(connectivity_labels == con_pre)[0]].ravel() ]
        p1 = preloc[::2, :]
        p2 = preloc[1::2, :]
        r1 = np.ones( len(preloc/2), dtype = np.float32 ) * 0.2
        r2 = np.zeros( len(preloc/2), dtype = np.float32 )
        if isinstance(connectivity_colormap, dict) and connectivity_colormap.has_key( con_pre ):
            preval = np.ones( len(preloc/2), dtype = np.dtype(type(con_pre)) ) * con_pre
        else:
            preval = None

        self.pre_actor = VectorScatter( "PreConnector", p1, p2, r1, r2, values = preval, resolution = 8, colormap = connectivity_colormap )

        # extract the post connectivity and create cones
        postloc = vertices[ connectivity[np.where(connectivity_labels == con_post)[0]].ravel() ]
        p1 = postloc[::2, :]
        p2 = postloc[1::2, :]
        r1 = np.zeros( len(postloc/2), dtype = np.float32 )
        r2 = np.ones( len(postloc/2), dtype = np.float32 ) * 0.2
        if isinstance(connectivity_colormap, dict) and connectivity_colormap.has_key( con_pre ):
            postval = np.ones( len(postloc/2), dtype = np.dtype(type(con_post)) ) * con_post
        else:
            postval = None
            
        self.post_actor = VectorScatter( "PostConnector", p1, p2, r1, r2, values = postval, resolution = 8, colormap = connectivity_colormap )

        self.polylines = PolygonLinesSimple( name = "Polygon Lines", vertices = self.vertices, connectivity = self.connectivity)

    def deselect_all(self):
        """
        Sets the alpha value of all polygon lines to 0.2
        """
        self.pre_actor.set_coloralpha_all( alphavalue = 0.2 )
        self.post_actor.set_coloralpha_all( alphavalue = 0.2 )
        self.polylines.set_coloralpha_all( alphavalue = 0.2 )

    def select_skeleton(self, skeleton_id_list, value = 1.0 ):

        # TODO: retrieve indices with con_pre type and skeleton_id

        for skeleton_id in skeleton_id_list:

            # retrieve skeleton indices for the skeleton ids from vertices_index

            # retrieve skeleton indices for the skeleton ids from connectivity_index
            preidxlist = np.where(self.connectivity_index[:,0] == skeleton_id)[0]
            self.pre_actor.set_coloralpha_index( preidxlist , 1.0 )


    def draw(self):

        self.pre_actor.draw()
        self.post_actor.draw()
        self.polylines.draw()