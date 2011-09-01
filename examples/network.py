import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region( regionname = "Main",
                     extent_min = np.array( [-5.0, -5, -5] ),
                     extent_max = np.array( [5, 5, 5] ) )

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [5,10,0],
                       [10,5,0]], dtype = np.float32 )

    conn = np.array( [ [0, 1],
                       [1, 2],
                       [1, 3] ], dtype = np.uint32 )

    val = np.array( [ 1.0, 5.0, 10.0, 5.0], dtype = np.float32 )

    region.add_actor( Network( "MyNetwork", vertices = vert, edges = conn, values = val  ) )

    w.add_region ( region )

    sys.exit(app.exec_())