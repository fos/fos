import sys
import numpy as np
from fos import *
from pylab import cm

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( width = 1200, height = 800, bgcolor = (0,0,0) )

    region = Region( regionname = "Main",
                     extent_min = np.array( [-5.0, -5, -5] ),
                     extent_max = np.array( [5, 5, 5] )  )

    vert = np.array( [ [0,0,0],[5,5,0],[5,10,0]], dtype = np.float32 )
    conn = np.array( [[ 0, 1, 2 ]], dtype = np.uint32 )
    scal = np.array( [ 0.2, 2.5, 10.2 ], dtype = np.float32 )

    # use colormap to define colors array
    colormap = cm.Accent
    if isinstance( colormap, dict):
        # TODO: do the dict mapping to colors
        pass
    else:
        # TODO: fix colormapping
        colors = colormap( scal ).astype( np.float32 )
        
    print colors
    
    mesh1 = Mesh( "Triangle", vertices = vert, connectivity = conn )

    vert = np.array( [ [8,0,0],[12,5,0],[12,10,0], [0,4, 2]], dtype = np.float32 )
    conn = np.array( [[ 0, 1, 2, 3 ]], dtype = np.uint32 )
    mesh2 = Mesh( "Quad", vertices = vert, connectivity = conn, vertices_colors = colors )

    region.add_actor( mesh1 )
    region.add_actor( mesh2 )

    w.add_region ( region )
    w.refocus_camera()

    sys.exit(app.exec_())
