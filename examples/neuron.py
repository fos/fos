import h5py
import sys
import os.path as op
from fos import *
import numpy as np

from PySide.QtGui import QApplication

a=np.loadtxt(op.join(op.dirname(__file__), "data", "rat-basal-forebrain.swc") )

pos = a[:,2:5].astype( np.float32 )
radius = a[:,5].astype( np.float32 ) * 4

# extract parent connectivity and create full connectivity
parents = a[1:,6] - 1
parents = parents.astype(np.uint32).T
connectivity = np.vstack( (parents, np.arange(1, len(parents)+1) ) ).T.ravel().astype(np.uint32)

colors = np.random.random( ( (len(connectivity)/2, 4)) )
colors[:,3] = 1.0

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()
    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

    act = PolygonLinesSimple( name = "Neuron", vertices = pos, connectivity = connectivity, colors=colors) #, radius = radius)
    region.add_actor( act )

    w.add_region( region )

    sys.exit(app.exec_())
