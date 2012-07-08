import sys
import os.path as op
from fos import *
import fos.util

import numpy as np

from PySide.QtGui import QApplication

import nibabel as nib
a=nib.trackvis.read( op.join(op.dirname(__file__), "data", "tracks300.trk") )
g=np.array(a[0], dtype=np.object)
trk = [tr[0] for tr in a[0]]
#trk = trk[:10]
#g=np.array(trk, dtype=np.object)
#g=g[:200]

def prepare_tracks(trk):
    pos = []
    con = []
    cons = [] # an id for each fiber!
    offset = 0
    for i, f in enumerate(trk):
        fiblen = len(f)
        conarr = np.vstack( (np.array(range(fiblen - 1)), np.array(range(1,fiblen)) )).T.ravel()
        conarr += offset
        con.append( conarr )
        pos.append( f) #(f-f.mean(axis=0)) )
        cons.append( np.ones( (len(conarr,)), dtype = np.uint32) * (i+1)  )
        offset += fiblen
    positions = np.concatenate(pos)
    connectivity = np.concatenate(con)
    consel = np.concatenate(cons).astype( np.uint32 )    
    # varying radius
    rad = np.cumsum(np.random.randn(len(positions)))
    rad = (rad - rad.min()) + 1.0
    rad = rad / rad.max()    
    positions, connectivity = fos.util.reindex_connectivity( positions, connectivity )
    return positions, connectivity, consel

positions,connectivity,consel=prepare_tracks(trk)
cols=np.random.rand(len(connectivity),4).astype('f4') 
cols[:,-1]=1
radii= np.random.randint(1,10,len(connectivity)).astype('f4')
radii = np.ascontiguousarray(radii[:,None],'f4')

w = Window(caption='Free on shades')
region = Region( regionname = "Main" )


act = Skeleton( name = "Tractography",
               vertices = positions,
               connectivity = connectivity,
               connectivity_ID = consel)
               #connectivity_colors = cols,
               #connectivity_radius = radii)


region.add_actor( act )
w.add_region( region )
w.refocus_camera()
