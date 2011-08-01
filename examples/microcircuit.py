import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm"),
                     extent = (np.array( [-5.0, -5, -5] ), np.array( [5, 5, 5] ) ) )

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [5,10,0],
                       [10,5,0],
                       [15,5,0],
                       [12,3,0]], dtype = np.float32 )
    conn = np.array( [ 0, 1, 1, 2, 1, 3, 4, 5 ], dtype = np.uint32 )

    # each vertex is labeled with a skeleton id
    vert_skeleton_labels = np.array( [1, 1, 1, 1, 2, 2] )

    # each vertex has an unique ID
    vert_ids = np.array( [1, 2, 3, 4, 5, 6] )

    # connectors
    cvert = np.array( [[12.5,5,0],
                       [5.5,5,0]], dtype = np.float32 )
    cvert_type = np.array( [1, 2] )
    cvert_size = np.array( [5, 8] )
    cvert_ids = np.array( [144, 212] )

    # topological relation between skeleton vertices and connector
    svert_cvert = np.array( [ [4, 144], [5, 144], [5, 212] ], dtype = np.uint32 )
    # e.g. pre / postsynaptic
    svert_cvert_type = np.array( [ [5, 6, 5]] )

    act = PolygonLines( name = "Polygon Lines", vertices = vert, connectivity = conn)
    region.add_actor( act )

    w.add_region ( region )

    w.add_actor_to_region( "Main", Sphere( "MySphere", radius = 2, iterations = 2 ) )

    sys.exit(app.exec_())