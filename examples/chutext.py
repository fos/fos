import sys
import numpy as np
from fos.actor.chutext import ChuText3D
from fos import *

w = Window( bgcolor = (0,0,0) )

region = Region( regionname = "Main",
                 extent_min = np.array( [-5.0, -5, -5] ),
                 extent_max = np.array( [5, 5, 5] ) )

vert = np.array( [[2.0,3.0,0.0],[5.0,5.0,0.0]], dtype = np.float32 )
width =np.array([1.5,1.5],dtype=np.int32)
heigh = np.array([2,2],dtype=np.int32)
linewidth = np.array([1.5,0.5],dtype=np.float32)
fontcolor = [(0,1,0),(1,0,0)]
#pointercolor = [(1,1,1),(0,0,1)]

#ptr = np.array( [[.2,.2,.2],[-5.,-5.,-5.]], dtype = np.float32 )

#vert = np.array( [[2.0,3.0,0.0]], dtype = np.float32 )
#ptr = np.array( [[.2,.2,.2]], dtype = np.float32 )
#width =np.array([10],dtype=np.int32)
#heigh = np.array([2],dtype=np.int32)
#linewidth = np.array([2.0],dtype=np.float32)
#fontcolor = [(1,1,1)]
#pointercolor = [(1,1,1)]

tex = ChuText3D("ChuText3D",2, vert, ["Lefeeg", "Rittttg"], width, heigh,linewidth, fontcolor)
#, pointercolor)#,ptr)

region.add_actor( Axes( name = "3 axes", linewidth = 2.0) )
region.add_actor( tex )

w.add_region (region)
w.refocus_camera()
