# Need to start with ipython --gui qt
# Shows a Shader

import numpy as np

from fos import *

w = Window()
w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )
w.show()


def a():
    global w

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [5,10,0],
                       [10,5,0]], dtype = np.float32 )

    conn = np.array( [ 0, 1, 1, 2, 1, 3 ], dtype = np.uint32 )

    cols = np.array( [ [0, 0, 1, 1],
                       [1, 0, 1, 1],
                       [0, 0, 1, 0.5]] , dtype = np.float32 )

    act = PolygonLines(vertices = vert, connectivity = conn, colors = cols)

    w.add_actor_to_region( "Main", act )
    return act


