import sys
import numpy as np
from fos import *

w = Window( dynamic = True )

region = Region( regionname = "Main" )

vert = np.array( [ [0,0,0], # skeleton node
                   [5,5,0], # skeleton node
                   [10,3,0], # connector
                   [15,5,0], # skeleton node
                   [18,0,0]], # skeleton node
                   dtype = np.float32 )

vert_labels = np.array( [1, 1, 2, 1, 1], dtype = np.uint32 )
vert_nodeides = np.array( [10, 11, 200, 20, 21], dtype = np.uint32 )

vert_skeleton_index = np.array( [
    [400, 0, 1], # skeleton with id 400 from 0 to 1
    [500, 3, 4], # skeleton with id 500 from 3 to 4
])

vertices_properties = {
    "label" : { "data" : vert_labels, "metadata" : {} },
    "id" : { "data" : vert_nodeides }
}

vertices_grouping = {
    "index" : { "data" : vert_skeleton_index }
}

conn = np.array( [ [0, 1], # parent
                   [1, 2], # presyn
                   [3, 2], # postsyn
                   [3, 4] ], # parent
                   dtype = np.uint32 )

# labels parent relations of skeletons, and pre and postsynaptic connections
conn_labels = np.array( [1, 2, 3, 1], dtype = np.uint32 )
# to store the skeleton ID for each skeleton node is very redundant,
# it would be faster with an index into the array (but more complicated to implement)
# we hope for future numpy (group_by) magic to implement this efficiently
# count the pre/post to the skeleton id!
conn_ids = np.array( [100, 100, 500, 500], dtype = np.uint32 )

conn_skeleton_index = np.array( [ [400, 0, 1], # skeleton with id 400 from 0 to 1
                                  [500, 2, 3], # skeleton with id 500 from 3 to 4
])

# colormap as dictionary with labels
conn_color_map = {
    1 : np.array([[1.0, 1.0, 0, 1.0]]),
    2 : np.array([[1.0, 0.0, 0, 1.0]]),
    3 : np.array([[0, 0, 1.0, 1.0]])
}

# TODO: best solution?
conn_color_map_skeleton= {
    400 : np.array([[0.8, 0.5, 0.2, 1.0]]),
    500 : np.array([[0.4, 0.3, 0, 1.0]])
}

act = Microcircuit(
    name="Testcircuit",
    vertices_location=vert,
    connectivity=conn,
    connectivity_ids=conn_ids,
    connectivity_label=conn_labels,
    connectivity_label_metadata=[
                        { "name" : "skeleton", "value" : "1" },
                        { "name" : "presynaptic", "value" : "2" },
                        { "name" : "postsynaptic", "value" : "3" }
                    ],
    connectivity_colormap=conn_color_map,
    connector_size=0.2,
    skeleton_linewidth=30.0
)

region.add_actor( act )
region.add_actor( Axes( name = "3 axes", linewidth = 5.0) )

w.add_region ( region )

act.deselect_all()

#act.select_skeleton( [400,500], 0.90 )

w.refocus_camera()
