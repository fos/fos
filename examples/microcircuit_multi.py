import h5py
import sys
import os.path as op
from fos import *
import numpy as np

a=np.loadtxt(op.join(op.dirname(__file__), "data", "rat-basal-forebrain.swc") )

pos = a[:,2:5].astype( np.float32 )
radius = a[:,5].astype( np.float32 ) * 4

# extract parent connectivity and create full connectivity
parents = a[1:,6] - 1
parents = parents.astype(np.uint32).T
connectivity = np.vstack( (parents, np.arange(1, len(parents)+1) ) ).T.astype(np.uint32)

colors = np.random.random( ( (len(connectivity)/2, 4)) )
colors[:,3] = 1.0

# displace neuron
pos2 = pos.copy()
pos2[:,0] += 20.0
pos2[:,1] += 2.0
pos2[:,2] += 2.0
lpos = len(pos)

# create connectors, select a few points
nc = 30
idx = np.random.random_integers(0, len(pos)-1, (nc,))
conpos = (pos[idx,:] + pos2[idx,:]) / 2

vertbig = np.concatenate( (pos, pos2, conpos) )

labels = np.ones( (len(vertbig),1), dtype = np.uint32 )
labels[-nc] = 2

# connectivity
ll = len(connectivity)*2+2*nc
con = np.zeros( (ll, 2), dtype = np.uint32)
con_lab = np.ones( (ll), dtype = np.uint32)
con_ids = np.ones( (ll), dtype = np.uint32)

lenc = len(connectivity)
con[0:lenc,:] = connectivity
con_ids[0:lenc] = 101
con[lenc:2*lenc,:] = connectivity + lpos
con_ids[lenc:2*lenc] = 102

con_lab[2*lenc:(2*lenc)+nc:] = np.ones( (nc,), dtype = np.uint32 ) * 2
con_ids[2*lenc:(2*lenc)+nc:] = np.ones( (nc,), dtype = np.uint32 ) * 101
con_lab[(2*lenc)+nc:] = np.ones( (nc,), dtype = np.uint32 ) * 3
con_ids[(2*lenc)+nc:] = np.ones( (nc,), dtype = np.uint32 ) * 102

con[2*lenc:(2*lenc)+nc, 0] = idx # from
con[2*lenc:(2*lenc)+nc, 1] = np.arange(0,nc) + 2*lpos # to

con[(2*lenc)+nc:, 0] = idx + lpos # from
con[(2*lenc)+nc:, 1] = np.arange(0,nc) + 2*lpos # to

w = Window( dynamic = True )

region = Region( regionname = "Main" )

conn_color_map = {
    1 : np.array([[0.0, 1.0, 1.0, 1.0]]),
    2 : np.array([[1.0, 0.0, 1.0, 1.0]]),
    3 : np.array([[0, 1.0, 1.0, 1.0]])
}

# new
vertices_properties = {
    "label" : { "data" : labels, "metadata" : {} }
}
connectivity_properties = {
    "label" : { "data" : con_lab,
                "metadata" : {
                    "semantics" : [
                        { "name" : "skeleton", "value" : "1" },
                        { "name" : "presynaptic", "value" : "2" },
                        { "name" : "postsynaptic", "value" : "3" }
                    ]
                }
              },
    "id" : { "data" : con_ids, "metadata" : { } }
}
act = Microcircuit(
    name = "Simple microcircuitry",
    vertices = vertbig,
    connectivity = con,
    vertices_properties = vertices_properties,
    connectivity_properties = connectivity_properties,
    connectivity_colormap = conn_color_map
)
region.add_actor( act )
region.add_actor( Axes( name = "3 axes", linewidth = 5.0) )

w.add_region( region )

act.deselect_all( 0.2 )
#act.select_skeleton( [101], 1.0 )

w.refocus_camera()
