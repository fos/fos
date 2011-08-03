import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( width = 1200, height = 800, bgcolor = (0,0,0) )

    mytransform = IdentityTranform()

    region = Region( regionname = "Main", transform = mytransform, resolution = ("mm", "mm", "mm"),
                     extent = (np.array( [-5.0, -5, -5] ), np.array( [5, 5, 5] ) ) )

    w.add_region ( region )


    w.add_actor_to_region( "Main", Sphere( "MySphere", radius = 2, iterations = 2 ) )

    sys.exit(app.exec_())
