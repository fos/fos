import sys
import numpy as np
from fos import *

w = Window( dynamic = True )

region = Region( regionname = "Main" )

vert = np.array( [ [0,0,0],
                   [5,5,0],
                   [5,10,0],
                   [10,5,0]], dtype = np.float32 )

conn = np.array( [ [0, 1],
                   [1, 2],
                   [1, 3] ], dtype = np.uint32 )

cols = np.array( [ [0, 0, 1, 1.0],
                   [1, 0, 0, 1.0],
                   [0, 1, 0, 1.0]] , dtype = np.float32 )

cols1 = np.array( [ [1, 0, 1, 1.0],
                   [1, 1, 0, 1.0],
                   [0, 0, 1, 1.0]] , dtype = np.float32 )


sel = np.array( [ 100, 123, 400] , dtype = np.uint32 )

rad = np.array( [ 1.0, 5.0, 10.0] , dtype = np.float32 )

act = Skeleton( name = "Skeleton",
                vertices = vert,
                connectivity = conn,
                connectivity_colors = cols,
                connectivity_ID = sel,
                connectivity_radius = rad,
                extruded = False )

region.add_actor( act )

w.add_region( region )
w.refocus_camera()

# act.deselect()
