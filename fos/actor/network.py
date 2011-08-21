import numpy as np
from pyglet.gl import *
from .base import Actor

from fos.actor.primitives import *
from fos.actor.scatter import *

class Network(Actor):

    def __init__(self, name, positions, edges, **kwargs):
        """ Network Actor
        """
        super(Network, self).__init__( name )

        # a NodeScatter for nodes
        self.vertices = np.random.random( (1000, 3) ) * 100 - 50
        values = np.random.random( (1000, 1) ) * 10 - 5

        self.node_scatter = Scatter( "CubeScatter", self.vertices[:,0], self.vertices[:,1], self.vertices[:,2], \
                                     values, type = 'cube' )

        # a VectorScatter for edges
        # TODO: should be polygonlines, or VectorScatters?
        self.edge_scatter = None

    def draw(self):
        self.node_scatter.draw()
        #self.edge_scatter.draw()