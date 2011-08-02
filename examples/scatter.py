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

    data = np.random.random( (1, 3) ) * 100
    values = np.random.random( (1, 1) ) * 10
    region.add_actor( Scatter( "MySphere", data[:,0], data[:,1], data[:,2], values, iterations = 0 ) )

    w.add_region ( region )

    sys.exit(app.exec_())
