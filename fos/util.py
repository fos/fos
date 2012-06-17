import numpy as np

def reindex_connectivity( vert, conn):
    vert = vert[conn.ravel(),:]
    conn = np.array( range(len(vert)), dtype = np.uint32 )
    conn = conn.reshape( (len(conn)/2, 2) )
    return vert, conn

import matplotlib.delaunay as triang

def find_triangulation2d(x,y):
    cens,edg,tri,neig = triang.delaunay(x,y)
    return tri
