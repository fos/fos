from fos import *
import numpy as np

import h5py
f=h5py.File('/tmp/6yftk50u9(iifdqa0p=0ucv55i29p5qhjxsxtf+_v)xd4f8+nx.h5', 'r')

vertices_id = f['Microcircuit']['vertices']['id'].value
vertices_location = f['Microcircuit']['vertices']['location'].value
connectivity_id = f['Microcircuit']['connectivity']['id'].value
connectivity_skeletonid = f['Microcircuit']['connectivity']['skeletonid'].value
connectivity_type = f['Microcircuit']['connectivity']['type'].value

print connectivity_type
vertices_location = ((vertices_location - np.mean(vertices_location, axis=0))).astype(np.float32)

def map_vertices_id2index(vertices_id):
    map_vertices_id2index = dict(zip(vertices_id,range(len(vertices_id))))
    connectivity_indices = np.zeros( connectivity_id.shape, dtype=np.uint32 )
    for i,c in enumerate(connectivity_id):
        connectivity_indices[i,0]=map_vertices_id2index[connectivity_id[i,0]]
        connectivity_indices[i,1]=map_vertices_id2index[connectivity_id[i,1]]
    return connectivity_indices

conn_color_map = {
    1 : np.array([[1.0, 1.0, 0.0, 1.0]]),
    2 : np.array([[0.0, 0.0, 1.0, 1.0]]),
    3 : np.array([[1.0, 0.0, 0.0, 1.0]])
}

w = Window( dynamic=True )

mytransform = Transform3D(np.eye(4))
mytransform.set_scale(0.1, 0.1, 0.1)

region = Region( regionname = "Main", transform = mytransform)

act = Microcircuit(
    name="Testcircuit",
    vertices_location=vertices_location,
    connectivity=map_vertices_id2index(vertices_id),
    connectivity_ids=connectivity_skeletonid,
    connectivity_label=connectivity_type,
    connectivity_label_metadata=[
                        { "name" : "skeleton", "value" : "1" },
                        { "name" : "presynaptic", "value" : "2" },
                        { "name" : "postsynaptic", "value" : "3" }
                    ],
    connectivity_colormap=conn_color_map
)

region.add_actor( act )
region.add_actor( Axes( name = "3 axes", linewidth = 5.0) )


values = np.ones( (len(vertices_location)) ) * 100
region.add_actor( Scatter( "MySphere", vertices_location[:,0], vertices_location[:,1], vertices_location[:,2], values, iterations = 2 ) )

w.add_region ( region )

act.deselect_all()

w.refocus_camera()