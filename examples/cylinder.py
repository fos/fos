import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region(regionname="Main",
                    extent_min=np.array([-5.0, -5, -5]),
                    extent_max=np.array([5, 5, 5]))

    cylinder = Cylinder("MySphere",
                 np.array([-5, 0, 6]),
                 np.array([0, 5, 0]), 1, 1, 10)

    region.add_actor(cylinder)

    w.add_region(region)
    w.refocus_camera()

    sys.exit(app.exec_())
