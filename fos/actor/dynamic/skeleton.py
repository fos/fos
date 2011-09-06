import numpy as np
from pyglet.gl import *

from ..skeleton import *
from ..base import *

class DynamicSkeleton(DynamicActor):

    def __init__(self,
             name,
             vertices,
             connectivity,
             connectivity_ID = None,
             connectivity_colors = None,
             connectivity_radius = None,
             extruded = False,
             linewidth = 3.0,
             useva = True):
        """ Dynamic skeleton, colors change over time

        connectivity_colors has a temporal (last) dimension
        """
        super(DynamicSkeleton, self).__init__( name )

        self.vertices = vertices
        self.connectivity_colors = connectivity_colors
        
        self.max_time_frame = self.connectivity_colors.shape[-1] - 1

        self.skeleton = Skeleton( name,
            vertices, connectivity, connectivity_ID, self.connectivity_colors[:,:,self.current_time_frame],
            connectivity_radius, extruded, linewidth, useva )

        self.updatePtr()

    def updatePtr(self):
        self.skeleton.update_colors( self.connectivity_colors[:,:,self.current_time_frame] )

    def draw(self):
        self.skeleton.draw()