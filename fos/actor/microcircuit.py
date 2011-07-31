import numpy as np
from pyglet.gl import *
from .base import *

class Microcircuit(Actor):

    def __init__(self, name ):
        """ A microcircuitry actor consisting of skeletons, connectors
        and pre and post connectivity
        """

        # for skeletons
        # - vertices
        # - connectivity
        # - skeleton_properties (labels, ...)

        # for connectors
        # - vertices
        # - connector_properties (labels, ...)
        
        # skeleton (tree)node with connectors
        # - connectivity
        # - t_c_properties (pre, post)

        # need to create basic primitives
        # sphere, tube, cone