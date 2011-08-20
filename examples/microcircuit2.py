import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

# vertices
vert = np.array( [ [0,0,0], # skeleton node
                   [5,5,0], # skeleton node
                   [10,3,0], # connector
                   [15,5,0], # skeleton node
                   [18,0,0]], # skeleton node
                   dtype = np.float32 )

# vertices property: vertices identifiers
vert_id_dict = { "data" : np.array( [10, 11, 200, 20, 21], dtype = np.uint32 ) }

# vertices property: vertices type
vert_type_dict = { "data" : np.array( [1, 1, 2, 1, 1], dtype = np.uint32 ),
                    "metadata" : {
                        "semantics" : {
                            1 : { "name" : "skeleton node" },
                            2 : { "name" : "connector node"}
                        }
                    }
}

# connectivity
conn = np.array( [ [0, 1], # axon -> blue
                   [1, 2], # presyn
                   [3, 2], # postsyn
                   [3, 4] ], # dendrite -> red
                   dtype = np.uint32 )


# connectivity property: type of connectivity
conn_type_dict = { "data" : np.array( [1, 2, 3, 4], dtype = np.uint32 ),
                   "metadata" : {
                    "type" : "categorial",
                    "semantics" : [
                        { "name" : "axon", "value" : "1" },
                        { "name" : "presynaptic", "value" : "2" },
                        { "name" : "postsynaptic", "value" : "3" },
                        { "name" : "dendrite", "value" : "4" },
                    ]
                }
}

# connectivity property: skeleton identifiers
conn_skeletonid_dict = { "data" : np.array( [100, 100, 500, 500], dtype = np.uint32 ),
                         "metadata" : {
                             "type" : "categorial"
                         }
}


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

    act = MicrocircuitNew(
        name = "Simple microcircuitry",
        
        vertices = vert,
        connectivity = conn,

        vertices_id = vert_id_dict,
        vertices_type = vert_type_dict,

        connectivity_type = conn_type_dict,
        connectivity_skeletonid = conn_skeletonid_dict,
        # connectivity_color = None
    )
    region.add_actor( act )
    region.add_actor( Axes( name = "3 axes", linewidth = 5.0) )

    w.add_region ( region )

    act.deselect()
    act.select( 'connectivity_skeletonid', [100] )
    
    w.refocus_camera()

    sys.exit(app.exec_())


