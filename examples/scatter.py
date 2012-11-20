import sys
import numpy as np
from fos import *

w = Window(caption = '[F]OS')

scene = Scene( scenename = "Main" )

data = np.random.random( (1000, 3) ) * 200 - 50
values = np.random.random( (1000, 1) ) * 10 - 5

point_actor = Scatter( "MySphere", data[:,0], data[:,1], data[:,2], values, iterations = 2 ) 
scene.add_actor(point_actor)

w.add_scene (scene)
w.refocus_camera()
