# Need to start with ipython --gui qt
# Shows a Shader

from fos import *
import numpy as np

w = Window()
w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )
w.show()


def a():
    global w

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [50,5,0]], dtype = np.float32 )

    conn = np.array( [ 0, 1, 1, 2 ], dtype = np.uint32 )

    cols = np.array( [ [1, 1, 0, 0.5], [1, 1, 0, 0.5] ] , dtype = np.float32 )

    vert_width = np.array( [5, 5, 20, 20 ], dtype = np.float32 )

    act = TreeActor(vertices = vert, connectivity = conn, radius = vert_width,colors = cols)
    w.add_actor_to_region( "Main", act )
    return act
