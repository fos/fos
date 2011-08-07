import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

    vert = np.array( [ [0,0,0],
                       [5,5,0],
                       [10,3,0], # connector
                       [15,5,0],
                       [18,0,0]], dtype = np.float32 )

    vert_labels = np.array( [1, 1, 2, 1, 1], dtype = np.uint32 )
    vert_nodeides = np.array( [10, 11, 200, 20, 21], dtype = np.uint32 )

    conn = np.array( [ [0, 1], # parent
                       [1, 2], # presyn
                       [3, 2], # postsyn
                       [3, 4] ], dtype = np.uint32 )

    # labels skeleton colors, and pre and postsynaptic colors
    conn_labels = np.array( [1, 2, 3, 1], dtype = np.uint32 )

    conn_color_map = {
        1 : np.array([[1.0, 1.0, 0, 1.0]]),
        2 : np.array([[1.0, 0.0, 0, 1.0]]),
        3 : np.array([[0, 0, 1.0, 1.0]])
    }
    
    act = Microcircuit( "Polygon Lines", vertices = vert,
                        connectivity = conn,
                        vertices_labels = vert_labels,
                        connectivity_labels = conn_labels,
                        connectivity_colormap = conn_color_map )
    region.add_actor( act )
    region.add_actor( Axes( name = "3 axes", linewidth = 5.0) )
    
    w.add_region ( region )

    sys.exit(app.exec_())


