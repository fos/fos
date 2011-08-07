import sys
import os.path as op
from fos import *
import numpy as np

from PySide.QtGui import QApplication

import nibabel as nib
a=nib.trackvis.read( op.join(op.dirname(__file__), "data", "tracks300.trk") )
g=np.array(a[0], dtype=np.object)
trk = [tr[0] for tr in a[0]]
g=np.array(trk, dtype=np.object)
g=g[:200]

pos = []
con = []
offset = 0
for f in g:
    fiblen = len(f)
    conarr = np.vstack( (np.array(range(fiblen - 1)), np.array(range(1,fiblen)) )).T.ravel()
    conarr += offset
    con.append( conarr )
    pos.append( (f-f.mean(axis=0)) )
    offset += fiblen
positions = np.concatenate(pos)
connectivity = np.concatenate(con)

# varying radius
rad = np.cumsum(np.random.randn(len(positions)))
rad = (rad - rad.min()) + 1.0
rad = rad / rad.max()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()
    region = Region( regionname = "Main", resolution = ("mm", "mm", "mm") )

    act = PolygonLinesSimple( name = "Tractography", vertices = positions, connectivity = connectivity) #, radius = rad)
    region.add_actor( act )
    w.add_region( region )
    w.refocus_camera()
    sys.exit(app.exec_())

