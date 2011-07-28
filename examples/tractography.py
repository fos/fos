import sys
from fos import *
import numpy as np

from PySide.QtGui import QApplication

import nibabel as nib
a=nib.trackvis.read('/home/stephan/data/project_atlas/PH0002/tp1/CMP/fibers/streamline_final_freesurferaparc.trk')
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
    w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )

    act = PolygonLinesExtruded( name = "Tractography", vertices = positions, connectivity = connectivity, radius = rad)

    w.add_actor_to_region( "Main", act )

    w.add_actor_to_region( "Main", Axes() )

    sys.exit(app.exec_())

