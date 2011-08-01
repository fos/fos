import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    mytransform = IdentityTranform()

    region = Region( regionname = "Main", transform = mytransform, resolution = ("mm", "mm", "mm"),
                     extent = (np.array( [-5.0, -5, -5] ), np.array( [5, 5, 5] ) ) )

    w.add_region ( region )


    w.add_actor_to_region( "Main", Cylinder( "MySphere", np.array([-5,0,6]), np.array([0,5,0]), 1, 1, 10 ) )

    sys.exit(app.exec_())
