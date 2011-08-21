import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm"),
                     extent_min = np.array( [-5.0, -5, -5] ), extent_max = np.array( [5, 5, 5] )  )

    data = np.random.random( (100, 3) ) * 100 - 50
    values = np.random.random( (100, 1) ) * 10 - 5
    conn = np.array( [ [0, 1],[1, 2],[3, 2],[3, 4] ], dtype = np.uint32 )

    region.add_actor( Network( "MyNetwork", positions = data, edges = conn  ) )

    w.add_region ( region )

    sys.exit(app.exec_())