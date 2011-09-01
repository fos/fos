import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( bgcolor = (0,0,0) )

    region = Region( regionname = "Main",
                     extent_min = np.array( [-5.0, -5, -5] ),
                     extent_max = np.array( [5, 5, 5] ) )

    vert = np.array( [[2.0,3.0,0.0]], dtype = np.float32 )
    ptr = np.array( [[.2,.2,.2]], dtype = np.float32 )

    tex = Text3D( "Text3D", vert, "Reg", 10, 2, ptr)
    
    region.add_actor( Axes( name = "3 axes", linewidth = 2.0) )
    region.add_actor( tex )

    w.add_region ( region )
    w.refocus_camera()

    sys.exit(app.exec_())
