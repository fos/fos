import sys
import numpy as np
from fos import *
import fos.util

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [5,10,0],
                       [10,5,0]], dtype = np.float32 )

    conn = np.array( [ 0, 1, 1, 2, 1, 3 ], dtype = np.uint32 )

    cols = np.array( [ [0, 0, 1, 0.7],
                       [1, 0, 1, 0.1],
                       [0, 0, 1, 0.5]] , dtype = np.float32 )

    vert, conn = fos.util.reindex_connectivity( vert, conn )

    act = PolygonLinesSimple( name = "Polygon Lines", vertices = vert, connectivity = conn, colors = cols)

    region.add_actor( act )

    w.add_region( region )

    sys.exit(app.exec_())
