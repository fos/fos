import sys
import numpy as np
from fos import *

w = Window( width = 1200, height = 800, bgcolor = (0,0,0) )

scene = Scene( scenename = "Main",
                 extent_min = np.array( [-5.0, -5, -5] ),
                 extent_max = np.array( [5, 5, 5] ) )

scene.add_actor( Sphere( "MySphere", radius = 2, iterations = 5 ) )

w.add_scene ( scene )

w.update_light_position( -100, 0, 10)
