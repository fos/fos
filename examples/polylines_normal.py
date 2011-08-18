import sys
import numpy as np
from fos import *


from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [5,10,0],
                       [10,5,0]], dtype = np.float32 )

    conn = np.array( [ [0, 1],
                       [1, 2],
                       [1, 3] ], dtype = np.uint32 )

    cols = np.array( [ [0, 0, 1, 1],
                       [1, 0, 1, 1],
                       [0, 0, 1, 0.5]] , dtype = np.float32 )

    sel = np.array( [ 100, 200, 200] , dtype = np.uint32 )

    # wanna color the edges
    vert = vert[conn.ravel(),:]
    conn = np.array( range(len(vert)), dtype = np.uint32 )
    conn = conn.reshape( (len(conn)/2, 2) )

    act = PolygonLines( name = "Polygon Lines", vertices = vert, connectivity = conn, colors = cols, connectivity_selectionID = sel)

    region.add_actor( act )

    w.add_region( region )
    w.refocus_camera()
    
    sys.exit(app.exec_())
