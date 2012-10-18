import sys
import numpy as np
from fos import *

w = Window()

scene = Scene(scenename="Main",
                extent_min=np.array([-5.0, -5, -5]),
                extent_max=np.array([5, 5, 5]))

cylinder = Cylinder("MySphere",
             np.array([-5, 0, 6]),
             np.array([0, 5, 0]), 1, 1, 10)

scene.add_actor(cylinder)

w.add_scene(scene)
w.refocus_camera()
