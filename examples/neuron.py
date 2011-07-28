import h5py
import sys
from fos import *
import numpy as np

from PySide.QtGui import QApplication

a=np.loadtxt("/home/stephan/03a_spindle2aFI.CNG.swc")

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
    w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )

    act = PolygonLinesExtruded( name = "Neuron", vertices = pos, connectivity = connectivity, colors=colors, radius = radius)

    w.add_actor_to_region( "Main", act )

    w.add_actor_to_region( "Main", Axes() )

    sys.exit(app.exec_())
