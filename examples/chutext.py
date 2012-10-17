import sys
import numpy as np
from fos.actor.chutext import ChuText3D
from fos import *
import string
import random


w = Window( bgcolor = (0,0,0) )

region = Region( regionname = "Main",
                 extent_min = np.array( [-5.0, -5, -5] ),
                 extent_max = np.array( [5, 5, 5] ) )

vert = np.array( [[-5.0,0.0,2.0],[5.0,0.0,2.0],
                  [0.0,5.0,5.0],[0.0,-5.0,-3.0],
                  [0.0,3.0,5.0],[0.0,-3.0,5.0]
                ],dtype = np.float32 )

fontcolor = [(0,1,0),(0,1,0),(1,0,0),(1,0,0),(0,0,1),(0,0,1)]

tex = ChuText3D("ChuText3D", vert, 
                ["Left", "Right", "Superior", "Interior", "Anterior", "Posterior"], 
                fontcolor)

region.add_actor( Axes( name = "3 axes", linewidth = 2.0) )
region.add_actor( tex )

w.add_region (region)
w.refocus_camera()
