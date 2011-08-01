import numpy as np
from pyglet.gl import *
from fos.actor.base import Actor

def makeUVSphere( radius, ordinates = 10, abscissa = 10):

    pass
# http://paulbourke.net/miscellaneous/sphere_cylinder/

class Sphere(Actor):

    def __init__(self, name, radius = 10, iterations = 0):
        """ A Sphere actor
        """
        super(Sphere, self).__init__( name )

        self.vertices, self.faces = makeNSphere( iterations )
        self.vertices *= radius

        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.faces.ctypes.data
        self.faces_nr = self.faces.size

    def draw(self):
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(1.0)
        glColor3f(1.0, 1.0, 0.0)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glDrawElements( GL_TRIANGLES, self.faces_nr, GL_UNSIGNED_INT, self.faces_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)
        

def makeNSphere( iterations = 3 ):
    """ Sphere generation subdivision starting from octahedron

    Notes
    -----
    According to http://paulbourke.net/miscellaneous/sphere_cylinder/
    """

    p = [ [0,0,1], [0,0,-1],[-1,-1,0], [1,-1,0], [1,1,0], [-1,1,0]]
    nt = 0

    a = 1 / np.sqrt(2.0)
    for i in range(len(p)):
        p[i][0] *= a
        p[i][1] *= a

    f =  [ [0,3,4],[0,4,5],[0,5,2],[0,2,3],[1,4,3],[1,5,4],[1,2,5],[1,3,2] ]
    nt = 8

    if iterations < 1:
        return np.array(p, dtype = np.float32 ), np.array(f, dtype = np.uint32 )

    # Bisect each edge and move to the surface of a unit sphere
    for it in range(iterations):
        ntold = nt
        for i in range(ntold):
            pa = [
                (p[f[i][0]][0] + p[f[i][1]][0]) / 2.,
                (p[f[i][0]][1] + p[f[i][1]][1]) / 2.,
                (p[f[i][0]][2] + p[f[i][1]][2]) / 2.
            ]
            pb = [
                (p[f[i][1]][0] + p[f[i][2]][0]) / 2.,
                (p[f[i][1]][1] + p[f[i][2]][1]) / 2.,
                (p[f[i][1]][2] + p[f[i][2]][2]) / 2.
            ]
            pc = [
                (p[f[i][2]][0] + p[f[i][0]][0]) / 2.,
                (p[f[i][2]][1] + p[f[i][0]][1]) / 2.,
                (p[f[i][2]][2] + p[f[i][0]][2]) / 2.
            ]
            # normalize new points, i.e. project them to the sphere
            pa = list( np.array(pa) / np.linalg.norm( np.array(pa) ) )
            p.append( pa )
            pai = len(p) - 1

            pb = list( np.array(pb) / np.linalg.norm( np.array(pb) ) )
            p.append( pb )
            pbi = len(p) - 1

            pc = list( np.array(pc) / np.linalg.norm( np.array(pc) ) )
            p.append( pc )
            pci = len(p) - 1

            # add new faces
            f.append( [ f[i][0], pai, pci ] )
            nt += 1
            f.append( [ pai, f[i][1], pbi ] )
            nt += 1
            f.append( [ pbi, f[i][2], pci ] )
            nt += 1
            f[i][0] = pai
            f[i][1] = pbi
            f[i][2] = pci

    return np.array(p, dtype = np.float32 ), np.array(f, dtype = np.uint32 )


def makeCylinder( p1, p2, r1, r2, resolution = 4 ):

    if r1 == 0.0 and r2 == 0.0:
        print("Not both radii can be zero!")
        return None

    # Normal pointing from p1 to p2
    n = (p1 - p2).astype( np.float32 )

    if n[0] != 0.0 or n[1] != 0.0:
        A = np.array( [n[1], -n[0], 0.0], dtype = np.float32 )
    elif n[1] != 0.0 or n[2] != 0.0:
        A = np.array( [0.0, n[2], -n[1]], dtype = np.float32 )
    elif n[0] != 0.0 or n[2] != 0.0:
        A = np.array( [n[0], 0.0, -n[1]], dtype = np.float32 )
    else:
        print("Cylinder coordinates well-posed. Cannot create perpendicular vector.")

    B = np.cross( n, A )

    # Normalize
    A = A / np.linalg.norm( A )
    B = B / np.linalg.norm( B )

    n = 0
    TWOPI =  2 * np.pi  
    p = []
    f = []
    for i in range(resolution):
        theta1 = i * TWOPI / (resolution)
        sint1 = np.sin(theta1)
        cost1 = np.cos(theta1)
        theta2 = (i+1) * TWOPI / (resolution)
        sint2 = np.sin(theta2)
        cost2 = np.cos(theta2)

        face = []
        # first point, q0
        p.append( [
            p1[0] + r1 * cost1 * A[0] + r1 * sint1 * B[0],
            p1[1] + r1 * cost1 * A[1] + r1 * sint1 * B[1],
            p1[2] + r1 * cost1 * A[2] + r1 * sint1 * B[2]
        ])
        face.append( n )
        n += 1

        # second point, q1
        p.append( [
            p2[0] + r2 * cost1 * A[0] + r2 * sint1 * B[0],
            p2[1] + r2 * cost1 * A[1] + r2 * sint1 * B[1],
            p2[2] + r2 * cost1 * A[2] + r2 * sint1 * B[2]
        ])
        face.append( n )
        n += 1

        if r2 != 0.0:
            p.append( [
                p2[0] + r2 * cost2 * A[0] + r2 * sint2 * B[0],
                p2[1] + r2 * cost2 * A[1] + r2 * sint2 * B[1],
                p2[2] + r2 * cost2 * A[2] + r2 * sint2 * B[2]
            ])
            face.append( n )
            n += 1

        if r1 != 0.0:
            p.append( [
                p1[0] + r1 * cost2 * A[0] + r1 * sint2 * B[0],
                p1[1] + r1 * cost2 * A[1] + r1 * sint2 * B[1],
                p1[2] + r1 * cost2 * A[2] + r1 * sint2 * B[2]
            ])
            face.append( n )
            n += 1

        # Create triangles
        if len(face) == 4:
            f.append( [face[0], face[1], face[2]] )
            f.append( [face[0], face[2], face[3]] )
        elif len(face) == 3:
            f.append( face )
        else:
            print("Wrong number of vertices in face.")

    return np.array( p, dtype = np.float32 ), np.array( f, dtype = np.uint32 )

    
if __name__ == '__main__':

    #print makeNSphere( 2 )
    print makeCylinder( np.array([0,0,0]), np.array([0,1,0]), 1, 1)