import sys
import numpy as np
from fos import *
from pylab import cm

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( bgcolor = (0,0,0) )

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm"),
                     extent_min = np.array( [-5.0, -5, -5] ), extent_max = np.array( [5, 5, 5] )  )

    vert = np.array( [ [0,0,0]], dtype = np.float32 )
    norm = np.array( [ [0,0,1.0]], dtype = np.float32 )

    tex = Text3D( "Text3D", vert, norm, "My Text")

    region.add_actor( tex )

    w.add_region ( region )
    w.refocus_camera()

    sys.exit(app.exec_())
