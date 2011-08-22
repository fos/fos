import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( dynamic = True )

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

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

    sel = np.array( [ 100, 123, 400] , dtype = np.uint32 )

    rad = np.array( [ 1.0, 5.0, 10.0] , dtype = np.float32 )

    act = Skeleton( name = "Skeleton", \
                    vertices = vert, \
                    connectivity = conn, \
                    colors = cols,\
                    ID = sel,
                    radius = rad,
                    extruded = True)

    region.add_actor( act )

    w.add_region( region )
    w.refocus_camera()

    act.deselect()

    sys.exit(app.exec_())
