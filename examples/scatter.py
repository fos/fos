import sys
import numpy as np
from fos import *

w = Window()

scene = Scene( scenename = "Main",
                 extent_min = np.array( [-5.0, -5, -5] ),
                 extent_max = np.array( [5, 5, 5] ) )

data = np.random.random( (1000, 3) ) * 200 - 50
values = np.random.random( (1000, 1) ) * 10 - 5
scene.add_actor( Scatter( "MySphere", data[:,0], data[:,1], data[:,2], values, iterations = 2 ) )

w.add_scene ( scene )
w.refocus_camera()
