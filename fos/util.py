import numpy as np

def reindex_connectivity( vert, conn):
    vert = vert[conn.ravel(),:]
    conn = np.array( range(len(vert)), dtype = np.uint32 )
    conn = conn.reshape( (len(conn)/2, 2) )
    return vert, conn
