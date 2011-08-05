import numpy as np

# http://download.oracle.com/docs/cd/E17802_01/j2se/javase/technologies/desktop/java3d/forDevelopers/J3D_1_3_API/j3dapi/javax/media/j3d/Transform3D.html

class Transform3D(object):
    """ A 3D transformation with rotation, scale, shear and translation
    Can return different types of objects with the transformation.
    Uses underlying NumPy array
    """
    def __init__(self, matrix ):
        self.matrix = matrix

    def set_translation(self, x=None, y=None, z=None ):
        """ Set the translation in the three dimensions
        """
        if x:
            self.matrix[0,3] = x
        if y:
            self.matrix[1,3] = y
        if z:
            self.matrix[2,3] = z

    def set_scale(self, x=None, y=None, z=None ):
        """ Set the scale in the three dimensions
        """
        # TODO: is this correct?
        if x:
            self.matrix[0,0] = x
        if y:
            self.matrix[1,1] = y
        if z:
            self.matrix[2,2] = z

    def rotate(self, angle, x, y, z ):
        """ Rotate around a given axes
        """
        mat = np.zeros( (4,4), dtype = np.float32)

        radAngle = np.deg2rad(angle)
        co = np.cos(radAngle)
        si = np.sin(radAngle)
        x2 = x*x
        y2 = y*y
        z2 = z*z

        mat[0,0] = x2 + (y2 + z2) * co
        mat[0,1] = x * y * (1 - co) - z * si
        mat[0,2] = x * z * (1 - co) + y * si
        mat[0,3]= 0.0

        mat[1,0] = x * y * (1 - co) + z * si
        mat[1,1] = y2 + (x2 + z2) * co
        mat[1,2] = y * z * (1 - co) - x * si
        mat[1,3]= 0.0

        mat[2,0] = x * z * (1 - co) - y * si
        mat[2,1] = y * z * (1 - co) + x * si
        mat[2,2]= z2 + (x2 + y2) * co
        mat[2,3]= 0.0

        mat[3,0] = 0.0
        mat[3,1] = 0.0
        mat[3,2]= 0.0
        mat[3,3]= 1.0

        self.matrix = np.dot( self.matrix, mat)


    def get_transform_numpy(self):
        return self.matrix

    def get_transform_gl(self):
        from ctypes import c_float
        return (c_float*16)(*self.modelview.T.ravel().tolist())

class IdentityTranform(Transform3D):

    def __init__(self):
        super(IdentityTranform, self).__init__( matrix = np.eye(4) )


def general_rotation(x, y, z, a, b, c, u, v, w, angle):
    """ Rotation about an arbitrary line
    x,y,z : point to rotate
    a,b,c : line through point
    u,v,w : direction vector of the line (normalized)
    angle : rotation angle in radians when looked down
            the rotation axis counter-clockwise
    """
    from math import cos, sin
    # assume the direction vector is normalized
    u2 = u*u
    v2 = v*v
    w2 = w*w
    cosa = cos(angle)
    cosam = 1 - cosa
    sina = sin(angle)
    h = -u*x-v*y-w*z
    x1 = (a*(v2+w2)-u*(b*v+c*w+h))*cosam+x*cosa+(-c*v+b*w-w*y+v*z)*sina
    y1 = (b*(u2+w2)-v*(a*u+c*w+h))*cosam+y*cosa+( c*u-a*w+w*x-u*z)*sina
    z1 = (c*(u2+v2)-w*(a*u+b*v+h))*cosam+z*cosa+(-b*u+a*v-v*x+u*y)*sina
    return np.array( [x1, y1, z1], dtype = np.float32)