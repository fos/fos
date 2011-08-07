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
             vertices_labels,
             connectivity_labels,
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

        # TODO: simplify by reusing the PolygonLines actor in here!

        if affine is None:
            self.affine = np.eye(4, dtype = np.float32)
        else:
            self.affine = affine

        # TODO: hard-coded values
        con_skeleton = 1
        con_pre = 2
        con_post = 3

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
        self.pre_actor = ScatterCylinder( "PreConnector", p1, p2, r1, r2, resolution = 8, wireframe = False )

        # extract the post connectivity and create cones
        postloc = vertices[ connectivity[np.where(connectivity_labels == con_post)[0]].ravel() ]
        p1 = postloc[::2, :]
        p2 = postloc[1::2, :]
        r1 = np.zeros( len(postloc/2), dtype = np.float32 )
        r2 = np.ones( len(postloc/2), dtype = np.float32 ) * 0.2
        self.post_actor = ScatterCylinder( "PostConnector", p1, p2, r1, r2, resolution = 8 )

        self.polylines = PolygonLinesSimple( name = "Polygon Lines", vertices = self.vertices,
                                             connectivity = self.connectivity)

    def draw(self):

        self.pre_actor.draw()
        self.post_actor.draw()
        self.polylines.draw()