import numpy as np
from pyglet.gl import *
from .base import Actor

from fos.actor.skeleton import *
from fos.actor.scatter import *

class Network(Actor):

    def __init__(self, name, vertices, edges, values, **kwargs):
        """ Network Actor
        """
        super(Network, self).__init__( name )

        # a NodeScatter for nodes
        self.vertices = vertices
        self.connectivity = edges
        self.values = values
        self.node_scatter = Scatter( "CubeScatter", self.vertices[:,0], self.vertices[:,1], self.vertices[:,2],
                                     self.values, type = 'cube' )

        # a Skeleton for edges
        self.edge_scatter = Skeleton( "EdgeSkeleton", self.vertices, self.connectivity )

    def draw(self):
        self.node_scatter.draw()
        self.edge_scatter.draw()