import sys
import numpy as np
from fos import *

w = Window( dynamic = True )

region = Region( regionname = "Main" )

vert = np.array( [ [0,0,0],
                   [5,5,0],
                   [5,10,0],
                   [10,5,0]], dtype = np.float32 )

conn = np.array( [ 0, 1, 1, 2, 1, 3 ], dtype = np.uint32 )

colt = np.zeros( (3,4,2), dtype = np.float32 )
colt[:,:,0] = np.array( [
                  [0, 1, 0, 1],
                  [0, 0, 1, 1],
                  [1, 0, 0, 0.5]] , dtype = np.float32 )
colt[:,:,1] = np.array( [
                  [1, 0, 1, 1.0],
                  [0, 1, 0, 0.2],
                  [0, 0, 1, 1.0]] , dtype = np.float32 )

colt = np.random.rand( 3, 4, 500 ).astype( np.float32 )

act = DynamicSkeleton( name = "Dynamic Skeleton",
                vertices = vert,
                connectivity = conn,
                connectivity_colors = colt,
                extruded = False )

region.add_actor( act )

w.add_region( region )

# act.play()
