import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( width = 1200, height = 800, bgcolor = (0,0,0) )

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm"),
                     extent_min = np.array( [-5.0, -5, -5] ), extent_max = np.array( [5, 5, 5] )  )

    region.add_actor( Sphere( "MySphere", radius = 2, iterations = 5 ) )

    w.add_region ( region )

    w.update_light_position( -100, 0, 10)

    sys.exit(app.exec_())
