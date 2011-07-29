import sys
from fos import *
import numpy as np
from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()
    w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [5,10,0],
                       [10,5,0]], dtype = np.float32 )

    conn = np.array( [ 0, 1, 1, 2, 1,3 ], dtype = np.uint32 )

    cols = np.array( [ [0, 0, 1, 1],
                       [1, 0, 1, 1],
                       [0, 0, 1, 0.5]] , dtype = np.float32 )

    rad = np.array( [4,4,4,10], dtype = np.float32 )

    act = PolygonLinesExtruded( name = "Extrude Polylines", vertices = vert, connectivity = conn, colors = cols, radius = rad)
    w.add_actor_to_region( "Main", act )

    sys.exit(app.exec_())
