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
    region.add_actor( Scatter( "MySphere", data[:,0], data[:,1], data[:,2], values, iterations = 2 ) )

    w.add_region ( region )

    sys.exit(app.exec_())
