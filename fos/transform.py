import numpy as np

# http://download.oracle.com/docs/cd/E17802_01/j2se/javase/technologies/desktop/java3d/forDevelopers/J3D_1_3_API/j3dapi/javax/media/j3d/Transform3D.html

class Transform3D(object):
    """ A 3D transformation with rotation, scale, shear and translation
    Can return different types of objects with the transformation.
    Uses underlying NumPy array
    """
    def __init__(self):
        pass


class IdentityTranform(Transform3D):

    def __init__(self):
        super(IdentityTranform, self).__init__()
        self.matrix = np.eye(4)


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