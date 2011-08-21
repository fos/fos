import numpy as np
from pyglet.gl import *
from .base import Actor

class Sphere(Actor):

    def __init__(self, name, radius = 10, iterations = 0, color = (0.0, 1.0, 0.0, 1.0), wireframe = False):
        """ A Sphere actor
        """
        super(Sphere, self).__init__( name )

        self.vertices, self.faces = makeNSphere( iterations )
        self.vertices *= radius
        self.wireframe = wireframe
        self.color = color

        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.faces.ctypes.data
        self.faces_nr = self.faces.size

    def draw(self):
        glDisable(GL_CULL_FACE)
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)
        glColor4f( self.color[0], self.color[1], self.color[2], self.color[3] )
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glDrawElements( GL_TRIANGLES, self.faces_nr, GL_UNSIGNED_INT, self.faces_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)

class Cylinder(Actor):

    def __init__(self, name, p1, p2, r1, r2, resolution = 4, color = (0.0, 1.0, 0.0, 1.0), wireframe = False):
        """ A Cylinder actor. Creates cones if radius set to zero
        """
        super(Cylinder, self).__init__( name )

        self.vertices, self.faces = makeCylinder( p1, p2, r1, r2, resolution )

        self.wireframe = wireframe
        self.color = color

        self.vertices_ptr = self.vertices.ctypes.data
        self.faces_ptr = self.faces.ctypes.data
        self.faces_nr = self.faces.size

    def draw(self):
        glDisable(GL_CULL_FACE)
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)
        glColor4f( self.color[0], self.color[1], self.color[2], self.color[3] )
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glDrawElements( GL_TRIANGLES, self.faces_nr, GL_UNSIGNED_INT, self.faces_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)

class Box(Actor):

    def __init__(self, name, blf = None, trb = None, margin = 0, color = (1.0, 1.0, 1.0, 1.0)):
        """ Box from bottom-left-front and top-right-back point coordinates
        (Axis Aligned Bounding)
        """
        super(Box, self).__init__( name )

        self.vertices = np.zeros( (8,3), dtype = np.float32 )
        self.c1 = np.zeros( (3,1), dtype = np.float32 )
        self.c2 = np.zeros( (3,1), dtype = np.float32 )
        self.indices = np.array([ [0,1,5,4],
                           [2,3,7,6],
                           [2,0,1,3],
                           [3,7,5,1],
                           [7,6,4,5],
                           [6,2,0,4] ], dtype = np.uint32)
        self.color = color

        self.update(blf, trb, margin)

        self.vertices_ptr = self.vertices.ctypes.data
        self.indices_ptr = self.indices.ctypes.data
        self.indices_nr = self.indices.size

    def update(self, c1, c2, margin):
        """ c1 is botton-left-front, and c2 is top-right-back point
        """
        # add the margin on all sides
        self.c1[0] = c1[0] - margin
        self.c1[1] = c1[1] - margin
        self.c1[2] = c1[2] - margin

        self.c2[0] = c2[0] + margin
        self.c2[1] = c2[1] + margin
        self.c2[2] = c2[2] + margin

        self.vertices[:4, 0] = self.c1[0]
        self.vertices[4:, 0] = self.c2[0]
        self.vertices[:2, 1] = self.vertices[4:6, 1] = self.c1[1]
        self.vertices[2:4, 1] = self.vertices[6:8, 1] = self.c2[1]
        self.vertices[::2, 2] = self.c2[2]
        self.vertices[1::2, 2] = self.c1[2]

    def draw(self):
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(1.0)
        glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glDrawElements( GL_QUADS, self.indices_nr, GL_UNSIGNED_INT, self.indices_ptr )
        glDisableClientState(GL_VERTEX_ARRAY)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_CULL_FACE)


def makeCube():
    """ Create a Cube

    Credits: https://github.com/danginsburg/webgl-brain-viewer/blob/master/common/esShapes.js
    """
    vertices = np.array( [
      [-0.5, -0.5, -0.5],[-0.5, -0.5,  0.5],[0.5, -0.5,  0.5],[0.5, -0.5, -0.5],
      [-0.5,  0.5, -0.5],[-0.5,  0.5,  0.5],[0.5,  0.5,  0.5],[0.5,  0.5, -0.5],
      [-0.5, -0.5, -0.5],[-0.5,  0.5, -0.5],[0.5,  0.5, -0.5],[0.5, -0.5, -0.5],
      [-0.5, -0.5, 0.5],[-0.5,  0.5, 0.5],[0.5,  0.5, 0.5],[0.5, -0.5, 0.5],
      [-0.5, -0.5, -0.5],[-0.5, -0.5,  0.5],[-0.5,  0.5,  0.5],[-0.5,  0.5, -0.5],
      [0.5, -0.5, -0.5],[0.5, -0.5,  0.5],[0.5,  0.5,  0.5],[0.5,  0.5, -0.5]], dtype = np.float32 )

    normals = np.array( [
      [0.0, -1.0, 0.0],[0.0, -1.0, 0.0],[0.0, -1.0, 0.0],[0.0, -1.0, 0.0],
      [0.0, 1.0, 0.0],[0.0, 1.0, 0.0],[0.0, 1.0, 0.0],[0.0, 1.0, 0.0],
      [0.0, 0.0, -1.0],[0.0, 0.0, -1.0],[0.0, 0.0, -1.0],[0.0, 0.0, -1.0],
      [0.0, 0.0, 1.0],[0.0, 0.0, 1.0],[0.0, 0.0, 1.0],[0.0, 0.0, 1.0],
      [-1.0, 0.0, 0.0],[-1.0, 0.0, 0.0],[-1.0, 0.0, 0.0],[-1.0, 0.0, 0.0],
      [1.0, 0.0, 0.0],[1.0, 0.0, 0.0],[1.0, 0.0, 0.0],[1.0, 0.0, 0.0] ], dtype = np.float32 )

    texcoords = np.array( [
      [0.0, 0.0],[0.0, 1.0],[1.0, 1.0],[1.0, 0.0],[1.0, 0.0],[1.0, 1.0],[0.0, 1.0],[0.0, 0.0],
      [0.0, 0.0],[0.0, 1.0],[1.0, 1.0],[1.0, 0.0],[0.0, 0.0],[0.0, 1.0],[1.0, 1.0],[1.0, 0.0],
      [0.0, 0.0],[0.0, 1.0],[1.0, 1.0],[1.0, 0.0],[0.0, 0.0],[0.0, 1.0],[1.0, 1.0],[1.0, 0.0]], dtype = np.float32 )
   
    indices = np.array( [
        [0, 2, 1],[0, 3, 2],[4, 5, 6],[4, 6, 7],[8, 9, 10],[8, 10, 11],
        [12, 15, 14],[12, 14, 13],[16, 17, 18],[16, 18, 19],[20, 23, 22],[20, 22, 21]], dtype = np.uint32 )

    return vertices, indices

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
    """ Cylinder or Cone generation

    Notes
    -----
    http://paulbourke.net/miscellaneous/sphere_cylinder/
    """
    # TODO: implement capping

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

def make_cube_scatter( x, y, z, values, colormap = None, scale_by_value = False):
    n = len(x)
    vertices = []
    faces = []
    colors = []
    # use values to create colormap array
    colormap_array = colormap( values )
    face_offset = 0
    for i in range(n):

        vert, fac = makeCube( )

        if scale_by_value:
            vert *= values[i]

        # translate
        vert[:,0] += x[i]
        vert[:,1] += y[i]
        vert[:,2] += z[i]

        if not colormap is None:
            colors.append( np.repeat( colormap_array[i,:].reshape( (1,4) ), len(vert), axis = 0) )

        vertices.append( vert )
        fac += face_offset
        faces.append( fac )
        face_offset += len(vert)

    vertices = np.concatenate( vertices ).astype( np.float32 )
    faces = np.concatenate( faces ).astype( np.uint32 )
    if len(colors)>0:
        colors = np.concatenate( colors ).astype( np.float32 )
    else:
        colors = None

    return vertices, faces, colors

def make_cylinder_scatter( p1, p2, r1, r2, values = None, resolution = 4, colormap = None):
    n = len(p1)
    vertices = []
    faces = []
    colors = []
    face_offset = 0
    # columns: index, range from vertices array, range to vertices array
    index_range = np.zeros( (n,3), dtype = np.uint32 )
    for i in range(n):
        vert, fac = makeCylinder( p1[i,:], p2[i,:], r1[i], r2[i], resolution )
        index_range[i,0] = i

        if isinstance(colormap, dict):
            colors.append( np.repeat( colormap[values[i]], len(vert), axis = 0).astype( np.float32 ) )

        vertices.append( vert )
        fac += face_offset
        faces.append( fac )

        index_range[i,1] = face_offset
        face_offset += len(vert)
        index_range[i,2] = face_offset
        
    vertices = np.concatenate( vertices ).astype( np.float32 )
    faces = np.concatenate( faces ).astype( np.uint32 )
    if len(colors)>0:
        colors = np.concatenate( colors ).astype( np.float32 )
    else:
        colors = None

    return vertices, faces, colors, index_range

def make_sphere_scatter( x, y, z, values, iterations = 3, colormap = None, scale_by_value = False):
    n = len(x)
    vertices = []
    faces = []
    colors = []
    # use values to create colormap array
    colormap_array = colormap( values )
    face_offset = 0
    for i in range(n):
        
        vert, fac = makeNSphere( iterations )

        if scale_by_value:
            vert *= values[i]

        # translate
        vert[:,0] += x[i]
        vert[:,1] += y[i]
        vert[:,2] += z[i]

        if not colormap is None:
            colors.append( np.repeat( colormap_array[i,:].reshape( (1,4) ), len(vert), axis = 0) )

        vertices.append( vert )
        fac += face_offset
        faces.append( fac )
        face_offset += len(vert)

    vertices = np.concatenate( vertices ).astype( np.float32 )
    faces = np.concatenate( faces ).astype( np.uint32 )
    if len(colors)>0:
        colors = np.concatenate( colors ).astype( np.float32 )
    else:
        colors = None
        
    return vertices, faces, colors