from fos import *
import numpy as np

# testcircuit from the microcircuit package
from microcircuit.dataset.testcircuit002 import testcircuit as tc

con_prob = {
    "label" : { "data" : np.ones( (tc.vertices.shape[0],1), ),
                "metadata" : {
                    "semantics" : [
                        { "name" : "skeleton", "value" : "1" },
                        { "name" : "presynaptic", "value" : "2" },
                        { "name" : "postsynaptic", "value" : "3" }
                    ]
                }
              },
    "id" : { "data" : np.array(range(tc.vertices.shape[0])), "metadata" : { } }
}

w = Window( )
scene = Scene( scenename = "Main" )

act = Microcircuit(
    name = "Testcircuit",
    vertices = tc.vertices,
    connectivity = tc.connectivity,
    #vertices_properties = vertices_properties,
    connectivity_properties = con_prob,
    #connectivity_colormap = conn_color_map
)
scene.add_actor( act )
scene.add_actor( Axes( name = "3 axes", linewidth = 5.0) )

w.add_scene ( scene )

w.refocus_camera()